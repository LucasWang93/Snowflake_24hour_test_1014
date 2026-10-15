"""Offline reliability tests. Worker/model/database failures below are explicit mocks."""

import hashlib
import json
import logging
import multiprocessing as mp
import os
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import pytest

from census_agent.agent import CensusAgent
from census_agent.backend import SnowflakeBackend
from census_agent.control import BearerAuthenticator, ControlIssue, Limits, SQLiteControl
from census_agent.service import AgentService, write_result
from census_agent.types import ConversationState, Deadline, Response, ServiceIssue
from tests.phase2.test_core import MockBackend, choice, intent

TOKEN_A = "offline-fixture-principal-A-token-00000000"
TOKEN_B = "offline-fixture-principal-B-token-00000000"


def auth():
    return BearerAuthenticator(
        {
            hashlib.sha256(TOKEN_A.encode()).hexdigest(): "A",
            hashlib.sha256(TOKEN_B.encode()).hexdigest(): "B",
        }
    )


def echo_worker(path, question, state, deadline, options):
    """Mock worker has no connector/Cortex; echoes only its own prior state."""
    response = Response(
        "answered", str(state.get("last", "empty")), 0, cleanup={"confirmed_suspended": True}
    )
    write_result(
        path,
        {
            "response": response.as_dict(),
            "state": {"last": question},
            "connected": False,
            "closed": True,
            "permissions": {},
        },
    )


def blocked_worker(path, question, state, deadline, options):
    time.sleep(60)  # Deliberately uncooperative provider/connector mock; parent must stop it.


def crashed_worker(path, question, state, deadline, options):
    os._exit(2)


def failed_cleanup_worker(path, question, state, deadline, options):
    response = Response("error", "Mock provider failure", 0, cleanup={"confirmed_suspended": False})
    write_result(
        path,
        {
            "response": response.as_dict(),
            "state": state,
            "connected": True,
            "closed": False,
            "permissions": {},
        },
    )


def admission_child(path, session, barrier, queue):
    control = SQLiteControl(Path(path))
    barrier.wait(10)
    try:
        control.begin("A", session, str(os.getpid()))
        queue.put(("admitted", str(os.getpid())))
    except ControlIssue as exc:
        queue.put((exc.status, str(os.getpid())))


@pytest.fixture
def control(tmp_path):
    return SQLiteControl(tmp_path / "control.sqlite")


def test_authentication_is_fail_closed(control):
    service = AgentService(auth(), control, worker=echo_worker)
    for token in ("", "x" * 31, "x" * 257, "incorrect-token-that-is-at-least-32-characters", None):
        result = service.ask(token, "a" * 32, "Census question")
        assert result.public["status"] == "unauthorized" and result.diagnostics is None
    assert str(TOKEN_A) not in repr(auth().__dict__)


def test_authenticated_owner_cannot_access_or_reset_another_session(control):
    service = AgentService(auth(), control, worker=echo_worker)
    session = service.create_session(TOKEN_A)
    assert service.ask(TOKEN_B, session, "Question").public["status"] == "unauthorized"
    with pytest.raises(ControlIssue):
        service.reset(TOKEN_B, session)


def test_separate_processes_only_one_can_reserve_shared_trial_warehouse(control):
    session = control.create_session("A")
    ctx = mp.get_context("spawn")
    barrier, queue = ctx.Barrier(2), ctx.Queue()
    workers = [
        ctx.Process(target=admission_child, args=(str(control.path), session, barrier, queue))
        for _ in range(2)
    ]
    for worker in workers:
        worker.start()
    results = [queue.get(timeout=15) for _ in workers]
    for worker in workers:
        worker.join(10)
        assert worker.exitcode == 0
        worker.close()
    assert sorted(r[0] for r in results) == ["admitted", "overloaded"]
    admitted = next(r[1] for r in results if r[0] == "admitted")
    control.finish(admitted, {}, healthy=True)
    queue.close()


def test_two_services_share_rate_limits_and_model_budget(tmp_path):
    limits = Limits(principal_requests_per_minute=1, model_calls_per_day=4)
    a, b = (
        SQLiteControl(tmp_path / "control.sqlite", limits),
        SQLiteControl(tmp_path / "control.sqlite", limits),
    )
    session_a, session_b = a.create_session("A"), b.create_session("B")
    a.begin("A", session_a, "request-a")
    a.record_model_submission("request-a")
    a.record_model_submission("request-a")
    a.finish("request-a", {}, healthy=True)
    with pytest.raises(ControlIssue) as rate:
        b.begin("A", session_a, "request-a2")
    assert rate.value.status == "rate_limited"
    b.begin("B", session_b, "request-b")
    b.record_model_submission("request-b")
    b.record_model_submission("request-b")
    b.finish("request-b", {}, healthy=True)
    session_c = a.create_session("C")
    a.begin("C", session_c, "request-c")
    with pytest.raises(ControlIssue) as budget:
        a.record_model_submission("request-c")
    assert budget.value.status == "budget_exhausted"


