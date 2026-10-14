"""Real integration is opt-in; ordinary verification never consumes Snowflake credits."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from census_catalog.catalog import Catalog
from scripts.snowflake_probe import execute, load_config, safe_error, suspend

ROOT = Path(__file__).resolve().parents[1]
LIVE_OUTCOMES = {}


def pytest_addoption(parser):
    parser.addoption(
        "--snowflake-live", action="store_true", help="Run bounded real Snowflake tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "snowflake_live: actual remote SQL, opt-in; no mocks")


def pytest_runtest_logreport(report):
    if "test_phase1_live.py" in report.nodeid and report.when == "call":
        LIVE_OUTCOMES[report.nodeid] = report.outcome


@pytest.fixture(scope="session")
def catalog():
    return Catalog.load(ROOT / "data/semantic_catalog.json")


@pytest.fixture(scope="session")
def live_session(request):
    if not request.config.getoption("--snowflake-live"):
        pytest.skip("Real Snowflake tests disabled; pass --snowflake-live (not a PASS)")
    import snowflake.connector

    config = load_config(ROOT / ".env")
    evidence = {"started_at_utc": datetime.now(timezone.utc).isoformat(), "queries": []}
    connection = None
    try:
        try:
            connection = snowflake.connector.connect(
                account=config["SNOWFLAKE_ACCOUNT"],
                user=config["SNOWFLAKE_USER"],
                password=config["SNOWFLAKE_PASSWORD"],
                warehouse=config["SNOWFLAKE_WAREHOUSE"],
                database=config["SNOWFLAKE_DATABASE"],
                schema=config["SNOWFLAKE_SCHEMA"],
                login_timeout=30,
                network_timeout=60,
                socket_timeout=30,
                client_session_keep_alive=False,
                session_parameters={
                    "STATEMENT_TIMEOUT_IN_SECONDS": 60,
                    "QUERY_TAG": "phase1_targeted_tests",
                },
            )
        except Exception as exc:
            evidence["connection_error"] = safe_error(exc, config["SNOWFLAKE_PASSWORD"])
            pytest.fail("Connection failed; see redacted Phase 1 evidence", pytrace=False)

        def run(sql, params=None):
            try:
                result = execute(connection, sql, params)
            except Exception as exc:
                evidence["query_error"] = safe_error(exc, config["SNOWFLAKE_PASSWORD"])
                pytest.fail("Remote query failed; see redacted Phase 1 evidence", pytrace=False)
            evidence["queries"].append({"sql": sql, "parameters": params, **result})
            return result

        yield run
    finally:
        if connection is not None:
            evidence["cleanup"] = suspend(
                connection, config["SNOWFLAKE_WAREHOUSE"], config["SNOWFLAKE_PASSWORD"]
            )
            connection.close()
        evidence["test_outcomes"] = dict(LIVE_OUTCOMES)
        evidence["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        (ROOT / "docs/phase1_integration_results.json").write_text(
            json.dumps(evidence, indent=2, default=str) + "\n"
        )
        if connection is not None and not evidence["cleanup"]["confirmed_suspended"]:
            pytest.fail("Warehouse suspension not confirmed; see Phase 1 evidence", pytrace=False)
