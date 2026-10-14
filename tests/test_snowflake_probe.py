"""Deterministic local tests; all cursor/connection doubles are mocks, not Snowflake."""

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

MODULE = Path(__file__).resolve().parents[1] / "scripts/snowflake_probe.py"
spec = importlib.util.spec_from_file_location("snowflake_probe", MODULE)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("Population by Age", '"Population by Age"'), ('a"b', '"a""b"'), ("MiXeD-%", '"MiXeD-%"')],
)
def test_quote_preserves_identifier_without_sql_injection(value, expected):
    assert probe.quote_identifier(value) == expected


@pytest.mark.parametrize("value", ["", "bad\x00name"])
def test_invalid_identifiers_rejected(value):
    with pytest.raises(ValueError):
        probe.quote_identifier(value)


def test_config_reads_only_known_keys_and_environment_overrides(tmp_path, monkeypatch):
    for key in probe.KEYS:
        monkeypatch.delenv(key, raising=False)
    path = tmp_path / ".env"
    path.write_text("\n".join(f"{key}=fixture-value" for key in probe.KEYS) + "\nOTHER=ignored\n")
    path.chmod(0o600)
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "test-account")
    result = probe.load_config(path)
    assert result["SNOWFLAKE_ACCOUNT"] == "test-account"
    assert set(result) == set(probe.KEYS)


def test_world_readable_config_rejected(tmp_path):
    path = tmp_path / ".env"
    path.write_text("SNOWFLAKE_PASSWORD=fixture-only\n")
    path.chmod(0o644)
    with pytest.raises(ValueError, match="owner-only"):
        probe.load_config(path)


def test_missing_config_reports_names_without_values(tmp_path, monkeypatch):
    for key in probe.KEYS:
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(ValueError, match="Missing required Snowflake configuration"):
        probe.load_config(tmp_path / "absent")


def test_error_message_redacts_password():
    assert probe.safe_error(ValueError("oops fixture-password"), "fixture-password")["message"] == (
        "oops [REDACTED]"
    )


def test_cursor_is_closed_and_params_are_bound():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.description = [("COUNT",)]
    cursor.fetchall.return_value = [(42,)]
    cursor.sfqid = "mock-query-id"
    result = probe.execute(connection, "SELECT %s", (42,))
    cursor.execute.assert_called_once_with("SELECT %s", (42,), timeout=60)
    assert result["rows"] == [(42,)]
    assert result["query_id"] == "mock-query-id"
    connection.cursor.return_value.__exit__.assert_called_once()


def test_suspend_failure_does_not_claim_success(monkeypatch):
    calls = []

    def mock_execute(connection, sql, params=None):
        calls.append(sql)
        if sql.startswith("ALTER"):
            raise PermissionError("mock: missing OPERATE")
        return {"query_id": "mock-show", "columns": ["name", "state"], "rows": [("WH", "STARTED")]}

    monkeypatch.setattr(probe, "execute", mock_execute)
    result = probe.suspend(object(), "WH", "fixture-password")
    assert calls == ['ALTER WAREHOUSE "WH" SUSPEND', "SHOW WAREHOUSES"]
    assert result["confirmed_suspended"] is False
    assert "alter_error" in result


def test_already_suspended_is_confirmed_after_alter_error(monkeypatch):
    def mock_execute(connection, sql, params=None):
        if sql.startswith("ALTER"):
            raise RuntimeError("mock: already suspended")
        return {
            "query_id": "mock-show",
            "columns": ["name", "state"],
            "rows": [("WH", "SUSPENDED")],
        }

    monkeypatch.setattr(probe, "execute", mock_execute)
    assert probe.suspend(object(), "WH", "fixture-password")["confirmed_suspended"] is True


def test_optional_model_is_loaded_without_becoming_required(tmp_path, monkeypatch):
    for key in probe.KEYS + probe.OPTIONAL_KEYS:
        monkeypatch.delenv(key, raising=False)
    path = tmp_path / ".env"
    path.write_text("\n".join(f"{key}=fixture-value" for key in probe.KEYS))
    path.chmod(0o600)
    assert "SNOWFLAKE_CORTEX_MODEL" not in probe.load_config(path)
    monkeypatch.setenv("SNOWFLAKE_CORTEX_MODEL", "fixture-model")
    assert probe.load_config(path)["SNOWFLAKE_CORTEX_MODEL"] == "fixture-model"


def test_symlink_connection_file_is_rejected(tmp_path):
    target = tmp_path / "fixture"
    target.write_text("fixture-only")
    target.chmod(0o600)
    link = tmp_path / ".env"
    link.symlink_to(target)
    with pytest.raises(ValueError, match="regular owner-only"):
        probe.load_config(link)
