"""Conservative statistical classification and executable aggregation guards."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


class UnsupportedAggregation(ValueError):
    """Requested aggregation is not justified by the catalog."""


def classify(title: str, universe: str, kind: str, verified: bool) -> dict[str, str]:
    if not verified:
        measure, unit = "unknown", "unknown"
    elif kind == "moe":
        measure, unit = "margin_of_error", "same_as_estimate"
    elif re.search(r"\bmedian\b", title, re.I):
        measure, unit = "median", "not_additive"
    elif re.search(r"\b(per capita|mean|average)\b", title, re.I):
        measure, unit = "mean_or_per_capita", "not_additive"
    elif re.search(r"\b(percent(?:age)?|ratio|rate|gini|index)\b", title, re.I):
        measure, unit = "ratio_or_index", "not_additive"
    elif re.search(r"\baggregate\b", title, re.I):
        # Amounts/durations may be additive, but this phase does not prove their units.
        measure, unit = "aggregate_amount_unverified", "unknown"
    else:
        unit = "unknown"
        for pattern, candidate in (
            (r"housing units", "housing_units"),
            (r"households?", "households"),
            (r"famil(?:y|ies)", "families"),
            (r"population|persons?|people|workers|children|grandparents", "persons"),
        ):
            if re.search(pattern, universe, re.I):
                unit = candidate
                break
        measure = "additive_count" if unit != "unknown" else "unknown"
    return {
        "measure": measure,
        "unit": unit,
        "spatial_operation": "sum_disjoint_cbgs" if measure == "additive_count" else "unsupported",
        "temporal_operation": "unsupported",
        "category_operation": "unsupported_without_disjointness_proof",
    }


@dataclass(frozen=True)
class CountObservation:
    entry_id: str
    year: int
    source_product: str
    cbg: str
    value: int | float


def sum_counts(entry: Mapping[str, Any], observations: Sequence[CountObservation]) -> float:
    """Sum one verified count across unique CBGs in the same release/product.

    This does not infer nationwide coverage, combine overlapping categories, sum
    across years, or manufacture aggregate MOEs. Missing/suppression sentinels fail.
    """
    if (
        not entry.get("semantic_verified")
        or not entry.get("schema_verified")
        or entry["aggregation"]["spatial_operation"] != "sum_disjoint_cbgs"
    ):
        raise UnsupportedAggregation("Only verified additive counts can be spatially summed")
    if not observations:
        raise UnsupportedAggregation("No observations; empty data is not a verified zero")
    seen = set()
    values = []
    for row in observations:
        if (row.entry_id, row.year, row.source_product) != (
            entry["id"],
            entry["year"],
            entry["source_product"],
        ):
            raise UnsupportedAggregation("Cannot mix fields, years or source products")
        if not isinstance(row.cbg, str) or not re.fullmatch(r"[0-9]{12}", row.cbg):
            raise UnsupportedAggregation("Only full 12-digit CBG identifiers are supported")
        if row.cbg in seen:
            raise UnsupportedAggregation("Repeated CBG: join duplication or overlapping geography")
        if isinstance(row.value, bool) or not isinstance(row.value, (int, float)) or row.value < 0:
            raise UnsupportedAggregation("Count must be finite, nonnegative and nonmissing")
        try:
            numeric = float(row.value)
        except (OverflowError, ValueError) as exc:
            raise UnsupportedAggregation("Count exceeds supported numeric bounds") from exc
        if not math.isfinite(numeric):
            raise UnsupportedAggregation("Count must be finite")
        seen.add(row.cbg)
        values.append(numeric)
    try:
        total = math.fsum(values)
    except OverflowError as exc:
        raise UnsupportedAggregation("Aggregate exceeds supported numeric bounds") from exc
    if not math.isfinite(total):
        raise UnsupportedAggregation("Aggregate exceeds supported numeric bounds")
    return total
