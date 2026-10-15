"""Fail-closed deployment configuration. Never fall back to development .env."""

from __future__ import annotations

import json
import os
import re
import stat
from pathlib import Path
from urllib.parse import urlsplit

from census_agent.control import BearerAuthenticator, Limits, SQLiteControl
from census_agent.service import AgentService


class ConfigurationIssue(ValueError):
    """Contains a safe configuration name/reason, never a supplied secret value."""


def build_service() -> AgentService:
    for key in (
        "CENSUS_PERMISSIONS_REVIEWED",
        "CENSUS_EXCLUSIVE_WAREHOUSE",
        "CENSUS_DURABLE_STORAGE",
    ):
        if os.environ.get(key) != "1":
            raise ConfigurationIssue(f"Administrator confirmation required: {key}")
    origin = urlsplit(os.environ.get("CENSUS_HTTPS_ORIGIN", ""))
    if (
        origin.scheme != "https"
        or not origin.hostname
        or origin.username
        or origin.password
        or origin.path not in ("", "/")
        or origin.query
        or origin.fragment
    ):
        raise ConfigurationIssue("CENSUS_HTTPS_ORIGIN must be an HTTPS origin")
    try:
        digests = json.loads(os.environ.get("CENSUS_REVIEWER_DIGESTS", ""))
        if not isinstance(digests, dict):
            raise ValueError
        auth = BearerAuthenticator(digests)
    except (ValueError, TypeError):
        raise ConfigurationIssue(
            "CENSUS_REVIEWER_DIGESTS must contain bounded token digests"
        ) from None

    role = os.environ.get("CENSUS_SNOWFLAKE_ROLE", "")
    if not re.fullmatch(r"[A-Z][A-Z0-9_]{0,254}", role) or role in {
        "PUBLIC",
        "ACCOUNTADMIN",
        "SECURITYADMIN",
        "USERADMIN",
        "SYSADMIN",
        "ORGADMIN",
    }:
        raise ConfigurationIssue("CENSUS_SNOWFLAKE_ROLE must be an administrator-reviewed app role")
    keys = (
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
    )
    config = {key: os.environ.get(key, "") for key in keys}
    if any(not value for value in config.values()):
        raise ConfigurationIssue("Missing required server-side Snowflake configuration names")
    if config["SNOWFLAKE_USER"].upper() == "CODEX_APP":
        raise ConfigurationIssue("Development identity is forbidden in the public adapter")
    mode = os.environ.get("SNOWFLAKE_AUTH_MODE", "keypair")
    if mode == "password":
        if config["SNOWFLAKE_USER"].upper() != "AGENT_PROD":
            raise ConfigurationIssue("Password deployment requires SNOWFLAKE_USER=AGENT_PROD")
        if os.environ.get("SNOWFLAKE_PRIVATE_KEY_FILE") or os.environ.get(
            "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"
        ):
            raise ConfigurationIssue("Configure exactly one server-side authentication method")
        password = os.environ.get("SNOWFLAKE_PASSWORD", "")
        if not password:
            raise ConfigurationIssue("Missing server-side SNOWFLAKE_PASSWORD")
        config["SNOWFLAKE_PASSWORD"] = password
    elif mode == "keypair":
        if os.environ.get("SNOWFLAKE_PASSWORD"):
            raise ConfigurationIssue("Configure exactly one server-side authentication method")
        key_path = Path(os.environ.get("SNOWFLAKE_PRIVATE_KEY_FILE", ""))
        if (
            not key_path.is_absolute()
            or key_path.is_symlink()
            or not key_path.is_file()
            or stat.S_IMODE(key_path.stat().st_mode) & 0o077
        ):
            raise ConfigurationIssue("Private key must be an absolute, owner-only regular file")
        config["SNOWFLAKE_PRIVATE_KEY_FILE"] = str(key_path)
        if os.environ.get("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"):
            config["SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"] = os.environ[
                "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"
            ]
    else:
        raise ConfigurationIssue("SNOWFLAKE_AUTH_MODE must be password or keypair")
    control_path = Path(os.environ.get("CENSUS_CONTROL_PATH", ""))
    if not control_path.is_absolute():
        raise ConfigurationIssue("CENSUS_CONTROL_PATH must be an absolute durable local path")
    control_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if control_path.parent.is_symlink() or stat.S_IMODE(control_path.parent.stat().st_mode) & 0o077:
        raise ConfigurationIssue("Control directory must be private and regular")
    limits = {}
    for name, field, default, maximum in (
        ("CENSUS_MODEL_CALLS_PER_DAY", "model_calls_per_day", 120, 2000),
        ("CENSUS_REQUESTS_PER_MINUTE", "principal_requests_per_minute", 6, 60),
        ("CENSUS_GLOBAL_REQUESTS_PER_MINUTE", "global_requests_per_minute", 20, 120),
        ("CENSUS_MAX_SESSIONS", "max_sessions", 128, 1024),
        ("CENSUS_SESSION_TTL_SECONDS", "session_ttl", 1800, 86400),
    ):
        try:
            value = int(os.environ.get(name, str(default)))
            if not 1 <= value <= maximum:
                raise ValueError
        except ValueError:
            raise ConfigurationIssue(f"{name} must be an integer from 1 to {maximum}") from None
        limits[field] = value
    return AgentService(
        auth,
        SQLiteControl(control_path, Limits(**limits)),
        backend_options={
            "role": role,
            "secondary_roles": "NONE",
            "connection_config": config,
        },
    )
