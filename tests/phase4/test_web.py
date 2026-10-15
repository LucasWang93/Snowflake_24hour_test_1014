"""Offline Streamlit AppTest + real local control/processes; Census worker is a mock."""

import hashlib
import json
from pathlib import Path

import pytest

pytest.importorskip("streamlit", reason="Install requirements-web.txt for UI tests")
from streamlit.testing.v1 import AppTest

from census_agent.control import BearerAuthenticator, Limits, SQLiteControl
from census_agent.service import AgentService, write_result
from census_agent.types import Response
from census_web import app, runtime

TOKEN_A = "phase4-offline-fixture-reviewer-A-0000000000"
TOKEN_B = "phase4-offline-fixture-reviewer-B-0000000000"


def mock_census_worker(path, question, state, deadline, options):
    """No Snowflake/Cortex: prove adapter context/privacy with an explicit fake worker."""
    if question == "unsupported":
        response = Response("unsupported", "This statistic is unavailable.", 0)
    else:
        response = Response(
            "answered",
            f"Mock context: {state.get('previous', 'empty')}",
            0,
            metric={
                "year": 2020,
                "source_product": "mock_product",
                "table": "mock_table",
                "column": "mock_column",
                "universe": "mock universe",
            },
            sql=[{"sql": "PRIVATE_SQL_MUST_NOT_RENDER"}],
            error={"message": "PRIVATE_ERROR_MUST_NOT_RENDER"},
        )
        state = {"previous": question}
    write_result(
        path,
        {
            "response": response.as_dict(),
            "state": state,
            "connected": False,
            "closed": True,
            "permissions": {"secret": "PRIVATE_AUDIT_MUST_NOT_RENDER"},
        },
    )


@pytest.fixture
def service(tmp_path, monkeypatch):
    auth = BearerAuthenticator(
        {hashlib.sha256(t.encode()).hexdigest(): who for t, who in ((TOKEN_A, "A"), (TOKEN_B, "B"))}
    )
    service = AgentService(
        auth, SQLiteControl(tmp_path / "control.sqlite"), worker=mock_census_worker
    )
    monkeypatch.setattr(app, "get_service", lambda: service)
    return service


def client():
    return AppTest.from_file(
        Path(__file__).resolve().parents[2] / "web_app.py", default_timeout=15
    ).run()


def button(at, label):
    return next(b for b in at.button if b.label == label)


def login(at, token=TOKEN_A):
    at.text_input[0].input(token)
    button(at, "Sign in").click().run()
    assert not at.exception
    return at


def texts(at):
    return " ".join(
        element.value
        for kind in ("text", "caption", "json", "error", "info")
        for element in at.get(kind)
    )


def test_authentication_required_and_invalid_token_cannot_open_chat(service):
    at = client()
    assert not at.chat_input
    assert at.text_input[0].proto.type == 1  # Streamlit TextInput.PASSWORD
    login(at, "wrong-token-that-is-longer-than-thirty-two")
    assert "Authentication is required" in texts(at)
    assert not at.chat_input
    login(at)
    assert at.chat_input
    assert TOKEN_A not in texts(at)


def test_multi_turn_reset_provenance_and_private_diagnostics(service):
    at = login(client())
    at.chat_input[0].set_value("first geography").run()
    at.chat_input[0].set_value("follow-up").run()
    assert "Mock context: first geography" in texts(at)
    assert "Release 2020" in texts(at) and "mock_product" in texts(at)
    assert "PRIVATE_" not in texts(at) and TOKEN_A not in texts(at)
    assert len(at.chat_message) == 4
    button(at, "New conversation").click().run()
    assert not at.chat_message
    at.chat_input[0].set_value("new scope").run()
    assert "Mock context: empty" in texts(at)


def test_two_browser_states_do_not_share_context_and_logout(service):
    a, b = login(client()), login(client(), TOKEN_B)
    a.chat_input[0].set_value("private-A-context").run()
    b.chat_input[0].set_value("follow-up").run()
    assert "Mock context: empty" in texts(b)
    assert "private-A-context" not in texts(b)
    assert a.session_state.conversation != b.session_state.conversation
    button(a, "Sign out").click().run()
    assert not a.chat_input and not a.chat_message


def test_unsupported_and_provider_boundary_failure_are_graceful(service, monkeypatch):
    at = login(client())
    at.chat_input[0].set_value("unsupported").run()
    assert "This statistic is unavailable" in texts(at)

    def fail(*args):
        raise RuntimeError("PRIVATE_EXCEPTION_MUST_NOT_RENDER")

    monkeypatch.setattr(service, "ask", fail)
    at.chat_input[0].set_value("population").run()
    assert "temporarily unavailable" in texts(at)
    assert "PRIVATE_" not in texts(at) and not at.exception


