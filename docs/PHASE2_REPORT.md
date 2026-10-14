# Phase 2 — Core conversational agent

Completed 2026-10-14. Official five-page assignment PDF reconciled before core
implementation: original 23 IDs retained, seven added (30 total); Cortex is a user
choice, not a PDF mandate. See [PDF_RECONCILIATION.md](PDF_RECONCILIATION.md).
Phase 1 and its verified evidence are preserved. No Phase 3, public deployment,
reviewer-sharing change or submission email was performed. The user subsequently authorized development commits/pushes; see
DEVELOPMENT_VERSIONS.md for GitHub checkpoints.

## Implemented modules

| Module | Responsibility |
| --- | --- |
| `census_agent/types.py` | Strict bounded intent, explicit resolved/pending conversation state, deadline and response diagnostics |
| `census_agent/planning.py` | Cortex intent/context, dynamic whole-catalog retrieval, exact definition/category checks, clarification and catalog-ID choice |
| `census_agent/sql.py` | Verified FIPS scopes, canonical typed SQL compiler, exact revalidation of SQL/params/result bound |
| `census_agent/backend.py` | Existing connector/config loader, bounded Cortex COMPLETE, visible permission audit, SQL execution, sanitized errors and suspension checks |
| `census_agent/agent.py` | Single pipeline, duplicate/missing/result validation, deterministic grounded answers, comparison and failure recovery |
| `census_agent/__main__.py` | Local one-shot/interactive CLI, progress stages, reset/quit and optional JSON diagnostics |

Reuses `Catalog`, `Geography` and catalog aggregation classifications. No application
dependency or infrastructure configuration changes. Cortex default is llama3.3-70b;
the existing environment default remains intact. At most two model calls and two
geographic data queries per turn, zero application retries. Models return semantic
JSON/field IDs only; executable SQL and answer numbers are never model-generated.

## Commands actually run

- `.venv/bin/python -m pytest -q tests/phase2/test_core.py`: **58 passed**.
- `.venv/bin/ruff format census_agent tests/phase2` and `ruff check`: passed.
- `bash scripts/verify.sh`: **116 passed / 25 explicitly skipped**, Ruff pass, exit 0.
  The skips are nine prior Phase 1 and sixteen opt-in Phase 2 live tests, not passes.