def test_controls_reject_mismatched_deployment_limits(control):
    with pytest.raises(ValueError, match="must match"):
        SQLiteControl(control.path, Limits(model_calls_per_day=2))


def test_session_capacity_expiry_and_reset(tmp_path):
    control = SQLiteControl(tmp_path / "control.sqlite", Limits(max_sessions=1, session_ttl=2))
    session = control.create_session("A")
    with pytest.raises(ControlIssue):
        control.create_session("B")
    with patch("census_agent.control.time.time", return_value=time.time() + 3):
        with pytest.raises(ControlIssue):
            control.begin("A", session, "expired")
        assert control.create_session("B") != session


@pytest.mark.parametrize("worker", [blocked_worker, crashed_worker, failed_cleanup_worker])
def test_worker_timeout_crash_or_cleanup_failure_quarantines_service(tmp_path, worker):
    limits = Limits(deadline_seconds=0.3 if worker == blocked_worker else 5)
    control = SQLiteControl(tmp_path / "control.sqlite", limits)
    service = AgentService(auth(), control, worker=worker)
    session = service.create_session(TOKEN_A)
    started = time.monotonic()
    result = service.ask(TOKEN_A, session, "First request")
    assert time.monotonic() - started < 6
    assert result.public["status"] in {"timeout", "unavailable", "error"}
    assert not result.public["results"]
    assert service.ask(TOKEN_A, session, "Next request").public["status"] == "unavailable"
    assert not list(control.path.parent.glob("request-*"))


def test_lost_expired_worker_lease_does_not_auto_admit(control):
    session = control.create_session("A")
    control.begin("A", session, "lost")
    with patch("census_agent.control.time.time", return_value=time.time() + 100):
        with pytest.raises(ControlIssue) as exc:
            control.begin("A", session, "new")
    assert exc.value.status == "unavailable"


def test_session_state_roundtrip_and_safe_logs(control, caplog):
    service = AgentService(auth(), control, worker=echo_worker)
    a, b = service.create_session(TOKEN_A), service.create_session(TOKEN_B)
    sentinel = "private-query-sentinel"
    caplog.set_level(logging.INFO, logger="census_agent.operations")
    assert service.ask(TOKEN_A, a, sentinel).public["answer"] == "empty"
    assert service.ask(TOKEN_B, b, "different").public["answer"] == "empty"
    assert service.ask(TOKEN_A, a, "followup").public["answer"] == sentinel
    service.reset(TOKEN_A, a)
    assert service.ask(TOKEN_A, a, "after reset").public["answer"] == "empty"
    assert sentinel not in caplog.text and TOKEN_A not in caplog.text and a not in caplog.text


def test_public_response_excludes_raw_diagnostics():
    response = Response(
        "error",
        "Safe error",
        0,
        error={"message": "fixture-secret"},
        model_calls=[{"structured_output": "fixture-secret"}],
        sql=[{"sql": "fixture-secret"}],
        intent={"metric": "fixture-secret"},
    )
    assert "fixture-secret" not in json.dumps(response.public_dict())
    assert "fixture-secret" in json.dumps(response.as_dict())


def test_backend_error_discards_arbitrary_connector_exception_text(catalog):
    backend = SnowflakeBackend(catalog)
    backend._config = {"SNOWFLAKE_PASSWORD": "offline-fixture-only"}
    detail = backend._failure("connection", RuntimeError("unrelated-private-token")).detail
    assert "message" not in detail and "unrelated-private-token" not in json.dumps(detail)


def test_backend_thread_ownership_is_enforced(catalog):
    backend = SnowflakeBackend(catalog)
    backend._assert_owner()
    with ThreadPoolExecutor(1) as executor:
        with pytest.raises(ServiceIssue):
            executor.submit(backend._assert_owner).result()


def test_overlapping_requests_cannot_share_agent_or_conversation(catalog):
    entered, release = threading.Event(), threading.Event()
    backend = MockBackend([intent(), choice("2020_CBG_B01.B01003e1")])
    original = backend.complete

    def wait(*args):
        entered.set()
        release.wait(5)
        return original(*args)

    backend.complete = wait
    agent, state = CensusAgent(catalog, backend), ConversationState()
    with ThreadPoolExecutor(1) as executor:
        first = executor.submit(agent.ask, "First", state)
        assert entered.wait(3)
        assert agent.ask("Second", state).status == "overloaded"
        other = CensusAgent(catalog, MockBackend([]))
        assert other.ask("Third", state).status == "overloaded"
        release.set()
        assert first.result().status == "answered"