def test_shared_rate_limit_displayed_and_no_extra_worker(service):
    control = SQLiteControl(
        service.control.path.parent / "limited.sqlite", Limits(principal_requests_per_minute=1)
    )
    service.control = control
    at = login(client())
    at.chat_input[0].set_value("first").run()
    at.chat_input[0].set_value("second").run()
    assert "Request rate limit reached" in texts(at)
    assert not at.exception


def test_missing_configuration_is_a_safe_page(monkeypatch):
    def fail():
        raise ValueError("PRIVATE_CONFIGURATION_MUST_NOT_RENDER")

    monkeypatch.setattr(app, "get_service", fail)
    at = client()
    assert "not configured for public access" in texts(at)
    assert "PRIVATE_" not in texts(at) and not at.chat_input and not at.exception


@pytest.fixture
def deployment_env(tmp_path, monkeypatch):
    for name in (
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE",
        "SNOWFLAKE_AUTH_MODE",
    ):
        monkeypatch.delenv(name, raising=False)
    key = tmp_path / "mock.p8"
    key.write_text("not a real key; offline presence fixture")
    key.chmod(0o600)
    env = {
        "CENSUS_PERMISSIONS_REVIEWED": "1",
        "CENSUS_EXCLUSIVE_WAREHOUSE": "1",
        "CENSUS_DURABLE_STORAGE": "1",
        "CENSUS_HTTPS_ORIGIN": "https://census.example.org",
        "CENSUS_REVIEWER_DIGESTS": json.dumps({hashlib.sha256(TOKEN_A.encode()).hexdigest(): "A"}),
        "CENSUS_SNOWFLAKE_ROLE": "CENSUS_APP_READONLY",
        "CENSUS_CONTROL_PATH": str(tmp_path / "durable" / "control.sqlite"),
        "SNOWFLAKE_ACCOUNT": "mock-account",
        "SNOWFLAKE_USER": "CENSUS_WEB_APP",
        "SNOWFLAKE_WAREHOUSE": "CENSUS_APP_WH",
        "SNOWFLAKE_DATABASE": "mock_database",
        "SNOWFLAKE_SCHEMA": "PUBLIC",
        "SNOWFLAKE_PRIVATE_KEY_FILE": str(key),
    }
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    return env


def test_dedicated_config_uses_same_durable_store_and_never_local_env(deployment_env, monkeypatch):
    def forbidden(*args):
        raise AssertionError("Development loader must never be used")

    monkeypatch.setattr("census_agent.backend.load_config", forbidden)
    a, b = runtime.build_service(), runtime.build_service()
    assert a.control.path == b.control.path
    assert a.options["role"] == "CENSUS_APP_READONLY" and a.options["secondary_roles"] == "NONE"
    assert a.options["connection_config"]["SNOWFLAKE_USER"] == "CENSUS_WEB_APP"
    assert Path(deployment_env["CENSUS_CONTROL_PATH"]).stat().st_mode & 0o077 == 0


