import pytest

from census_catalog.aggregation import (
    CountObservation,
    UnsupportedAggregation,
    classify,
    sum_counts,
)


def observation(entry, cbg="010010201001", value=12, **overrides):
    return CountObservation(
        **{
            "entry_id": entry["id"],
            "year": entry["year"],
            "source_product": entry["source_product"],
            "cbg": cbg,
            "value": value,
            **overrides,
        }
    )


def test_additive_count_of_disjoint_same_year_cbgs(catalog):
    entry = catalog.entries["2020_CBG_B01.B01001e1"]
    assert sum_counts(entry, [observation(entry), observation(entry, "010010201002", 5)]) == 17


@pytest.mark.parametrize(
    "identifier",
    [
        "2020_CBG_B01.B01002e1",
        "2020_CBG_B19.B19013e1",
        "2020_CBG_B01.B01001m1",
        "2020_CBG_B25.B25071e1",
        "2020_CBG_B01.B01002Ee1",
    ],
)
def test_nonadditive_or_undefined_statistics_cannot_sum(catalog, identifier):
    entry = catalog.entries[identifier]
    with pytest.raises(UnsupportedAggregation):
        sum_counts(entry, [observation(entry)])


@pytest.mark.parametrize(
    "overrides",
    [
        {"year": 2019},
        {"source_product": "decennial_redistricting_pl94_171"},
        {"entry_id": "different-field"},
        {"cbg": "01001"},
        {"value": -666666666},
        {"value": None},
        {"value": float("nan")},
        {"value": float("inf")},
        {"value": True},
    ],
)
def test_invalid_mixed_or_missing_observations_rejected(catalog, overrides):
    entry = catalog.entries["2020_CBG_B01.B01001e1"]
    with pytest.raises(UnsupportedAggregation):
        sum_counts(entry, [observation(entry, **overrides)])


def test_duplicate_geography_and_empty_data_are_not_valid_counts(catalog):
    entry = catalog.entries["2020_CBG_B01.B01001e1"]
    with pytest.raises(UnsupportedAggregation):
        sum_counts(entry, [observation(entry), observation(entry)])
    with pytest.raises(UnsupportedAggregation):
        sum_counts(entry, [])


def test_mean_ratio_amount_and_unknown_units_are_unsupported():
    for title in (
        "Mean Household Size",
        "Per Capita Income",
        "Percentage Of Income",
        "Gini Index",
        "Aggregate Travel Time",
    ):
        assert (
            classify(title, "Total population", "estimate", True)["spatial_operation"]
            == "unsupported"
        )
    assert (
        classify("Mystery", "Unknown units", "estimate", True)["spatial_operation"] == "unsupported"
    )


def test_numeric_overflow_is_an_explicit_policy_error(catalog):
    entry = catalog.entries["2020_CBG_B01.B01001e1"]
    with pytest.raises(UnsupportedAggregation, match="numeric bounds"):
        sum_counts(entry, [observation(entry, value=10**1000)])
