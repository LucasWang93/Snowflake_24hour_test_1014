"""Opt-in targeted real-data integration; no COUNT(*) or full indicator scans."""

import math

import pytest

from census_catalog.aggregation import CountObservation, sum_counts
from census_catalog.geography import Geography
from scripts.snowflake_probe import quote_identifier

pytestmark = pytest.mark.snowflake_live
CBGS = ("010010201001", "010010201002")


@pytest.mark.parametrize(
    "query", ["population", "median age", "household income", "education", "employment"]
)
def test_retrieved_field_executes_exact_identifier(catalog, live_session, query):
    mapping = catalog.search(query, year=2020, top_k=1)[0]
    sql = (
        f'SELECT "CENSUS_BLOCK_GROUP", {mapping["quoted_column"]} '
        f'FROM {mapping["qualified_table"]} WHERE "CENSUS_BLOCK_GROUP" IN (%s, %s) '
        'ORDER BY "CENSUS_BLOCK_GROUP" LIMIT 2'
    )
    result = live_session(sql, CBGS)
    assert result["columns"] == ["CENSUS_BLOCK_GROUP", mapping["column"]]
    assert len(result["rows"]) == 2
    assert all(
        row[0] in CBGS and row[1] is not None and math.isfinite(float(row[1]))
        for row in result["rows"]
    )


@pytest.mark.parametrize("table", ["2019_CBG_B01", "2020_CBG_B01", "2020_REDISTRICTING_CBG_DATA"])
def test_geography_real_data_join_matches_offline_mapping(catalog, live_session, table):
    year = int(table[:4])
    prefix = ".".join(
        quote_identifier(v) for v in (catalog.data["database"], catalog.data["schema"])
    )
    fips = quote_identifier(catalog.data["geography"][str(year)]["table"])
    geographic = (
        f"{year}_REDISTRICTING_METADATA_CBG_GEOGRAPHIC_DATA"
        if "REDISTRICTING" in table
        else f"{year}_METADATA_CBG_GEOGRAPHIC_DATA"
    )
    assert "CENSUS_BLOCK_GROUP" in {c["column"] for c in catalog.table_schema(geographic)}
    sql = (
        'SELECT d."CENSUS_BLOCK_GROUP", f."STATE", f."STATE_FIPS", f."COUNTY_FIPS", f."COUNTY", g."CENSUS_BLOCK_GROUP" '
        f"FROM {prefix}.{quote_identifier(table)} d "
        f'JOIN {prefix}.{fips} f ON SUBSTR(d."CENSUS_BLOCK_GROUP", 1, 2) = f."STATE_FIPS" '
        'AND SUBSTR(d."CENSUS_BLOCK_GROUP", 3, 3) = f."COUNTY_FIPS" '
        f'JOIN {prefix}.{quote_identifier(geographic)} g ON d."CENSUS_BLOCK_GROUP" = g."CENSUS_BLOCK_GROUP" '
        'WHERE d."CENSUS_BLOCK_GROUP" IN (%s, %s) ORDER BY d."CENSUS_BLOCK_GROUP" LIMIT 2'
    )
    result = live_session(sql, CBGS)
    assert len(result["rows"]) == 2
    for cbg, state, state_fips, county_fips, county_name, geo_cbg in result["rows"]:
        offline = Geography(catalog.data).lookup_cbg(cbg, year)
        assert (state, state_fips, county_fips, county_name, geo_cbg) == (
            offline["provider_state_abbreviation"],
            offline["state_fips"],
            offline["county_fips"],
            offline["county_name"],
            cbg,
        )


def test_safe_count_sum_matches_bounded_real_sql(catalog, live_session):
    entry = catalog.mapping("2020_CBG_B01.B01001e1")
    raw = live_session(
        f'SELECT "CENSUS_BLOCK_GROUP", {entry["quoted_column"]} FROM {entry["qualified_table"]} '
        'WHERE "CENSUS_BLOCK_GROUP" IN (%s, %s) ORDER BY "CENSUS_BLOCK_GROUP" LIMIT 2',
        CBGS,
    )
    assert len(raw["rows"]) == 2
    observations = [
        CountObservation(entry["id"], entry["year"], entry["source_product"], cbg, value)
        for cbg, value in raw["rows"]
    ]
    observed = sum_counts(entry, observations)
    actual = live_session(
        f"SELECT SUM({entry['quoted_column']}) FROM {entry['qualified_table']} "
        'WHERE "CENSUS_BLOCK_GROUP" IN (%s, %s)',
        CBGS,
    )
    assert observed == actual["rows"][0][0]