@pytest.mark.parametrize("stage", ["model", "database"])
def test_soft_deadline_does_not_commit_late_answer_or_context(catalog, stage):
    backend = MockBackend([intent(), choice("2020_CBG_B01.B01003e1")])
    if stage == "model":
        backend.complete = lambda *args: (time.sleep(0.04), intent())[1]
    else:
        original = backend.execute_data
        backend.execute_data = lambda *args: (time.sleep(0.04), original(*args))[1]
    state = ConversationState()
    result = CensusAgent(catalog, backend).ask("Question", state, deadline=Deadline(budget=0.02))
    assert result.status == "error" and not result.results and state.resolved is None


def test_database_lock_fails_fast_without_exposing_exception(control):
    session = control.create_session("A")
    service = AgentService(auth(), control, worker=echo_worker)
    db = sqlite3.connect(control.path)
    db.execute("BEGIN IMMEDIATE")
    try:
        start = time.monotonic()
        result = service.ask(TOKEN_A, session, "Question")
        assert result.public["status"] == "unavailable" and time.monotonic() - start < 1
        assert "database is locked" not in json.dumps(result.public)
    finally:
        db.rollback()
        db.close()


def test_model_may_not_invent_product_for_ambiguous_2020_population(catalog):
    backend = MockBackend(
        [
            intent(
                product="decennial",
                geographies=[{"type": "county", "name": "Baldwin County", "state": "Alabama"}],
            )
        ]
    )
    response = CensusAgent(catalog, backend).ask(
        "What is the total population of Baldwin County, Alabama in 2020?"
    )
    assert response.status == "clarification" and not backend.executions


def test_household_count_is_not_median_income_even_if_model_confuses_terms(catalog):
    backend = MockBackend([intent("household income", "count"), choice("2020_CBG_B11.B11001e1")])
    response = CensusAgent(catalog, backend).ask(
        "What is the total number of households at CBG 010010201001 using ACS 2020?"
    )
    assert response.status == "answered" and response.metric["universe"] == "Households"


def test_metadata_filters_match_tenure_and_poverty_without_numeric_substitution(catalog):
    from census_agent.planning import candidate_fields
    from census_agent.types import Intent

    poverty = Intent.parse(
        intent("income", "count", year=2019, filters={"income_band": "below poverty level"})
    )
    choices = candidate_fields(
        catalog, poverty, "How many individuals had income below poverty level using ACS 2019?"
    )
    assert any(e["id"] == "2019_CBG_B17.B17021e2" for e in choices)
    assert all("below poverty level" in " ".join(e["field_path"]).lower() for e in choices)
    tenure = Intent.parse(intent("housing", "median", filters={"ownership": "owner-occupied"}))
    choices = candidate_fields(
        catalog, tenure, "Median value in dollars of owner-occupied housing units?"
    )
    assert any(e["id"] == "2020_CBG_B25.B25077e1" for e in choices)
    assert all("owner-occupied" in e["universe"].lower() for e in choices)


def test_operator_recovery_requires_evidence_and_cannot_clear_live_lease(control):
    session = control.create_session("A")
    control.begin("A", session, "active")
    with pytest.raises(ValueError):
        control.recover_after_operator_check(
            warehouse_suspended=True, no_active_server_queries=False
        )
    with pytest.raises(ControlIssue):
        control.recover_after_operator_check(
            warehouse_suspended=True, no_active_server_queries=True
        )
    control.finish("active", None, healthy=False)
    control.recover_after_operator_check(warehouse_suspended=True, no_active_server_queries=True)
    assert control.begin("A", session, "recovered") == {}
    control.finish("recovered", {}, healthy=True)


def test_scope_only_followup_preserves_verified_metric_despite_model_topic_guess(catalog):
    from census_agent.types import Intent

    state = ConversationState(
        resolved=Intent.parse(intent("households", "count")), entry_id="2020_CBG_B11.B11001e1"
    )
    backend = MockBackend([intent("household income", "count")])
    response = CensusAgent(catalog, backend).ask(
        "For Census block group 010010201001 instead?", state
    )
    assert response.status == "answered" and response.metric["column"] == "B11001e1"


def test_explicit_education_category_changes_topic_when_model_omits_metric(catalog):
    from census_agent.types import Intent

    state = ConversationState(
        resolved=Intent.parse(intent("employment", "count", filters={"employment": "employed"})),
        entry_id="2020_CBG_B23.B23025e4",
    )
    delta = intent(
        None,
        None,
        year=None,
        product=None,
        geographies=[],
        filters={"age": "25 years and over", "education": "Bachelor's degree"},
    )
    backend = MockBackend([delta, choice("2020_CBG_B15.B15003e22")])
    response = CensusAgent(catalog, backend).ask(
        "What about people aged 25 years and over whose highest educational attainment is a bachelor's degree only?",
        state,
    )
    assert response.status == "answered" and response.metric["column"] == "B15003e22"
