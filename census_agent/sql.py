"""Closed SQL language: canonical compiler + exact revalidation, never model SQL."""

from __future__ import annotations

import re
from dataclasses import dataclass

from census_agent.types import AgentIssue, GeoRequest
from census_catalog.catalog import Catalog
from census_catalog.geography import Geography, GeographyError


@dataclass(frozen=True)
class Scope:
    type: str
    key: str
    year: int
    label: str


def resolve_scope(geo: GeoRequest, year: int, geography: Geography) -> Scope:
    try:
        if geo.type == "cbg":
            info = geography.lookup_cbg(geo.name, year)
            return Scope(
                "cbg",
                info["cbg"],
                year,
                f"CBG {info['cbg']}, {info['county_name']}, {info['state_name']}",
            )
        if geo.type == "state":
            info = geography.resolve_state(geo.name, year)
            return Scope("state", info["STATE"], year, info["STATE_NAME"])
        if geo.type == "county":
            info = geography.resolve_county(geo.name, year, geo.state)
            state = geography.resolve_state(info["STATE_FIPS"], year)
            return Scope(
                "county",
                info["STATE_FIPS"] + info["COUNTY_FIPS"],
                year,
                f"{info['COUNTY']}, {state['STATE_NAME']}",
            )
        raise AgentIssue("Only CBG, county and state scopes are supported.", "unsupported")
    except GeographyError as exc:
        raise AgentIssue(str(exc)) from exc


@dataclass(frozen=True)
class QueryPlan:
    entry_id: str
    scope: Scope
    operation: str


@dataclass(frozen=True)
class ValidatedQuery:
    plan: QueryPlan
    sql: str
    params: tuple[str, ...]
    row_limit: int = 2


def compile_query(catalog: Catalog, plan: QueryPlan) -> ValidatedQuery:
    try:
        mapping = catalog.mapping(plan.entry_id)
    except (KeyError, ValueError) as exc:
        raise AgentIssue("Metric is not a verified catalog field.", "unsupported") from exc
    if not mapping["semantic_verified"] or mapping["year"] != plan.scope.year:
        raise AgentIssue("Metric or release is not verified.", "unsupported")
    geo = Geography(catalog.data)
    if plan.scope.type == "cbg":
        canonical = resolve_scope(GeoRequest("cbg", plan.scope.key), plan.scope.year, geo)
        predicate = '"CENSUS_BLOCK_GROUP" = %s'
    elif plan.scope.type == "county":
        if not re.fullmatch(r"[0-9]{5}", plan.scope.key):
            raise AgentIssue("Invalid county key.")
        canonical = resolve_scope(GeoRequest("county", plan.scope.key), plan.scope.year, geo)
        predicate = 'SUBSTR("CENSUS_BLOCK_GROUP", 1, 5) = %s'
    elif plan.scope.type == "state":
        if not re.fullmatch(r"[0-9]{2}", plan.scope.key):
            raise AgentIssue("Invalid state key.")
        canonical = resolve_scope(GeoRequest("state", plan.scope.key), plan.scope.year, geo)
        predicate = 'SUBSTR("CENSUS_BLOCK_GROUP", 1, 2) = %s'
    else:
        raise AgentIssue("Unrestricted geography is not allowed.", "unsupported")
    if canonical != plan.scope:
        raise AgentIssue("Geography does not match verified FIPS metadata.")
    col, table = mapping["quoted_column"], mapping["qualified_table"]
    invalid = f"{col} IS NULL OR {col} < 0"
    if plan.operation == "value" and plan.scope.type == "cbg":
        sql = (
            f'SELECT {col} AS "VALUE", 1 AS "ROWS_MATCHED", 1 AS "UNIQUE_CBGS", '
            f'CASE WHEN {invalid} THEN 1 ELSE 0 END AS "INVALID_VALUES" '
            f"FROM {table} WHERE {predicate} LIMIT 2"
        )
    elif (
        plan.operation == "sum"
        and mapping["aggregation"]["spatial_operation"] == "sum_disjoint_cbgs"
    ):
        sql = (
            f'SELECT SUM({col}) AS "VALUE", COUNT(*) AS "ROWS_MATCHED", '
            'COUNT(DISTINCT "CENSUS_BLOCK_GROUP") AS "UNIQUE_CBGS", '
            f'SUM(CASE WHEN {invalid} THEN 1 ELSE 0 END) AS "INVALID_VALUES" '
            f"FROM {table} WHERE {predicate} LIMIT 1"
        )
    else:
        raise AgentIssue(
            "This statistic cannot be aggregated at that geography. Specify one CBG; medians, ratios and MOEs cannot be summed.",
            "unsupported",
        )
    return ValidatedQuery(plan, sql, (plan.scope.key,))


def validate_query(catalog: Catalog, statement: ValidatedQuery) -> ValidatedQuery:
    """Regenerate the sole authorized statement from its typed plan at execution.

    Equality covers SQL text, parameters and result limit; no permissive SELECT
    regex, arbitrary function, second statement or table can pass this boundary.
    """
    if not isinstance(statement, ValidatedQuery):
        raise AgentIssue("Only validated compiled queries can execute.", "refused")
    expected = compile_query(catalog, statement.plan)
    if statement != expected:
        raise AgentIssue("SQL differs from its validated catalog plan.", "refused")
    return expected
