"""Explicit, bounded live Snowflake configuration probe; no agent implementation."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KEYS = (
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
)
OPTIONAL_KEYS = ("SNOWFLAKE_CORTEX_MODEL",)
MODELS = ("llama3.1-70b", "llama3.3-70b", "mistral-7b", "gemma2-9b")


def quote_identifier(value: str) -> str:
    """Preserve exact case and escape Snowflake delimited identifiers."""
    if not value or "\x00" in value:
        raise ValueError("Identifier must be nonempty and contain no NUL")
    return '"' + value.replace('"', '""') + '"'


def load_config(path: Path) -> dict[str, str]:
    """Read only the explicitly authorized local connection file; never source it."""
    values: dict[str, str] = {}
    if path.exists():
        if path.is_symlink() or path.stat().st_mode & 0o077:
            raise ValueError("Connection file must be a regular owner-only file (chmod 600)")
        for line in path.read_text().splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            key, separator, value = line.partition("=")
            if separator and key.strip() in KEYS + OPTIONAL_KEYS:
                values[key.strip()] = value.strip()
    for key in KEYS + OPTIONAL_KEYS:
        if os.environ.get(key):
            values[key] = os.environ[key]
    if any(not values.get(key) for key in KEYS):
        raise ValueError("Missing required Snowflake configuration; check .env variable names")
    return values


def safe_error(exc: Exception, password: str) -> dict[str, Any]:
    message = str(exc).replace(password, "[REDACTED]") if password else str(exc)
    return {
        "type": type(exc).__name__,
        "errno": getattr(exc, "errno", None),
        "sqlstate": getattr(exc, "sqlstate", None),
        "query_id": getattr(exc, "sfqid", None),
        "message": message,
    }


def execute(connection: Any, sql: str, params: tuple[Any, ...] | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute(sql, params, timeout=60)
        columns = [column[0] for column in cursor.description or ()]
        rows = cursor.fetchall()
        return {
            "query_id": cursor.sfqid,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "columns": columns,
            "rows": rows,
        }


def records(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(zip((c.lower() for c in result["columns"]), row)) for row in result["rows"]]


def save(evidence: dict[str, Any], path: Path) -> None:
    # This artifact contains public Census results and diagnostics, never credentials.
    path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, default=str) + "\n")


def suspend(connection: Any, warehouse: str, password: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    try:
        result["alter"] = execute(
            connection, f"ALTER WAREHOUSE {quote_identifier(warehouse)} SUSPEND"
        )
    except Exception as exc:
        result["alter_error"] = safe_error(exc, password)
    try:
        status = execute(connection, "SHOW WAREHOUSES")
        matching = [row for row in records(status) if row["name"] == warehouse]
        result["show_query_id"] = status["query_id"]
        result["warehouse"] = matching[0] if matching else None
        result["confirmed_suspended"] = bool(matching and matching[0]["state"] == "SUSPENDED")
    except Exception as exc:
        result["show_error"] = safe_error(exc, password)
        result["confirmed_suspended"] = False
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("inventory", "full"), default="inventory")
    parser.add_argument("--core-table", action="append", default=[])
    parser.add_argument("--output", type=Path, default=ROOT / "docs/snowflake_evidence.json")
    args = parser.parse_args()
    config = load_config(ROOT / ".env")
    import snowflake.connector

    evidence: dict[str, Any] = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "connector_version": snowflake.connector.__version__,
        "connection_parameters": {k: v for k, v in config.items() if k != "SNOWFLAKE_PASSWORD"},
        "tables": [],
        "core_tables": [],
        "models": [],
    }
    connection = None
    failed = False
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
                "STATEMENT_QUEUED_TIMEOUT_IN_SECONDS": 30,
                "QUERY_TAG": "codex_snowflake_configuration_probe",
            },
        )
        evidence["context"] = execute(
            connection,
            "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(), "
            "CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_REGION()",
        )
        prefix = ".".join(
            quote_identifier(config[key]) for key in ("SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA")
        )
        listing = execute(connection, f"SHOW TABLES IN SCHEMA {prefix}")
        evidence["table_listing_query_id"] = listing["query_id"]
        evidence["table_listing"] = records(listing)
        views = execute(connection, f"SHOW VIEWS IN SCHEMA {prefix}")
        evidence["view_listing_query_id"] = views["query_id"]
        evidence["view_listing"] = records(views)
        kinds = {row["name"]: "TABLE" for row in evidence["table_listing"]}
        kinds.update({row["name"]: "VIEW" for row in evidence["view_listing"]})
        names = sorted(kinds)
        print(
            f"Connected; discovered {len(evidence['table_listing'])} tables and {len(evidence['view_listing'])} views",
            flush=True,
        )
        for name in names:
            print(f"{kinds[name]}: {name}", flush=True)
        initial_warehouse = records(execute(connection, "SHOW WAREHOUSES"))
        evidence["initial_warehouse"] = next(
            (w for w in initial_warehouse if w["name"] == config["SNOWFLAKE_WAREHOUSE"]), None
        )
        save(evidence, args.output)
        if args.mode == "full":
            if len(args.core_table) != 3 or any(name not in names for name in args.core_table):
                raise ValueError("Full probe requires three --core-table names from live inventory")
            for index, name in enumerate(names, 1):
                table: dict[str, Any] = {"name": name, "kind": kinds[name]}
                try:
                    result = execute(
                        connection, f"SELECT COUNT(*) FROM {prefix}.{quote_identifier(name)}"
                    )
                    table.update(
                        row_count=int(result["rows"][0][0]),
                        query_id=result["query_id"],
                        elapsed_seconds=result["elapsed_seconds"],
                    )
                    print(f"COUNT {index}/{len(names)}: {name} = {table['row_count']}", flush=True)
                except Exception as exc:
                    table["error"] = safe_error(exc, config["SNOWFLAKE_PASSWORD"])
                    failed = True
                    print(f"COUNT {index}/{len(names)}: {name} FAILED", flush=True)
                evidence["tables"].append(table)
                save(evidence, args.output)
            for name in args.core_table:
                sample: dict[str, Any] = {"name": name}
                try:
                    qualified = f"{prefix}.{quote_identifier(name)}"
                    sample["describe"] = execute(connection, f"DESCRIBE TABLE {qualified}")
                    sample["sample"] = execute(connection, f"SELECT * FROM {qualified} LIMIT 5")
                    print(f"SAMPLE: {name}; {len(sample['sample']['columns'])} columns", flush=True)
                except Exception as exc:
                    sample["error"] = safe_error(exc, config["SNOWFLAKE_PASSWORD"])
                    failed = True
                evidence["core_tables"].append(sample)
                save(evidence, args.output)
            models = list(MODELS)
            for model in models:
                probe: dict[str, Any] = {"model": model}
                started = time.perf_counter()
                try:
                    result = execute(
                        connection,
                        "SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, %s)",
                        (model, "Say hello in one sentence."),
                    )
                    output = result["rows"][0][0]
                    probe.update(
                        available=isinstance(output, str) and bool(output.strip()),
                        output=output,
                        query_id=result["query_id"],
                    )
                except Exception as exc:
                    probe.update(
                        available=False, error=safe_error(exc, config["SNOWFLAKE_PASSWORD"])
                    )
                probe["elapsed_seconds"] = round(time.perf_counter() - started, 3)
                evidence["models"].append(probe)
                print(
                    f"MODEL: {model}; available={probe['available']}; {probe['elapsed_seconds']}s",
                    flush=True,
                )
                # Discovering unsupported names is a result, not a reason to retry.
                if model == "llama3.3-70b" and not probe["available"]:
                    models.append("snowflake-llama-3.3-70b")
                save(evidence, args.output)
            if not any(probe["available"] for probe in evidence["models"]):
                failed = True
    except Exception as exc:
        evidence["fatal_error"] = safe_error(exc, config["SNOWFLAKE_PASSWORD"])
        failed = True
        print(f"Probe failed: {type(exc).__name__}; see redacted evidence", flush=True)
    finally:
        if connection is not None:
            evidence["cleanup"] = suspend(
                connection, config["SNOWFLAKE_WAREHOUSE"], config["SNOWFLAKE_PASSWORD"]
            )
            if not evidence["cleanup"]["confirmed_suspended"]:
                failed = True
            connection.close()
            print(
                f"Warehouse confirmed suspended: {evidence['cleanup']['confirmed_suspended']}",
                flush=True,
            )
        evidence["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        save(evidence, args.output)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
