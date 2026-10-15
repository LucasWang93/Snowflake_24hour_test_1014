"""Authenticated deployment boundary: isolated disposable workers, no public UI."""

from __future__ import annotations

import json
import logging
import multiprocessing as mp
import os
import sqlite3
import tempfile
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from census_agent.agent import CensusAgent
from census_agent.backend import SnowflakeBackend
from census_agent.control import Authenticator, ControlIssue, Limits, SQLiteControl
from census_agent.types import AgentIssue, ConversationState, Deadline, Intent, Response
from census_catalog.catalog import Catalog
from scripts.snowflake_probe import ROOT

LOGGER = logging.getLogger("census_agent.operations")


def restore_state(data: dict) -> ConversationState:
    return ConversationState(
        resolved=Intent.parse(data["resolved"]) if data.get("resolved") else None,
        pending=Intent.parse(data["pending"]) if data.get("pending") else None,
        entry_id=data.get("entry_id"),
    )


def write_result(path: str, payload: dict) -> None:
    encoded = json.dumps(payload, default=str).encode()
    if len(encoded) > 2_000_000:
        raise ValueError("Bounded worker result exceeded")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(encoded)


def request_worker(path: str, question: str, state_data: dict, deadline: Deadline, options: dict):
    """Spawned process owns all connection, cursor, model traces and mutable state."""
    backend = None
    try:
        catalog = Catalog.load(
            ROOT / "data/semantic_catalog.json",
            index_path=ROOT / "data/semantic_search_index.jsonl",
        )
        deadline.check()
        options = dict(options)
        budget_context = options.pop("model_budget", None)
        if budget_context is not None:
            control = SQLiteControl(
                Path(budget_context["path"]), Limits(**budget_context["limits"])
            )

            def before_model_call():
                try:
                    control.record_model_submission(budget_context["request"])
                except ControlIssue as exc:
                    raise AgentIssue(str(exc), exc.status) from exc

            options["before_model_call"] = before_model_call
        backend = SnowflakeBackend(catalog, **options)
        state = restore_state(state_data)
        response = CensusAgent(catalog, backend).ask(question, state, deadline=deadline)
        audit = backend.audit
        connected = backend._connection is not None
        backend.close()
        payload = {
            "response": response.as_dict(),
            "state": state.context(),
            "permissions": audit,
            "connected": connected,
            "closed": True,
        }
    except Exception:
        payload = {
            "response": Response(
                "error", "Data service could not safely complete this request; retry later.", 0
            ).as_dict(),
            "state": state_data,
            "permissions": {},
            "connected": backend is not None,
            "closed": False,
        }
    write_result(path, payload)


@dataclass
class ServiceResult:
    public: dict[str, Any]
    diagnostics: dict[str, Any] | None = None  # Trusted operator/evaluator only.


class AgentService:
    def __init__(
        self,
        auth: Authenticator,
        control: SQLiteControl,
        *,
        backend_options: dict | None = None,
        worker: Callable = request_worker,
    ):
        self.auth, self.control = auth, control
        self.options = dict(backend_options or {})
        self._worker = worker

    def create_session(self, token: str) -> str:
        return self.control.create_session(self.auth.verify(token))

    def reset(self, token: str, session: str) -> None:
        self.control.reset(self.auth.verify(token), session)

    def ask(self, token: str, session: str, question: str) -> ServiceResult:
        started = time.monotonic()
        request = uuid.uuid4().hex
        proc = workspace = None
        admitted = False
        healthy = False
        state = None
        result = ServiceResult({})
        response = Response(
            "error", "Data service could not complete this request; retry later.", 0
        )
        try:
            owner = self.auth.verify(token)
            if not isinstance(question, str) or not 1 <= len(question.strip()) <= 2000:
                raise ControlIssue(
                    "clarification", "Please ask a Census question of at most 2000 characters."
                )
            state = self.control.begin(owner, session, request)
            admitted = True
            context = mp.get_context("spawn")
            workspace = tempfile.TemporaryDirectory(prefix="request-", dir=self.control.path.parent)
            result_path = Path(workspace.name) / "result.json"
            budget = self.control.limits.deadline_seconds
            work_deadline = Deadline(started, max(0.05, budget - 8))
            proc = context.Process(
                target=self._worker,
                args=(
                    str(result_path),
                    question,
                    state,
                    work_deadline,
                    {
                        **self.options,
                        "query_tag": "census_request_" + request,
                        "model_budget": {
                            "path": str(self.control.path),
                            "limits": asdict(self.control.limits),
                            "request": request,
                        },
                    },
                ),
            )
            proc.start()
            remaining = max(0, started + budget - time.monotonic())
            proc.join(timeout=remaining)
            if proc.is_alive():
                response = Response(
                    "timeout",
                    "Request deadline reached; no statistic is reported. Operator recovery may be required.",
                    0,
                )
            else:
                if (
                    proc.exitcode != 0
                    or not result_path.is_file()
                    or result_path.stat().st_size > 2_000_000
                ):
                    raise OSError("Worker did not complete safely")
                payload = json.loads(result_path.read_bytes())
                response = Response(**payload["response"])
                if time.monotonic() >= started + budget:
                    response = Response(
                        "timeout", "Request deadline reached; no statistic is reported.", 0
                    )
                else:
                    healthy = bool(
                        payload["closed"]
                        and (
                            not payload["connected"]
                            or (response.cleanup and response.cleanup.get("confirmed_suspended"))
                        )
                    )
                    state = payload["state"]
                    result.diagnostics = payload
        except ControlIssue as exc:
            response = Response(exc.status, str(exc), 0)
        except (sqlite3.Error, EOFError, OSError):
            response = Response(
                "unavailable", "Data service is temporarily unavailable; retry later.", 0
            )
        except Exception:
            response = Response(
                "error", "Data service could not safely complete this request; retry later.", 0
            )
        finally:
            if proc is not None and proc.pid is not None:
                proc.join(timeout=0.1)
                if proc.is_alive():
                    proc.terminate()
                    proc.join(timeout=0.5)
                if proc.is_alive():
                    proc.kill()
                    proc.join(timeout=0.5)
                if proc.is_alive():
                    healthy = False
            if proc is not None and proc.pid is not None and not proc.is_alive():
                proc.close()
            if workspace is not None:
                workspace.cleanup()
            if admitted:
                try:
                    self.control.finish(request, state, healthy=healthy)
                except Exception:
                    response = Response(
                        "unavailable",
                        "Request completion requires operator attention; retry later.",
                        0,
                    )
            response.latency_seconds = round(time.monotonic() - started, 4)
            result.public = {"request_id": request, **response.public_dict()}
            LOGGER.info(
                json.dumps(
                    {
                        "event": "request_complete",
                        "request_id": request,
                        "status": response.status,
                        "elapsed_seconds": response.latency_seconds,
                        "worker_healthy": healthy,
                    }
                )
            )
        return result
