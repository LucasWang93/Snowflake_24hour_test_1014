"""Constrained conversational pipeline with result-derived answers and no model SQL."""

from __future__ import annotations

import math
import threading
import time
from dataclasses import asdict
from typing import Any, Callable

from census_agent.planning import (
    INTENT_SYSTEM,
    check_semantics,
    constrain_intent,
    guard_question,
    merge_intent,
    select_field,
)
from census_agent.sql import QueryPlan, compile_query, resolve_scope, validate_query
from census_agent.types import (
    AgentIssue,
    ConversationState,
    Deadline,
    Intent,
    Response,
    ServiceIssue,
)
from census_catalog.catalog import Catalog
from census_catalog.geography import Geography


class CensusAgent:
    def __init__(
        self, catalog: Catalog, backend: Any, progress: Callable[[str], None] | None = None
    ):
        self._request_lock = threading.Lock()
        self.catalog, self.backend = catalog, backend
        self.geography = Geography(catalog.data)
        self.progress = progress or (lambda _: None)

    def ask(
        self,
        question: str,
        state: ConversationState | None = None,
        *,
        deadline: Deadline | None = None,
    ) -> Response:
        state = state if state is not None else ConversationState()
        if not self._request_lock.acquire(blocking=False):
            return Response(
                "overloaded", "This agent is handling another request; retry shortly.", 0
            )
        if not state._lock.acquire(blocking=False):
            self._request_lock.release()
            return Response(
                "overloaded", "This conversation has a request in progress; retry shortly.", 0
            )
        try:
            return self._ask(question, state, deadline)
        except ServiceIssue:
            return Response(
                "error", "Connection ownership prevents this request; use an isolated agent.", 0
            )
        finally:
            state._lock.release()
            self._request_lock.release()

    def _ask(self, question: str, state: ConversationState, deadline: Deadline | None) -> Response:
        started = time.monotonic()
        deadline = deadline or Deadline(
            started, 50.0
        )  # Reserve time for bounded warehouse cleanup.
        response = Response("error", "Unable to complete this request.", 0.0)
        if hasattr(self.backend, "begin_request"):
            self.backend.begin_request()
        model_start = len(getattr(self.backend, "model_calls", []))
        old_pending = state.pending
        mark = started

        def stage(name: str) -> None:
            nonlocal mark
            now = time.monotonic()
            response.stages[name] = round(now - mark, 4)
            mark = now
            self.progress(name)

        try:
            deadline.check()
            guard_question(question, state)
            stage("request validation")
            delta = Intent.parse(
                self.backend.complete(
                    INTENT_SYSTEM, {"question": question, "context": state.context()}, deadline
                )
            )
            deadline.check()
            delta = constrain_intent(delta, state, question)
            merged = merge_intent(delta, state, question)
            state.pending = merged
            response.intent = asdict(merged)
            resolved = check_semantics(merged, question)
            response.intent = asdict(resolved)
            stage("context resolution")
            scopes = [resolve_scope(g, resolved.year, self.geography) for g in resolved.geographies]
            if len({(s.type, s.key) for s in scopes}) != len(scopes):
                raise AgentIssue(
                    "The comparison geographies are identical; name two distinct entities."
                )
            mapping = select_field(
                self.catalog,
                self.backend,
                resolved,
                question,
                deadline,
                state.entry_id if delta.metric is None else None,
            )
            response.metric = {
                k: mapping[k]
                for k in (
                    "id",
                    "table",
                    "column",
                    "title",
                    "universe",
                    "field_path",
                    "year",
                    "source_product",
                    "estimate_kind",
                    "aggregation",
                    "survey_interval",
                )
            }
            stage("catalog grounding")
            for scope in scopes:
                operation = "value" if scope.type == "cbg" else "sum"
                if resolved.aggregation == "sum":
                    operation = "sum"
                statement = validate_query(
                    self.catalog,
                    compile_query(self.catalog, QueryPlan(mapping["id"], scope, operation)),
                )
                trace = {
                    "sql": statement.sql,
                    "params": statement.params,
                    "plan": asdict(statement.plan),
                }
                response.sql.append(trace)
                deadline.check()
                raw = self.backend.execute_data(statement, deadline)
                deadline.check()
                trace.update(query_id=raw["query_id"], elapsed_seconds=raw.get("elapsed_seconds"))
                rows = [dict(zip(raw["columns"], row)) for row in raw["rows"]]
                if not rows or rows[0]["ROWS_MATCHED"] == 0:
                    raise AgentIssue(
                        f"No Census rows match {scope.label} in this release; I cannot report a statistic.",
                        "unsupported",
                    )
                if len(rows) != 1 or rows[0]["ROWS_MATCHED"] != rows[0]["UNIQUE_CBGS"]:
                    raise AgentIssue(
                        "Duplicate CBG rows would make this result unsafe; no total is reported.",
                        "unsupported",
                    )
                row = rows[0]
                if (
                    row["INVALID_VALUES"]
                    or row["VALUE"] is None
                    or not math.isfinite(float(row["VALUE"]))
                ):
                    raise AgentIssue(
                        "This field contains missing/suppressed/invalid values in that scope; I cannot safely report it.",
                        "unsupported",
                    )
                response.results.append(
                    {
                        "geography": asdict(scope),
                        "value": float(row["VALUE"]),
                        "cbgs_matched": int(row["ROWS_MATCHED"]),
                        "query_id": raw["query_id"],
                    }
                )
            stage("validated SQL execution")
            deadline.check()
            response.answer = grounded_answer(mapping, response.results)
            response.status = "answered"
            state.resolved, state.pending, state.entry_id = resolved, None, mapping["id"]
            stage("grounded answer")
        except AgentIssue as exc:
            response.status, response.answer = exc.status, str(exc)
            response.results = []  # Never present partial comparisons as complete answers.
        except ServiceIssue as exc:
            response.status, response.answer = "error", str(exc)
            response.error = {"stage": exc.stage, **exc.detail}
            response.results = []
            state.pending = old_pending
        except Exception:
            # Do not expose exception bodies, credentials, raw model output or a traceback.
            response.status = "error"
            response.answer = "I could not safely complete that request. Please specify the metric, release and geography or try again."
            response.results = []
            state.pending = old_pending
        finally:
            response.model_calls = list(getattr(self.backend, "model_calls", []))[model_start:]
            try:
                response.cleanup = self.backend.suspend()
                if response.cleanup and not response.cleanup.get("confirmed_suspended"):
                    response.answer += (
                        " Warehouse cleanup could not be confirmed; operator attention is needed."
                    )
            except Exception:
                response.cleanup = {"confirmed_suspended": False}
                response.answer += (
                    " Warehouse cleanup could not be confirmed; operator attention is needed."
                )
            response.latency_seconds = round(time.monotonic() - started, 4)
        return response