- `.venv/bin/python -m census_agent --help`: exit 0.
- CLI `--question 'DROP TABLE test' --json`: safe refusal, no model/data calls,
  exit 2 (the CLI's intentional clarification/refusal status).
- `.venv/bin/python -m pip check`: exit 0; no broken requirements.
- Git whitespace, documentation traceability and preservation checks: recorded in
  `phase2_documentation_audit.json` / `phase2_preservation.json`.
- Targeted live pytest executed by Slurm jobs **2847474**, **2847509**, **2847520**, **2847530**;
  durable script, logs, job ID and code manifest in each `slurm_runs/phase2_core_vN/`.
  No full inventory scan or Cortex availability sweep was repeated.
- Pre-commit `bash scripts/preflight.sh`: exit 2, verification passed; remaining delivery
  checklist items and not-yet-committed checkpoint work are incomplete, not test failures.

Final live pytest: **16 passed**, Slurm **COMPLETED / exit 0:0**.
Final actual live test status is in `../slurm_runs/phase2_core_v4/stdout.log` and
`results.json`, collected 2026-10-14T18:03:56.232711+00:00 through 2026-10-14T18:06:11.938420+00:00.
Six golden questions cover five families (B01, B19, B15, B23, B25). Developer-written
reference SQL selects the independently specified verified golden column; county
references use CBG LIKE while agent SQL uses SUBSTR. Numeric tolerance is relative
1e-12 / absolute 1e-9. These are development acceptance cases, not a held-out accuracy
benchmark, nationwide coverage proof or production SLA.

## Actual real-data answers and SQL evidence

All six questions explicitly select **ACS provider release 2020**. Population,
education, employment and housing use Autauga County, Alabama (FIPS 01001).
Median age and median household income use CBG 010010201001. Education explicitly
means age 25+ with highest attainment bachelor-only, not bachelor-or-higher.

| Question | Selected physical field | Actual value | E2E seconds | Agent data query ID |
| --- | --- | --- | --- | --- |
| population | 2020_CBG_B01.B01003e1 | 55,639 | 14.4261 | 01c7babc-3204-bb79-0008-3d1a00015bc2 |
| median_age | 2020_CBG_B01.B01002e1 | 46.2 | 5.7881 | 01c7babc-3204-bd12-0008-3d1a000169da |
| median_income | 2020_CBG_B19.B19013e1 | 39,167 | 6.7031 | 01c7babc-3204-bd10-0008-3d1a0002e01a |
| education | 2020_CBG_B15.B15003e22 | 6,320 | 6.6924 | 01c7babc-3204-bd57-0008-3d1a00017a2a |
| employment | 2020_CBG_B23.B23025e4 | 24,580 | 9.3186 | 01c7babc-3204-bb79-0008-3d1a00015bda |
| housing | 2020_CBG_B25.B25001e1 | 23,697 | 6.5010 | 01c7babc-3204-bda9-0008-3d1a0002a07e |

Full natural-language questions, answer text, intent, source/universe/year, generated
SQL/params, result numbers, Cortex query IDs/token counts, data query IDs, independent
reference outputs/query IDs and cleanup are preserved in the final result artifact.
Answers label ACS estimates, unverified survey interval, incomplete independent
coverage validation and missing aggregate MOE. Published medians are CBG values.

Example generated population SQL (parameter `%s` bound to `01001`):
```sql
SELECT SUM("B01003e1") AS "VALUE", COUNT(*) AS "ROWS_MATCHED", COUNT(DISTINCT "CENSUS_BLOCK_GROUP") AS "UNIQUE_CBGS", SUM(CASE WHEN "B01003e1" IS NULL OR "B01003e1" < 0 THEN 1 ELSE 0 END) AS "INVALID_VALUES" FROM "US_OPEN_CENSUS_DATA_NEIGHBORHOOD_INSIGHTS_FREE_DATASET"."PUBLIC"."2020_CBG_B01" WHERE SUBSTR("CENSUS_BLOCK_GROUP", 1, 5) = %s LIMIT 1
```
Independent reference SQL (bound parameter `01001%`):
```sql
SELECT SUM("B01003e1")
FROM "US_OPEN_CENSUS_DATA_NEIGHBORHOOD_INSIGHTS_FREE_DATASET"."PUBLIC"."2020_CBG_B01"
WHERE "CENSUS_BLOCK_GROUP" LIKE %s
```
For a published CBG median the compiler selects that field with an exact bound CBG
key and LIMIT 2; it never averages or sums medians. Returned duplicate rows, invalid
values or empty scopes suppress answers. Comparison differences are descriptive,
not significance claims.

## Multi-turn results

| Turn | Actual user question | Result | E2E seconds |
| --- | --- | --- | --- |
| conversation1/initial | Using ACS 2020, what is the total population of Autauga County, Alabama? | answered: 01001=55,639 | 8.4386 |
| conversation1/year | And in 2019? | answered: 01001=55,380 | 5.6646 |
| conversation1/compare | Compare with Baldwin County, Alabama. | answered: 01001=55,380, 01003=212,830 | 4.6116 |
| conversation2/initial | Median age for Census block group 010010201001, ACS 2020? | answered: 010010201001=46.2 | 9.8099 |
| conversation2/metric | What about median household income? | answered: 010010201001=39,167 | 8.1293 |
| conversation2/geography | For Census block group 010010201002 instead? | answered: 010010201002=70,699 | 6.0598 |
| conversation3/missing_geo | Using ACS release 2020, how many civilians are employed? | clarification: Please specify a state, county (with state if ambiguous), or 12-digit Census block group. | 3.2717 |
| conversation3/clarification | Autauga County, Alabama. | answered: 01001=24,580 | 8.8040 |
| conversation3/metric | What about people aged 25 years and over whose highest educational attainment is a bachelor's degree only? | answered: 01001=6,320 | 6.5315 |

Scenario 1 inherits geography/metric while changing release, then adds a comparison.
Scenario 2 changes metric and then CBG. Scenario 3 resolves pending missing geography
and changes category/metric. Offline tests also cover reset, independent state,
ambiguous comparison pronouns and preserving successful context after service errors.

## SQL security and failure evidence

Backend revalidation regenerates the sole allowed statement from its verified typed
plan and compares complete SQL, bound parameters and row limit. Offline adversarial
cases prove DROP/DELETE/COPY/ALTER, multiple statements, system-schema/functions,
UNION, Cortex-in-data-SQL, unknown catalog IDs, raw strings and changed parameters/
limits cannot reach a connection/cursor. Live backend rejection checks a tampered
statement without executing it. SQL policy is not a regex or model instruction.

Non-additive county sums (median age/income, MOE and ratio-classified fields) are
blocked; counts retain distinct-CBG/missing-value guards. Live negative questions
cover off-topic weather, SQL injection, ambiguous bachelor's attainment, unsupported
county median, unavailable year and nonexistent IQ metric. No negative case reports
statistics or executes successful data SQL. Cortex/Snowflake outages, malformed
intent and bad/empty rows use explicitly labeled mocks in offline tests.

Real failures are retained: NONE-secondary-mode pilot could not access data
(`phase2_pilot_failure.json`); an actual Cortex timeout returned a safe error
(`phase2_timeout_case.json`). First batch: 13 passed / 2 failed due bachelor-only vs
bachelor-or-higher substitution. Second: 15 passed / 1 failed due an empty array
instead of filter object in a follow-up. Third: 15 passed / 1 failed when a category follow-up did not inherit the established
count. Corrected exact category constraints,
clarification, canonical filter serialization and harmless empty-array normalization;
nonempty invalid arrays remain rejected. A narrowly defined category-only follow-up
inherits the established count; generic income or explicitly different statistics
still clarify. No failed run was rewritten as successful.

## Latency, permissions and warehouse

Final 21 measured turns: 0.2299–14.4261s including cleanup.
Answered turns: 4.6116–14.4261s; median 6.6978s,
nearest-rank sample p95 14.4261s.
First request includes connection/permission initialization; catalog startup occurs
before `ask` timing. CLI loading cost and sample/cold sensitivity prevent an SLA
claim. No concurrent throughput or Snowflake-credit cost was measured. Token usage
is available per successful Cortex call; it is not a dollar/credit-cost measurement.

Data/model timeouts are capped at 15s/20s, shared request budget 50s with finite
network/login/queue limits and reserved cleanup; no unbounded model/query retries.
CLI progress provides stage feedback. Suspension uses ALTER followed by at most
three state checks within a bounded check budget. Per-turn confirmed suspension:
21/21; final fixture confirmed SUSPENDED=True.
Any unconfirmed cleanup remains visible in answer diagnostics, never silently ignored.

Effective primary role PUBLIC, secondary mode ALL; visible grants and actual data
access in `phase2_permissions.json`, `phase2_permission_access_check.json` and final
live artifact. NONE denied access; ALL preserves the existing direct-user grants.
Snowflake documents that direct-user privileges are considered with secondary ALL
([access control overview](https://docs.snowflake.com/en/user-guide/security-access-control-overview)).
Grant visibility is limited, and PUBLIC/user rights are broader than application
SQL: **no least-privilege claim**, no GRANT/role provisioning changes. Credentials
remain ignored/untracked/owner-only; no values are in prompts or documented artifacts.

## Hardening review and limitations

| Severity | Finding / disposition |
| --- | --- |
| P1 fixed | Wrong educational universe in first run; exact category/universe guard and regression tests |
| P1 fixed | Filter serialization mismatch in second run; canonical objects plus empty-only normalization |
| P1 fixed | Filtered category follow-up lost count kind; explicit bounded inheritance rule and regression |
| P1 fixed | NONE mode broke existing access; preserve ALL and record visible effective permissions |
| P2 handled | Suspension state may be transitional; bounded checks retain observed state and surface failure |
| P2 core limit / deployment prerequisite | Broad Snowflake user rights; canonical SQL constrains this CLI, restricted hosted identity still needs review |
| P2 core limit / deployment prerequisite | Synchronous backend is not safe for concurrent sharing; isolate backend/state per session or serialize |
| P2 | Candidate retrieval is dynamic but bounded lexical search; model semantics may still select an incorrect plausible field outside tested cases |
| P2 | 296 undefined columns, unknown ACS survey interval, unsupported city/place/crosswalk/national coverage guarantees |

Supported scope: one verified published indicator, release 2019/2020, ACS or 2020
redistricting product, CBG/county/state, at most two comparison entities and published
cell filters. No general cross-table calculations, derived rates, cross-year
calculations, category totals without disjointness proof, aggregate median/mean/MOE,
or unrestricted SQL. Unsupported scope clarifies/refuses. Metadata coverage does
not mean every natural-language question is answerable. Model/connector latency can
fail despite bounded calls; genuine timeout evidence is preserved.

Outstanding official delivery: public UI/deployment and clean reviewer-browser
verification; comprehensive held-out/end-to-end deployment/security evaluation;
final README and four-topic Markdown Reflection; private-repo reviewer permissions,
final code packaging and submission email within 24h of receipt (absolute receipt
and recipient still need confirmation). Phase 2 stops here.

## Local usage / reproduction

Reuse the existing configured environment; no infrastructure reset or scan needed:
```bash
.venv/bin/python -m census_agent
# /reset clears state; /quit exits. Explicit calls consume trial credits.
.venv/bin/python -m census_agent --question "What is median age for Census block group 010010201001 using ACS 2020?" --json
.venv/bin/python -m pytest -q tests/phase2/test_core.py
bash scripts/verify.sh
```
Existing dependency manifests are `requirements-dev.txt` and
`requirements-snowflake.txt`; credentials stay in ignored `.env` through the existing
loader. Fresh-checkout reproduction/deployed access has not been claimed.

Reusable API:
```python
from census_agent import CensusAgent, ConversationState
from census_agent.backend import SnowflakeBackend
from census_catalog.catalog import Catalog

catalog = Catalog.load()
backend = SnowflakeBackend(catalog)
agent, state = CensusAgent(catalog, backend), ConversationState()
try:
    response = agent.ask("Using ACS 2020, what is population in Autauga County, Alabama?", state)
    follow_up = agent.ask("And in 2019?", state)
finally:
    backend.close()
```

Raw pytest stdout is retained unchanged, including traceback whitespace; a scoped
`.gitattributes` rule exempts those generated stdout logs from Git whitespace checks.
Source and documentation whitespace checks remain enabled.
