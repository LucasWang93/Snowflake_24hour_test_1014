# Phase 1 — Data grounding and semantic catalog

Phase 1 only: implemented a local semantic catalog, retrieval, geography utilities
and guarded aggregation. No UI, agent, model calls, infrastructure reconfiguration,
repeated table counts or full statistical-data scans were performed.

## Acceptance results

| Requirement | Actual evidence | Result |
| --- | --- | --- |
| All indicator families | 59 physical statistical tables: 29 B/C families in each release plus 2020 redistricting | Pass |
| Exact schema mappings | 16,878 indicator columns reconciled against live INFORMATION_SCHEMA.COLUMNS | Pass |
| All supplied definitions | 16,582 dictionary rows mapped exactly; no unused or ambiguous IDs | Pass |
| Required natural-language searches | 5/5 predefined queries return relevant verified families; targeted returned columns execute | Pass |
| Geography/year | 2019/2020 FIPS dictionaries; state reference; real joins for both releases and redistricting | Pass for tested cases |
| Aggregation safety | Counts guarded by field/year/product/unique CBG; medians, ratios, MOEs and unsupported units rejected | Pass |
| Tests/evidence | Deterministic tests and nine opt-in real integration tests; artifacts linked below | Verified |

**Metadata gap:** 296 physical columns (148 per release),
such as `B01002Ee1`, have no supplied dictionary definition. Their exact schema is
recorded, semantics remain unknown, aggregation is unsupported, and they are
excluded from search. No alias, race label or statistical meaning was invented.
All discoverable families and all supplied descriptions are covered; complete
semantic coverage of those missing definitions is not claimed.

## Deliverables and usage

- `data/semantic_catalog.json`: machine-readable catalog, complete physical schemas,
  metadata provenance/query IDs, release/source/universe, estimate/MOE class,
  aggregation policies, FIPS mappings and coverage/quarantine audit.
- `census_catalog/catalog.py`: offline inverted-index BM25 with generic synonyms,
  title/topic weighting, estimate-first defaults, definition diversity and filters.
  Returned mappings include fully qualified quoted table, exact column, verified
  schema context (CBG key, selected field, paired estimate/MOE when available),
  topic, universe, year, source family, field path and geography association.
- `census_catalog/geography.py`: parse CBG, resolve state/county and look up FIPS;
  reject ambiguous county names and lossy numeric identifiers. A prefix match is
  not proof of CBG membership; that flag remains false without a real data check.
- `census_catalog/aggregation.py`: statistical policy and executable `sum_counts`.
- `scripts/collect_phase1_metadata.py`: explicit metadata-only refresh. It reuses
  the working connection loader, saves query IDs, and suspends the warehouse.

From the repository root, offline commands:

```bash
.venv/bin/python -m census_catalog build
.venv/bin/python -m census_catalog search "population" --year 2020
.venv/bin/python -m census_catalog search "median age" --year 2019
.venv/bin/python -m census_catalog search "household income" --year 2020
.venv/bin/python -m census_catalog geography 010010201001 --year 2020
bash scripts/verify.sh
```

Build uses captured metadata; it does not connect remotely. Python API:
`Catalog.load().search(...)`, `Catalog.table_schema(...)`,
`Geography(catalog.data).resolve_county("Washington County", 2020, "Alabama")`.
Read-only, paid remote checks are opt-in:

```bash
.venv/bin/python -m scripts.collect_phase1_metadata  # metadata refresh only, if needed
.venv/bin/python -m pytest -q tests/test_phase1_live.py --snowflake-live
```

Ordinary verification skips the nine live tests; a SKIP is not integration success.
The separate live run actually passed nine tests using ten bounded SQL queries:
five retrieved fields, three year/product-specific FIPS/geography joins, and a
raw two-CBG count versus SQL SUM comparison. The observed sum was
1941.0 for those two CBGs, not a national population total.
The connector emitted one third-party X509 deprecation warning; no infrastructure
package upgrade was performed.

## Measured search examples

2020 filter, five results per query; first mappings and single local timings:

