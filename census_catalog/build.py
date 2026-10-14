"""Reconcile provider dictionaries against captured exact physical schema."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from census_catalog.aggregation import classify

INDICATOR_TABLE = re.compile(r"(?:2019|2020)_CBG_[BC][0-9]{2}\Z")
REDS_TABLE = "2020_REDISTRICTING_CBG_DATA"
ACS_SOURCE = "https://www.census.gov/programs-surveys/acs/data/data-tables/table-ids-explained.html"
REDS_SOURCE = (
    "https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html"
)


def result_records(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(zip(result["columns"], row)) for row in result["rows"]]


def build_catalog(snapshot_path: Path, inventory_path: Path, states_path: Path) -> dict[str, Any]:
    snapshot = json.loads(snapshot_path.read_text())
    inventory = json.loads(inventory_path.read_text())
    states = json.loads(states_path.read_text())
    if "error" in snapshot or not snapshot.get("columns", {}).get("rows"):
        raise ValueError("Incomplete metadata snapshot")
    objects = {row["name"]: row["kind"] for row in inventory["tables"]}
    schemas: dict[str, list[dict[str, Any]]] = {}
    for row in result_records(snapshot["columns"]):
        table = row["TABLE_NAME"]
        if table in objects:
            schemas.setdefault(table, []).append(
                {
                    "column": row["COLUMN_NAME"],
                    "data_type": row["DATA_TYPE"],
                    "ordinal": row["ORDINAL_POSITION"],
                    "nullable": row["IS_NULLABLE"] == "YES",
                }
            )
    if set(schemas) != set(objects):
        raise ValueError("Physical schema is missing an inventoried object")
    for columns in schemas.values():
        if len({c["column"] for c in columns}) != len(columns):
            raise ValueError("Duplicate physical schema columns")
    definitions: dict[tuple[int, str], dict[str, Any]] = {}
    for source, result in snapshot["dictionaries"].items():
        if source not in schemas:
            raise ValueError("Dictionary source is not an inventoried physical table")
        for definition in result_records(result):
            key = (int(source[:4]), definition.get("TABLE_ID", definition.get("COLUMN_ID")))
            if key in definitions:
                raise ValueError("Ambiguous/duplicate dictionary field ID")
            definitions[key] = {**definition, "metadata_source": source}
    entries = []
    unused = set(definitions)
    family_coverage = {}
    for table in sorted(schemas):
        if not INDICATOR_TABLE.fullmatch(table) and table != REDS_TABLE:
            continue
        year = int(table[:4])
        redistricting = table == REDS_TABLE
        product = (
            "decennial_redistricting_pl94_171"
            if redistricting
            else "acs_detailed"
            if table.split("_")[-1].startswith("B")
            else "acs_collapsed"
        )
        geo_columns = [c for c in schemas[table] if c["column"] == "CENSUS_BLOCK_GROUP"]
        if len(geo_columns) != 1:
            raise ValueError(f"Missing exact geography key: {table}")
        covered = 0
        for physical in schemas[table]:
            column = physical["column"]
            if column == "CENSUS_BLOCK_GROUP":
                continue
            definition = definitions.get((year, column))
            verified = definition is not None
            if definition:
                # The dictionary must belong to the same product, not just share an ID.
                if redistricting != ("REDISTRICTING" in definition["metadata_source"]):
                    raise ValueError("Cross-product dictionary collision")
                unused.discard((year, column))
                covered += 1
            definition = definition or {}
            title = definition.get("TABLE_TITLE", definition.get("COLUMN_TOPIC", "")) or ""
            universe = definition.get("TABLE_UNIVERSE", definition.get("COLUMN_UNIVERSE", "")) or ""
            if redistricting and verified:
                kind = "census_count"
                path = [definition["FIELD_NAME"]]
            else:
                kind = {"Estimate": "estimate", "MarginOfError": "moe"}.get(
                    definition.get("FIELD_LEVEL_1"), "unknown"
                )
                path = [
                    value
                    for key, value in definition.items()
                    if key.startswith("FIELD_LEVEL")
                    and key not in {"FIELD_LEVEL_1", "FIELD_LEVEL_2", "FIELD_LEVEL_3"}
                    and value
                ]
            entry = {
                "id": f"{table}.{column}",
                "year": year,
                "year_meaning": "provider_release_year" if not redistricting else "census_year",
                "source_product": product,
                "source_product_basis": "dictionary naming and official Census ID conventions",
                "survey_interval": None,
                "table": table,
                "column": column,
                "data_type": physical["data_type"],
                "family": table.split("_")[-1] if not redistricting else "redistricting",
                "original_table_id": definition.get(
                    "TABLE_NUMBER", column[:4] if redistricting else None
                ),
                "title": title,
                "topic": definition.get("TABLE_TOPICS", definition.get("COLUMN_TOPIC", "")) or "",
                "universe": universe,
                "field_path": path,
                "estimate_kind": kind,
                "schema_verified": True,
                "semantic_verified": verified,
                "metadata_source": definition.get("metadata_source"),
                "aggregation": classify(title, universe, kind, verified),
            }
            entries.append(entry)
        family_coverage[table] = {
            "physical_fields": len(schemas[table]) - 1,
            "described_fields": covered,
        }
    if unused:
        raise ValueError(f"Dictionary definitions have no exact physical mapping: {len(unused)}")
    if len({e["id"] for e in entries}) != len(entries):
        raise ValueError("Duplicate catalog IDs")
    fips = {}
    for table, result in snapshot["fips"].items():
        year = str(int(table[:4]))
        required = {"STATE", "STATE_FIPS", "COUNTY_FIPS", "COUNTY", "CLASS_CODE"}
        if not required <= {c["column"] for c in schemas[table]}:
            raise ValueError("FIPS schema incomplete")
        fips[year] = {
            "table": table,
            "rows": result_records(result),
            "query_id": result["query_id"],
        }
    return {
        "format_version": 1,
        "database": snapshot["database"],
        "schema": snapshot["schema"],
        "captured_at_utc": snapshot["created_at_utc"],
        "sources": {
            "snapshot_path": str(snapshot_path),
            "snapshot_sha256": hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
            "schema_query_id": snapshot["columns"]["query_id"],
            "dictionary_query_ids": {k: v["query_id"] for k, v in snapshot["dictionaries"].items()},
            "acs_id_reference": ACS_SOURCE,
            "redistricting_reference": REDS_SOURCE,
            "state_reference": states,
        },
        "schemas": schemas,
        "entries": entries,
        "geography": fips,
        "coverage": {
            "indicator_tables": len(family_coverage),
            "physical_fields": len(entries),
            "described_fields": sum(e["semantic_verified"] for e in entries),
            "quarantined_fields": [e["id"] for e in entries if not e["semantic_verified"]],
            "by_table": family_coverage,
            "classification_counts": dict(Counter(e["aggregation"]["measure"] for e in entries)),
            "excluded_objects": sorted(set(schemas) - set(family_coverage)),
        },
    }


def write_catalog(catalog: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Compact JSON: all fields retained; no duplicate complete schema per indicator.
    path.write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")) + "\n")
