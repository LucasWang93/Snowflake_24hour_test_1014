"""Deterministic real-SQLite metering tests; connector/Cortex are explicitly mocked."""

from contextlib import nullcontext
from unittest.mock import Mock

import pytest

from census_agent.backend import SnowflakeBackend
from census_agent.control import ControlIssue, Limits, SQLiteControl

CORTEX_SQL = "SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, PARSE_JSON(%s), PARSE_JSON(%s))"


def store(tmp_path, limit=2):
    control = SQLiteControl(tmp_path / "control.sqlite", Limits(model_calls_per_day=limit))
    session = control.create_session("owner")
    control.begin("owner", session, "request")
    return control, session


def count(control):
    with control._transaction() as db:
        return db.execute("SELECT COUNT(*) FROM model_submissions").fetchone()[0]


def backend(control):
    obj = SnowflakeBackend(
        None, before_model_call=lambda: control.record_model_submission("request")
    )
    cursor = Mock(description=[], sfqid="mock-query", fetchmany=Mock(return_value=[]))
    obj._connection = Mock(cursor=Mock(return_value=nullcontext(cursor)))
    return obj, cursor


def test_admission_local_refusal_and_legacy_reservations_do_not_count(tmp_path):
    control, _ = store(tmp_path)
    with control._transaction() as db:
        db.execute("UPDATE events SET calls=120")
    control.finish("request", {}, healthy=True)
    assert count(control) == 0
    session = control.create_session("other")
    control.begin("other", session, "next-request")
    control.record_model_submission("next-request")
    assert count(control) == 1


def test_only_cortex_cursor_submissions_count(tmp_path):
    control, _ = store(tmp_path)
    obj, cursor = backend(control)
    obj._run("SELECT 1", None, 1, 1)
    assert count(control) == 0
    obj._run(CORTEX_SQL, ("mock", "[]", "{}"), 1, 1)
    assert count(control) == 1
    cursor.execute.side_effect = RuntimeError("mock remote failure")
    with pytest.raises(RuntimeError):
        obj._run(CORTEX_SQL, ("mock", "[]", "{}"), 1, 1)
    assert count(control) == 2  # Sent attempt remains charged even when provider fails.


def test_cursor_failure_before_submission_is_not_charged(tmp_path):
    control, _ = store(tmp_path)
    obj, _ = backend(control)
    obj._connection.cursor.side_effect = RuntimeError("mock cursor failure")
    with pytest.raises(RuntimeError):
        obj._run(CORTEX_SQL, None, 1, 1)
    assert count(control) == 0


def test_budget_rejection_prevents_execute_and_survives_reopen(tmp_path):
    control, _ = store(tmp_path, limit=1)
    obj, cursor = backend(control)
    obj._run(CORTEX_SQL, None, 1, 1)
    reopened = SQLiteControl(control.path, control.limits)
    obj.before_model_call = lambda: reopened.record_model_submission("request")
    with pytest.raises(ControlIssue) as error:
        obj._run(CORTEX_SQL, None, 1, 1)
    assert error.value.status == "budget_exhausted"
    assert "24-hour" in str(error.value)
    assert cursor.execute.call_count == 1
    assert count(control) == 1


def test_rolling_boundary_expires_without_midnight_reset(tmp_path, monkeypatch):
    now = [1_000_000.0]
    monkeypatch.setattr("census_agent.control.time.time", lambda: now[0])
    control, session = store(tmp_path, limit=1)
    control.record_model_submission("request")
    control.finish("request", {}, healthy=True)
    now[0] += 86400 - 1
    # Refresh session without losing the prior submission.
    session = control.create_session("owner")
    control.begin("owner", session, "second")
    with pytest.raises(ControlIssue) as error:
        control.record_model_submission("second")
    assert error.value.status == "budget_exhausted"
    now[0] += 1
    control.record_model_submission("second")
    assert count(control) == 1


def test_lease_and_per_request_bounds_stay_enforced(tmp_path):
    control, _ = store(tmp_path, limit=1200)
    with pytest.raises(ControlIssue):
        control.record_model_submission("foreign-request")
    control.record_model_submission("request")
    control.record_model_submission("request")
    with pytest.raises(ControlIssue) as error:
        control.record_model_submission("request")
    assert error.value.status == "unavailable"
    assert count(control) == 2


def test_concurrent_submission_debits_cannot_overshoot(tmp_path):
    import threading
    from concurrent.futures import ThreadPoolExecutor

    control, _ = store(tmp_path, limit=1)
    other = SQLiteControl(control.path, control.limits)
    barrier = threading.Barrier(2)

    def submit(instance):
        barrier.wait(timeout=5)
        try:
            instance.record_model_submission("request")
            return "submitted"
        except ControlIssue as error:
            return error.status

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(submit, [control, other]))
    assert sorted(outcomes) == ["budget_exhausted", "submitted"]
    assert count(control) == 1


def test_request_worker_injects_shared_meter_and_preserves_safe_budget_status(
    tmp_path, monkeypatch, catalog
):
    import json
    from dataclasses import asdict

    from census_agent import service
    from census_agent.types import Deadline

    control, _ = store(tmp_path, limit=1)
    control.record_model_submission("request")

    class MockBackend:
        audit = {}
        model_calls = []
        _connection = None

        def __init__(self, catalog, **options):
            self.before = options["before_model_call"]

        def complete(self, *args):
            self.before()
            raise AssertionError("No Cortex call permitted after the cap")

        def suspend(self):
            return None

        def close(self):
            pass

    monkeypatch.setattr(service.Catalog, "load", lambda *args, **kwargs: catalog)
    monkeypatch.setattr(service, "SnowflakeBackend", MockBackend)
    path = tmp_path / "result.json"
    service.request_worker(
        str(path),
        "Using ACS release 2020, what is the population of Autauga County, Alabama?",
        {},
        Deadline(budget=10),
        {
            "model_budget": {
                "path": str(control.path),
                "limits": asdict(control.limits),
                "request": "request",
            }
        },
    )
    result = json.loads(path.read_text())
    assert result["response"]["status"] == "budget_exhausted"
    assert result["closed"] and not result["connected"]
    assert count(control) == 1