| Query | First physical mapping | Search ms |
| --- | --- | --- |
| population | `2020_CBG_B01` / `"B01003e1"` | 58.391 |
| median age | `2020_CBG_B01` / `"B01002e1"` | 2.746 |
| household income | `2020_CBG_B19` / `"B19001e1"` | 13.368 |
| education | `2020_CBG_B15` / `"B15003e1"` | 11.261 |
| employment | `2020_CBG_B23` / `"B23025e1"` | 18.505 |

Index/load: 3.617 seconds in this run. These are one-shot local
observations on five explicit acceptance queries, not p95, throughput, calibrated
confidence or general search accuracy. Full ranked examples are in
`docs/phase1_search_results.json`. Early retrieval surfaced incidental SNAP/person
mentions and allocation fields; generic literal/title weighting and definition
diversification corrected the recorded acceptance cases without hardcoded field IDs.

Final local verification: `bash scripts/verify.sh` exited 0; Ruff formatting/lint
passed, **58 tests passed and nine live tests were explicitly skipped** in this
normal offline run. Those nine were separately executed against Snowflake and
passed. Optional ShellCheck remains unavailable/SKIP. Existing infrastructure and
exploration-artifact hashes match `docs/phase1_preservation.json`; `.env` remains
ignored, untracked and owner-only. Git whitespace checks passed.

## Statistical and geographic limits

- B/C source families are ACS base/detailed versus collapsed tables, based on
  supplied dictionaries and [official Census ID conventions](https://www.census.gov/programs-surveys/acs/data/data-tables/table-ids-explained.html).
  Their physical prefix year is preserved as provider release year. The exact
  provider survey interval is not proven by this metadata and remains null;
  do not claim these are single-year population measurements.
- The 2020 redistricting source is kept separate, with its own universe/count
  definitions and census year. See [Census redistricting documentation](https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html).
- State names/abbreviations come from the [Census state reference](https://www2.census.gov/geo/docs/reference/state.txt);
  county names/codes come from year-specific Snowflake FIPS metadata. Null provider
  territory abbreviations are preserved, not silently replaced in original data.
- Only one metric across distinct full CBGs in the same product/release can be
  summed. Duplicate CBGs, mixed fields/years/products, missing/negative/nonfinite
  values, overflow, medians, means, ratios, indexes and MOEs fail explicitly.
- Summing categories, nationwide coverage, temporal comparisons, weighted means,
  ratio reconstruction and aggregate MOE formulas are not implemented. MOEs need
  a justified covariance/variance method; see [Census VRE guidance](https://www.census.gov/programs-surveys/acs/data/variance-tables.html).
- Classification deliberately blocks even some valid count distributions with
  percentage-bearing titles and aggregate amounts whose units were not proven.
  Catalog coverage is broader than supported aggregation; conservative blocking
  is preferable to unsupported statistical inference.
- All 73 object schemas are retained. Geometry, patterns, dictionaries and the
  two derived rental views are listed as ancillary/excluded from indicator search:
  no matching indicator dictionary for those derived views was fabricated.
- Real geography checks covered two Alabama CBGs in each tested product/release;
  they do not prove global uniqueness, join coverage, national/territory scope or
  historical boundary crosswalks. County matches require exact names or GEOIDs;
  city/place geocoding is not implemented.

## Provenance and preservation

`docs/phase1_metadata.json` contains only schema and dictionary/FIPS queries.
`docs/phase1_state_reference.json` records the official reference URL/time/hash.
`docs/phase1_integration_results.json` records real SQL, parameters, rows, query IDs,
test outcomes and cleanup. The final warehouse state is **SUSPENDED**;
ALTER query ID `01c7ba60-3204-bd57-0008-3d1a000176de`.
Existing environment configuration, connection scripts and original exploration
artifacts were preserved; nonsecret preservation hashes are recorded in
`docs/phase1_preservation.json`. No credentials were placed in catalog/report artifacts.
No commit, push or Phase 2 work is included.

Repository preflight ran and exited 2 because whole-challenge templates and
uncommitted local changes remain pending. It reran Ruff/tests successfully and
reported no obvious secret-file risk. This is not a Phase 1 test failure and is
not presented as full homework delivery readiness.
