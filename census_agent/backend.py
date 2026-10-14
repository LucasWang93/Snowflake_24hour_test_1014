"""Bounded Cortex/SQL transport reusing the established local connection loader."""

from __future__ import annotations

import json
import re
import time
from typing import Any

from census_agent.sql import ValidatedQuery, validate_query
from census_agent.types import Deadline, ServiceIssue
from census_catalog.catalog import Catalog
from scripts.snowflake_probe import ROOT, load_config, quote_identifier, safe_error


class SnowflakeBackend:
    def __init__(self, catalog: Catalog, model: str = "llama3.3-70b"):
        if model not in {"llama3.3-70b", "llama3.1-70b", "mistral-7b"}:
            raise ValueError("Choose a previously verified Cortex model")
        self.catalog, self.model = catalog, model
        self._connection = None
        self._ready = False
        self._config = None
        self.audit: dict[str, Any] = {}
        self.model_calls: list[dict[str, Any]] = []

    def connect(self, deadline: Deadline) -> None:
        if self._ready and self._connection is not None and not self._connection.is_closed():
            return
        if self._connection is not None and not self._connection.is_closed():
            self._connection.close()
        self._ready = False
        import snowflake.connector

        self._config = load_config(ROOT / ".env")
        c = self._config
        try:
            self._connection = snowflake.connector.connect(
                account=c["SNOWFLAKE_ACCOUNT"],
                user=c["SNOWFLAKE_USER"],
                password=c["SNOWFLAKE_PASSWORD"],
                warehouse=c["SNOWFLAKE_WAREHOUSE"],
                database=c["SNOWFLAKE_DATABASE"],
                schema=c["SNOWFLAKE_SCHEMA"],
                role="PUBLIC",
                login_timeout=deadline.timeout(10),
                network_timeout=10,
                socket_timeout=10,
                client_session_keep_alive=False,
                session_parameters={
                    "STATEMENT_TIMEOUT_IN_SECONDS": 20,
                    "STATEMENT_QUEUED_TIMEOUT_IN_SECONDS": 3,
                    "QUERY_TAG": "phase2_conversational_agent",
                },
            )
            self._run("USE SECONDARY ROLES ALL", None, deadline.timeout(5), 1)
            self.audit["context"] = self._run(
                "SELECT CURRENT_ROLE(), CURRENT_SECONDARY_ROLES(), CURRENT_USER()",
                None,
                deadline.timeout(5),
                1,
            )
            self.audit["primary_role_grants"] = self._run(
                'SHOW GRANTS TO ROLE "PUBLIC"',
                None,
                deadline.timeout(5),
                1000,
            )
            self.audit["user_role_grants"] = self._run(
                f"SHOW GRANTS TO USER {quote_identifier(c['SNOWFLAKE_USER'])}",
                None,
                deadline.timeout(5),
                1000,
            )
            self._ready = True
        except Exception as exc:
            raise self._failure("Snowflake connection/permissions", exc) from exc

    def begin_request(self) -> None:
        self.model_calls.clear()  # Each Response retains its diagnostics; no unbounded model history.

    def _failure(self, stage: str, exc: Exception) -> ServiceIssue:
        password = self._config["SNOWFLAKE_PASSWORD"] if self._config else ""
        return ServiceIssue(stage, safe_error(exc, password))

    def _run(
        self, sql: str, params: tuple[Any, ...] | None, timeout: int, max_rows: int
    ) -> dict[str, Any]:
        started = time.monotonic()
        with self._connection.cursor() as cursor:
            cursor.execute(sql, params, timeout=timeout)
            rows = cursor.fetchmany(max_rows + 1)
            if len(rows) > max_rows:
                raise ServiceIssue("result bound", {"query_id": cursor.sfqid})
            return {
                "columns": [c[0] for c in cursor.description or ()],
                "rows": rows,
                "query_id": cursor.sfqid,
                "elapsed_seconds": round(time.monotonic() - started, 4),
            }

    def complete(self, system: str, payload: dict[str, Any], deadline: Deadline) -> dict[str, Any]:
        self.connect(deadline)
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]
        try:
            result = self._run(
                "SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, PARSE_JSON(%s), PARSE_JSON(%s))",
                (
                    self.model,
                    json.dumps(messages),
                    json.dumps({"temperature": 0, "max_tokens": 450, "guardrails": True}),
                ),
                deadline.timeout(20),
                1,
            )
            wrapper = json.loads(result["rows"][0][0])
            message = wrapper["choices"][0]["messages"]
            if not isinstance(message, str) or len(message) > 10000:
                raise ValueError("Invalid model response size")
            message = re.sub(r"^```(?:json)?\s*|\s*```$", "", message.strip())
            parsed = json.loads(message)
            if not isinstance(parsed, dict):
                raise ValueError("Expected a JSON object")
            self.model_calls.append(
                {
                    "model": self.model,
                    "query_id": result["query_id"],
                    "elapsed_seconds": result["elapsed_seconds"],
                    "usage": wrapper.get("usage"),
                    "structured_output": parsed,
                }
            )
            return parsed
        except Exception as exc:
            raise self._failure("Cortex interpretation", exc) from exc

    def execute_data(self, statement: ValidatedQuery, deadline: Deadline) -> dict[str, Any]:
        statement = validate_query(
            self.catalog, statement
        )  # Always before cursor/network execution.
        self.connect(deadline)
        try:
            return self._run(
                statement.sql, statement.params, deadline.timeout(15), statement.row_limit
            )
        except Exception as exc:
            raise self._failure("Snowflake data query", exc) from exc

    def suspend(self) -> dict[str, Any] | None:
        if self._connection is None or self._connection.is_closed():
            return None
        output: dict[str, Any] = {}
        try:
            output["alter"] = self._run(
                f"ALTER WAREHOUSE {quote_identifier(self._config['SNOWFLAKE_WAREHOUSE'])} SUSPEND",
                None,
                3,
                1,
            )
        except Exception as exc:
            output["alter_error"] = safe_error(exc, self._config["SNOWFLAKE_PASSWORD"])
        try:
            check_budget = Deadline(budget=3)
            output["state_checks"] = []
            for attempt in range(3):
                show = self._run("SHOW WAREHOUSES", None, check_budget.timeout(2), 100)
                rows = [
                    dict(zip((c.lower() for c in show["columns"]), row)) for row in show["rows"]
                ]
                wh = next(
                    (r for r in rows if r["name"] == self._config["SNOWFLAKE_WAREHOUSE"]), None
                )
                observed = wh["state"] if wh else None
                output["state_checks"].append({"query_id": show["query_id"], "state": observed})
                output.update(
                    query_id=show["query_id"], confirmed_suspended=observed == "SUSPENDED"
                )
                if observed == "SUSPENDED":
                    break
                if attempt < 2:
                    time.sleep(
                        0.25
                    )  # Suspension can briefly be transitional; bounded polling only.
        except Exception as exc:
            output.update(
                confirmed_suspended=False, error=safe_error(exc, self._config["SNOWFLAKE_PASSWORD"])
            )
        return output

    def close(self) -> None:
        if self._connection is not None:
            self.suspend()
            self._connection.close()
