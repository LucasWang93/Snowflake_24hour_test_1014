import pytest

from census_catalog.geography import Geography, GeographyError, parse_cbg


@pytest.fixture(scope="module")
def geography(catalog):
    return Geography(catalog.data)


@pytest.mark.parametrize("year", [2019, 2020])
def test_cbg_year_county_and_leading_zeros(geography, year):
    row = geography.lookup_cbg("010010201001", year)
    assert (row["state_fips"], row["county_fips"], row["tract"]) == ("01", "001", "020100")
    assert row["state_name"] == "Alabama" and row["county_name"] == "Autauga County"
    assert row["year"] == year and not row["cbg_membership_verified"]


@pytest.mark.parametrize(
    "value",
    [10010201001, "10010201001", "0100102010011", "01001020100x", "０１００１０２０１００１"],
)
def test_invalid_or_lossy_cbg_is_rejected(value):
    with pytest.raises(GeographyError):
        parse_cbg(value)


def test_ambiguous_county_requires_state(geography):
    with pytest.raises(GeographyError, match="ambiguous"):
        geography.resolve_county("Washington County", 2020)
    row = geography.resolve_county("Washington County", 2020, "Alabama")
    assert row["STATE_FIPS"] == "01"


def test_state_names_abbreviations_and_fips(geography):
    assert geography.resolve_state("Alabama", 2020) == geography.resolve_state("AL", 2020)
    assert geography.resolve_state("01", 2020)["STATE_NAME"] == "Alabama"


def test_territory_null_provider_abbreviation_preserved(geography):
    row = geography.lookup_cbg("780100001001", 2020)
    assert row["provider_state_abbreviation"] is None
    assert row["state_abbreviation"] == "VI"
    assert not row["cbg_membership_verified"]


def test_unknown_year_and_county_fail_closed(geography):
    with pytest.raises(GeographyError):
        geography.lookup_cbg("010010201001", 2021)
    with pytest.raises(GeographyError):
        geography.lookup_cbg("019990201001", 2020)
