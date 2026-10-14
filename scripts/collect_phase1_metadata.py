"""Collect dictionaries, FIPS metadata and schema only; never scan indicator data."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from scripts.snowflake_probe import (
    ROOT,
    execute,
    load_config,
    quote_identifier,
    safe_error,
    suspend,
)


def collect() -> int:
    import snowflake.connector

    config = load_config(ROOT / ".env")
    inventory = json.loads((ROOT / "docs/snowflake_evidence.json").read_text())
    names = [r["name"] for r in inventory["tables"]]
    dictionaries = [name for name in names if name.endswith("FIELD_DESCRIPTIONS")]
    fips = [name for name in names if name.endswith("FIPS_CODES")]
    output = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "inventory_source": "docs/snowflake_evidence.json",
        "database": config["SNOWFLAKE_DATABASE"],
        "schema": config["SNOWFLAKE_SCHEMA"],
        "dictionaries": {},
        "fips": {},
    }
    path = ROOT / "docs/phase1_metadata.json"
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
                "QUERY_TAG": "phase1_metadata_only",
            },
        )
        db = quote_identifier(config["SNOWFLAKE_DATABASE"])
        prefix = f"{db}.{quote_identifier(config['SNOWFLAKE_SCHEMA'])}"
        output["columns"] = execute(
            connection,
            f"SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, ORDINAL_POSITION, IS_NULLABLE "
            f"FROM {db}.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s "
            "ORDER BY TABLE_NAME, ORDINAL_POSITION",
            (config["SNOWFLAKE_SCHEMA"],),
        )
        print(f"Schema metadata: {len(output['columns']['rows'])} columns", flush=True)
        for kind, tables in (("dictionaries", dictionaries), ("fips", fips)):
            for name in tables:
                output[kind][name] = execute(
                    connection, f"SELECT * FROM {prefix}.{quote_identifier(name)}"
                )
                print(f"Metadata: {name}; {len(output[kind][name]['rows'])} rows", flush=True)
    except Exception as exc:
        output["error"] = safe_error(exc, config["SNOWFLAKE_PASSWORD"])
        failed = True
    finally:
        if connection is not None:
            output["cleanup"] = suspend(
                connection, config["SNOWFLAKE_WAREHOUSE"], config["SNOWFLAKE_PASSWORD"]
            )
            failed |= not output["cleanup"]["confirmed_suspended"]
            connection.close()
        path.write_text(json.dumps(output, ensure_ascii=False, default=str) + "\n")
    return int(failed)


if __name__ == "__main__":
    sys.exit(collect())
