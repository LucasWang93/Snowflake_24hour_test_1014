"""Offline tests against captured metadata plus synthetic malformed cases."""

import copy
import json
from pathlib import Path

import pytest

from census_catalog.build import build_catalog
from census_catalog.catalog import Catalog

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("query", "expected_family"),
    [
        ("population", "B01"),
        ("median age", "B01"),
        ("household income", "B19"),
        ("education", "B15"),
        ("employment", "B23"),
    ],
)
def test_required_searches_return_grounded_relevant_fields(catalog, query, expected_family):
    results = catalog.search(query, year=2020, top_k=5)
    assert any(row["family"] == expected_family for row in results)
    for row in results:
        assert row["schema_verified"] and row["semantic_verified"]
        assert (row["table"], row["column"]) in catalog.physical
        assert row["year"] == row["geography"]["year"] == 2020
        assert row["quoted_column"] == '"' + row["column"] + '"'
        assert any(c["column"] == row["column"] for c in row["physical_schema"])


def test_all_discovered_families_and_dictionary_definitions_are_accounted_for(catalog):
    c = catalog.data["coverage"]
    snapshot = json.loads((ROOT / "docs/phase1_metadata.json").read_text())
    assert c["indicator_tables"] == 59
    assert c["physical_fields"] == 16878
    assert c["described_fields"] == sum(len(d["rows"]) for d in snapshot["dictionaries"].values())
    assert all(t["described_fields"] > 0 for t in c["by_table"].values())
    assert c["described_fields"] + len(c["quarantined_fields"]) == c["physical_fields"]


def test_unmatched_variant_is_recorded_and_not_searchable(catalog):
    ident = "2020_CBG_B01.B01002Ee1"
    assert ident in catalog.data["coverage"]["quarantined_fields"]
    assert not catalog.entries[ident]["semantic_verified"]
    assert ident not in catalog.documents
    assert catalog.entries[ident]["aggregation"]["spatial_operation"] == "unsupported"


def test_exact_case_and_paired_moe_are_preserved(catalog):
    row = catalog.mapping("2020_CBG_B01.B01001e1")
    assert {c["column"] for c in row["physical_schema"]} == {
        "CENSUS_BLOCK_GROUP",
        "B01001e1",
        "B01001m1",
    }
    with pytest.raises(KeyError):
        catalog.mapping("2020_CBG_B01.B01001E1")


def test_rejects_catalog_schema_drift(catalog):
    malformed = copy.deepcopy(catalog.data)
    malformed["entries"][0]["column"] = "InventedColumn"
    with pytest.raises(ValueError, match="exact physical schema"):
        Catalog(malformed)


def test_rebuild_is_deterministic(catalog):
    rebuilt = build_catalog(
        ROOT / "docs/phase1_metadata.json",
        ROOT / "docs/snowflake_evidence.json",
        ROOT / "docs/phase1_state_reference.json",
    )
    assert rebuilt["entries"] == catalog.data["entries"]
    assert rebuilt["schemas"] == catalog.data["schemas"]


def test_year_in_question_filters_results(catalog):
    assert all(r["year"] == 2019 for r in catalog.search("2019 population"))
    with pytest.raises(ValueError, match="conflicts"):
        catalog.search("2019 population", year=2020)


def test_product_filter_preserves_decennial_counts(catalog):
    results = catalog.search("population", source_product="decennial_redistricting_pl94_171")
    assert results and all(r["estimate_kind"] == "census_count" for r in results)
    assert all(r["source_product"] == "decennial_redistricting_pl94_171" for r in results)


def test_median_and_moe_keep_distinct_definitions(catalog):
    age = catalog.search("median age", year=2020)[0]
    assert age["column"] == "B01002e1" and age["aggregation"]["measure"] == "median"
    moe = catalog.search("population margin of error", year=2020)
    assert moe and all(r["estimate_kind"] == "moe" for r in moe)


def test_empty_unrelated_and_bounded_search(catalog):
    assert catalog.search("") == []
    assert catalog.search("nonexistent-zqxstatistics") == []
    with pytest.raises(ValueError):
        catalog.search("population", top_k=0)
    with pytest.raises(ValueError):
        catalog.search("x" * 2001)


def test_people_synonym_and_deterministic_rank(catalog):
    assert catalog.search("how many people", year=2020)[0]["family"] == "B01"
    assert catalog.search("employment") == catalog.search("employment")