def grounded_answer(mapping: dict[str, Any], results: list[dict[str, Any]]) -> str:
    parts = [f"{r['geography']['label']}: {r['value']:,.15g}" for r in results]
    text = "; ".join(parts) + "."
    if len(results) == 2:
        text += (
            f" Difference (second minus first): {results[1]['value'] - results[0]['value']:,.15g}."
        )
    path = " / ".join(mapping["field_path"])
    text += f" Metric: {mapping['title']} — {path}; universe: {mapping['universe']}."
    text += f" Year/release: {mapping['year']}; statistical source: {mapping['source_product']}; field: {mapping['column']} ({mapping['estimate_kind']})."
    if mapping["source_product"].startswith("acs_"):
        text += " ACS prefix year is a provider release label; the survey interval is unverified. These are estimates, not decennial counts."
    if any(r["geography"]["type"] != "cbg" for r in results):
        text += " Total covers the matching CBGs present in this source; full geographic coverage is not independently established. No aggregate MOE was calculated."
    if mapping["estimate_kind"] == "moe":
        text += " This is the published CBG margin of error, not an estimate or an aggregated MOE."
    elif mapping["aggregation"]["measure"] != "additive_count":
        text += (
            " This is a published CBG statistic; it has not been summed or averaged across CBGs."
        )
    if len(results) == 2:
        text += " The descriptive difference is not a statistical-significance test."
    return text