@pytest.mark.parametrize(
    "name,value",
    [
        ("CENSUS_PERMISSIONS_REVIEWED", "0"),
        ("CENSUS_EXCLUSIVE_WAREHOUSE", "0"),
        ("CENSUS_DURABLE_STORAGE", "0"),
        ("CENSUS_HTTPS_ORIGIN", "http://public.example.org"),
        ("CENSUS_HTTPS_ORIGIN", "https://user:private@public.example.org"),
        ("CENSUS_REVIEWER_DIGESTS", "invalid"),
        ("CENSUS_REVIEWER_DIGESTS", "[]"),
        ("CENSUS_SNOWFLAKE_ROLE", "PUBLIC"),
        ("CENSUS_SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        ("SNOWFLAKE_USER", "CODEX_APP"),
        ("SNOWFLAKE_PASSWORD", "offline-forbidden-value"),
        ("CENSUS_CONTROL_PATH", "relative.sqlite"),
        ("SNOWFLAKE_PRIVATE_KEY_FILE", "/not-present/mock.p8"),
    ],
)
def test_unsafe_deployment_configuration_fails_closed(deployment_env, monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises((runtime.ConfigurationIssue, ValueError)):
        runtime.build_service()


def test_key_pair_connector_options_without_reading_dev_env(deployment_env, monkeypatch):
    from unittest.mock import MagicMock

    import snowflake.connector

    from census_agent.backend import SnowflakeBackend
    from census_agent.types import Deadline

    service = runtime.build_service()
    mock = MagicMock()
    monkeypatch.setattr(snowflake.connector, "connect", mock)
    monkeypatch.setattr(SnowflakeBackend, "_run", lambda *args: {"columns": [], "rows": []})
    monkeypatch.setattr(
        "census_agent.backend.load_config", lambda *args: pytest.fail("local .env read")
    )
    backend = SnowflakeBackend(None, **service.options)
    backend.connect(Deadline())
    kwargs = mock.call_args.kwargs
    assert kwargs["authenticator"] == "SNOWFLAKE_JWT" and "password" not in kwargs
    assert (
        kwargs["role"] == "CENSUS_APP_READONLY"
        and kwargs["private_key_file"] == deployment_env["SNOWFLAKE_PRIVATE_KEY_FILE"]
    )


def test_private_key_permissions_and_symlink_rejected(deployment_env, tmp_path, monkeypatch):
    path = Path(deployment_env["SNOWFLAKE_PRIVATE_KEY_FILE"])
    path.chmod(0o644)
    with pytest.raises(runtime.ConfigurationIssue):
        runtime.build_service()
    path.chmod(0o600)
    link = tmp_path / "linked.p8"
    link.symlink_to(path)
    monkeypatch.setenv("SNOWFLAKE_PRIVATE_KEY_FILE", str(link))
    with pytest.raises(runtime.ConfigurationIssue):
        runtime.build_service()


@pytest.fixture
def password_deployment_env(deployment_env, monkeypatch):
    monkeypatch.delenv("SNOWFLAKE_PRIVATE_KEY_FILE")
    monkeypatch.setenv("SNOWFLAKE_AUTH_MODE", "password")
    monkeypatch.setenv("SNOWFLAKE_USER", "AGENT_PROD")
    monkeypatch.setenv("SNOWFLAKE_PASSWORD", "offline-production-password-fixture")
    return deployment_env


def test_production_password_connector_uses_environment_only(password_deployment_env, monkeypatch):
    from unittest.mock import MagicMock

    import snowflake.connector

    from census_agent.backend import SnowflakeBackend
    from census_agent.types import Deadline

    monkeypatch.setattr(
        "census_agent.backend.load_config", lambda *args: pytest.fail("Development .env read")
    )
    mock = MagicMock()
    monkeypatch.setattr(snowflake.connector, "connect", mock)
    monkeypatch.setattr(SnowflakeBackend, "_run", lambda *args: {"columns": [], "rows": []})
    service = runtime.build_service()
    backend = SnowflakeBackend(None, **service.options)
    backend.connect(Deadline())
    kwargs = mock.call_args.kwargs
    assert kwargs["user"] == "AGENT_PROD"
    assert kwargs["password"] == "offline-production-password-fixture"
    assert "private_key_file" not in kwargs and "authenticator" not in kwargs
    assert service.options["secondary_roles"] == "NONE"
    assert service.options["role"] == "CENSUS_APP_READONLY"
    assert "SNOWFLAKE_PRIVATE_KEY_FILE" not in service.options["connection_config"]


@pytest.mark.parametrize(
    "name,value",
    [
        ("SNOWFLAKE_USER", "CODEX_APP"),
        ("SNOWFLAKE_USER", "UNAPPROVED_USER"),
        ("SNOWFLAKE_PASSWORD", ""),
        ("SNOWFLAKE_ACCOUNT", ""),
        ("SNOWFLAKE_AUTH_MODE", "auto"),
        ("SNOWFLAKE_PRIVATE_KEY_FILE", "/server/unused.p8"),
        ("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", "offline-passphrase"),
        ("CENSUS_SNOWFLAKE_ROLE", "PUBLIC"),
        ("CENSUS_PERMISSIONS_REVIEWED", "0"),
        ("CENSUS_EXCLUSIVE_WAREHOUSE", "0"),
    ],
)
def test_password_deployment_fails_closed_without_fallback(
    password_deployment_env, monkeypatch, name, value
):
    monkeypatch.setenv(name, value)
    monkeypatch.setattr(
        "census_agent.backend.load_config", lambda *args: pytest.fail("Development .env read")
    )
    with pytest.raises(runtime.ConfigurationIssue) as error:
        runtime.build_service()
    assert "offline-production-password-fixture" not in str(error.value)


def test_review_limits_are_configurable(deployment_env, monkeypatch):
    settings = {
        "CENSUS_MODEL_CALLS_PER_DAY": "1200",
        "CENSUS_REQUESTS_PER_MINUTE": "12",
        "CENSUS_GLOBAL_REQUESTS_PER_MINUTE": "60",
        "CENSUS_MAX_SESSIONS": "256",
        "CENSUS_SESSION_TTL_SECONDS": "7200",
    }
    for name, value in settings.items():
        monkeypatch.setenv(name, value)
    limits = runtime.build_service().control.limits
    assert (limits.model_calls_per_day, limits.principal_requests_per_minute) == (1200, 12)
    assert (limits.global_requests_per_minute, limits.max_sessions, limits.session_ttl) == (
        60,
        256,
        7200,
    )
    assert limits.deadline_seconds == 55


@pytest.mark.parametrize("value", ["0", "2001", "nonsense"])
def test_invalid_review_budget_fails_closed(deployment_env, monkeypatch, value):
    monkeypatch.setenv("CENSUS_MODEL_CALLS_PER_DAY", value)
    with pytest.raises(runtime.ConfigurationIssue, match="CENSUS_MODEL_CALLS_PER_DAY"):
        runtime.build_service()
