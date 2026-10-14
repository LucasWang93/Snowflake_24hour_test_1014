"""Bounded Cortex/SQL transport reusing the established local connection loader."""

from __future__ import annotations

import json
import os
import re
import stat
import threading
import time
from pathlib import Path
from typing import Any

from census_agent.sql import ValidatedQuery, validate_query
from census_agent.types import Deadline, ServiceIssue
from census_catalog.catalog import Catalog
from scripts.snowflake_probe import ROOT, load_config, quote_identifier, safe_error


class SnowflakeBackend:
    def __init__(
        self,
        catalog: Catalog,
        model: str = "llama3.3-70b",
        *,
        role: str = "PUBLIC",
        secondary_roles: str = "ALL",
        query_tag: str = "census_agent_bounded_request",
        connection_config: dict[str, str] | None = None,
    ):
        if model not in {"llama3.3-70b", "llama3.1-70b", "mistral-7b"}:
            raise ValueError("Choose a previously verified Cortex model")
        if not re.fullmatch(r"[A-Z][A-Z0-9_]{0,254}", role) or secondary_roles not in {
            "ALL",
            "NONE",
        }:
            raise ValueError("Invalid trusted role configuration")
        if not re.fullmatch(r"[A-Za-z0-9_]{1,80}", query_tag):
            raise ValueError("Invalid trusted query tag")
        self.query_tag = query_tag
        # Public deployment injects a dedicated key-pair configuration. The existing
        # operator CLI retains its explicitly authorized local .env loader.
        self._connection_config = dict(connection_config) if connection_config is not None else None
        self.role, self.secondary_roles = role, secondary_roles
        self._owner_thread = None
        self._owner_guard = threading.Lock()
        self.catalog, self.model = catalog, model
        self._connection = None
        self._ready = False
        self._config = None
        self.audit: dict[str, Any] = {}
        self.model_calls: list[dict[str, Any]] = []

    def _assert_owner(self) -> None:
        current = (os.getpid(), threading.get_ident())
        with self._owner_guard:
            if self._owner_thread is None:
                self._owner_thread = current
            elif self._owner_thread != current:
                raise ServiceIssue("connection ownership")

    def connect(self, deadline: Deadline) -> None:
        self._assert_owner()
        deadline.check()
        if self._ready and self._connection is not None and not self._connection.is_closed():
            return
        if self._connection is not None and not self._connection.is_closed():
            self._connection.close()
        self._ready = False
        import snowflake.connector

        self._config = (
            dict(self._connection_config)
            if self._connection_config is not None
            else load_config(ROOT / ".env")
        )
        c = self._config
        try:
            if c.get("SNOWFLAKE_PRIVATE_KEY_FILE"):
                key = Path(c["SNOWFLAKE_PRIVATE_KEY_FILE"])
                if (
                    not key.is_absolute()
                    or key.is_symlink()
                    or not key.is_file()
                    or stat.S_IMODE(key.stat().st_mode) & 0o077
                ):
                    raise ValueError("Private key must be an owner-only regular file")
                credentials = {"authenticator": "SNOWFLAKE_JWT", "private_key_file": str(key)}
                if c.get("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"):
                    credentials["private_key_file_pwd"] = c["SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"]
            else:
                credentials = {"password": c["SNOWFLAKE_PASSWORD"]}
            self._connection = snowflake.connector.connect(
                account=c["SNOWFLAKE_ACCOUNT"],
                user=c["SNOWFLAKE_USER"],
                **credentials,
                warehouse=c["SNOWFLAKE_WAREHOUSE"],
                database=c["SNOWFLAKE_DATABASE"],
                schema=c["SNOWFLAKE_SCHEMA"],
                role=self.role,
                login_timeout=deadline.timeout(10),
                network_timeout=10,
                socket_timeout=10,
                client_session_keep_alive=False,
                session_parameters={
                    "STATEMENT_TIMEOUT_IN_SECONDS": 20,
                    "STATEMENT_QUEUED_TIMEOUT_IN_SECONDS": 3,
                    "QUERY_TAG": self.query_tag,
                },
            )
            self._run(f"USE SECONDARY ROLES {self.secondary_roles}", None, deadline.timeout(5), 1)
            self.audit["context"] = self._run(
                "SELECT CURRENT_ROLE(), CURRENT_SECONDARY_ROLES(), CURRENT_USER(), CURRENT_SESSION()",
                None,
                deadline.timeout(5),
                1,
            )
            self.audit["primary_role_grants"] = self._run(
                f"SHOW GRANTS TO ROLE {quote_identifier(self.role)}",
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
            self.audit_visible_inherited_roles(deadline)
            self._ready = True
        except Exception as exc:
            raise self._failure("Snowflake connection/permissions", exc) from exc

    def audit_visible_inherited_roles(self, deadline: Deadline) -> None:
        """Follow at most four visible role grants; not an account-wide completeness claim."""
        pending = [self.audit["primary_role_grants"], self.audit["user_role_grants"]]
        visited = {self.role}
        self.audit["inherited_role_grants"] = {}
        while pending and len(visited) <= 4:
            grants = pending.pop(0)
            columns = [c.lower() for c in grants.get("columns", [])]
            for row in grants.get("rows", []):
                grant = dict(zip(columns, row))
                role = grant.get("name")
                if grant.get("granted_on") != "ROLE" or role in visited:
                    continue
                if len(visited) >= 5:
                    break
                visited.add(role)
                try:
                    result = self._run(
                        f"SHOW GRANTS TO ROLE {quote_identifier(role)}",
                        None,
                        deadline.timeout(2),
                        1000,
                    )
                    self.audit["inherited_role_grants"][role] = result
                    pending.append(result)
                except Exception as exc:
                    self.audit["inherited_role_grants"][role] = {
                        "visibility_error": self._failure("role audit", exc).detail
                    }

    def begin_request(self) -> None:
        self._assert_owner()
        self.model_calls.clear()  # Each Response retains its diagnostics; no unbounded model history.

    def _failure(self, stage: str, exc: Exception) -> ServiceIssue:
        password = self._config.get("SNOWFLAKE_PASSWORD", "") if self._config else ""
        detail = safe_error(exc, password)
        detail.pop("message", None)  # Connector exception text may contain arbitrary credentials.
        return ServiceIssue(stage, detail)

    def _run(
        self, sql: str, params: tuple[Any, ...] | None, timeout: int, max_rows: int
    ) -> dict[str, Any]:
        self._assert_owner()
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
        self._assert_owner()
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
            output["alter_error"] = self._failure("warehouse cleanup", exc).detail
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
                confirmed_suspended=False, error=self._failure("warehouse cleanup", exc).detail
            )
        return output

    def close(self) -> None:
        self._assert_owner()
        if self._connection is not None:
            self.suspend()
            self._connection.close()
