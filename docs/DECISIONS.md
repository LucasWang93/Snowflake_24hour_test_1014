# Decision log

Status: Phase 1 decisions preserved; Phase 2 D-5/D-6/D-7 are now implemented.
The official PDF is reconciled. Historical records below retain their original
context; current implementation supersedes the earlier proposal status.

## Decision status register

| Decision | Status | Evidence / requirement |
| --- | --- | --- |
| D-1 Preparation harness, minimal tooling | Accepted and implemented (historical) | Existing scripts/config; preserve user files/history |
| D-2 Existing connector and bounded live probes | Accepted and implemented | SF-1 through SF-6; stored query IDs, results and cleanup |
| D-3 Metadata-grounded catalog and offline lexical retrieval | Accepted and implemented | P1-1/P1-2/P1-5; catalog, builder and tests |
| D-4 Statistical/geographic correctness boundaries | Accepted and implemented in Phase 1 scope | P1-3/P1-4; policy/geography modules and bounded live tests |
| D-5 Metadata-grounded Text-to-SQL | Accepted and implemented | Typed planning/canonical SQL/result answers; AS-1/AS-4 |
| D-6 Cortex as primary agent provider | Accepted and implemented | llama3.3-70b real intent/choice calls; AS-3 |
| D-7 Constrained workflow instead of multi-agent orchestration | Accepted and implemented | Single constrained pipeline; AS-1/AS-2/AS-4 |

## Historical records
These entries preserve the decisions and context at the time. In particular,
"requirements have not arrived" in the preparation entry is historical; current
Phase 1 requirements and evidence are available.

## 2026-10-14 — Preparation scope
Decision: Create a stack-neutral workflow harness with optional local Python development tools.
Rationale: Requirements have not arrived; preserve the original README and history.
Rejected alternatives: Speculative application scaffolding, service dependencies,
credentials, and precomputed evaluation results would assume unsupported requirements.
Tradeoff: Application tests, architecture, and quality gates remain pending.

## 2026-10-14 — Snowflake connection and smoke-test design
User authorized full AI use and live data/model calls. Use the existing local
Python environment, connector 4.8.0, explicitly authorized owner-only `.env`
loader, SQL identifier quoting and value binding. Keep the probe bounded with
60-second statement/network limits, serial counts and one request per model;
record query IDs and elapsed times and suspend the warehouse in finally.
Choose llama3.1-70b as the initial environment default because it is the requested
first model and live-tested; no quality comparison supports a preferred model yet.
Rejected: speculative agent/application scaffolding, hardcoded us-east-1 endpoint,
metadata-only row counts, and repeated unsupported-model calls. Preserve observed
71-table/2-view distinction and actual region. No credentials in tracked artifacts.

## 2026-10-14 — Phase 1 catalog architecture
Compare (1) compact JSON + in-memory lexical/BM25 search, (2) SQLite FTS5,
(3) embeddings/vector service. Choose JSON and standard-library lexical scoring:
metadata remains inspectable/versionable, startup and search are local, no new
dependency or inference cost. SQLite adds an opaque binary artifact without a
concrete need at this scale; embeddings introduce cost and nondeterminism.
Catalog entries reference exact schemas, metadata provenance and conservative
aggregation policy. Unknown physical fields are quarantined, never guessed.
Fallback: inspect quarantined/unmatched IDs and report gaps instead of returning
unverified mappings. Source family follows official Census ID conventions;
provider-specific survey interval will remain unknown unless metadata proves it.

## 2026-10-14 — D-4: statistical and geographic correctness
Status: accepted and implemented within Phase 1, not complete agent safety.
Preserve exact identifiers, release year, source family, universe and estimate/MOE
classification. Keep ACS families and decennial redistricting distinct; leave survey
interval unknown rather than infer it. Preserve 12-digit CBG strings and year-specific
FIPS, reject ambiguous counties, and separate prefix resolution from CBG membership.

Only one verified count can sum across distinct CBGs of the same field/release/product.
Medians, ratios, means, MOEs, uncertain units and unsupported amounts fail closed;
overlapping categories and temporal aggregation require evidence and are not supported.
Reject duplicates and missing/nonfinite/negative values. Alternatives of summing all
numeric columns, averaging medians or adding MOEs would silently change meaning.
Tradeoff: some legitimate distributions/amounts are conservatively unsupported.
Two-CBG real joins/sums do not prove nationwide coverage or boundary compatibility.

## 2026-10-14 — D-5: metadata-grounded Text-to-SQL
Status: grounding principle accepted; Text-to-SQL implementation planned.
Use verified field IDs, schema, universe, year, product and geography as input to
future planning. Treat 296 missing definitions as unavailable, not aliases to guessed
fields. This reduces invented-column and wrong-statistic risk and makes chosen fields
reviewable. The catalog does not itself execute arbitrary queries or guarantee that
a generated query is safe/correct. Runtime validation, result-grounded answers and
clarification behavior still need implementation and AS-1/AS-4 tests.
Rejected direction: unrestricted model SQL using only table names or hand-picked
examples as schema context.

## 2026-10-14 — D-6: Cortex as primary LLM provider
Status: accepted intended provider; no agent planning/generation integration yet.
The user requested Cortex for the chat agent foundation. Existing Snowflake/Cortex
connectivity and three available models make it the intended primary provider.
`llama3.1-70b` is the configured initial default; `llama3.3-70b` and `mistral-7b` also
returned outputs. `gemma2-9b` failed with unknown model. Greeting latencies are single
observations and do not establish model quality or an agent latency budget.
Alternatives of a new paid external provider or heavyweight local model are not
justified by the current task. Final model/function choice, prompts and fallback
behavior remain subject to PDF requirements and real agent evaluation. No provider
change, new model test or dependency installation occurs in this synchronization.

## 2026-10-14 — D-7: constrained workflow proposal
Status: proposed for a later authorized phase; not an implemented architectural fact.
Prefer one explicit sequence of scope resolution, grounded retrieval, Cortex plan,
deterministic validation, bounded execution and grounded answer. Store conversation
state explicitly and ask clarification when statistical/geographic scope is unclear.
A single constrained workflow should be easier to audit/test and deliver than
a multi-agent orchestration layer; there is no demonstrated need for agent-to-agent
delegation. Runtime implementation, orchestration semantics and benchmarks do not
exist yet. UI/framework/hosting/state-persistence choices remain open, not accepted.

## Phase 1 tradeoffs and remaining risks
JSON is inspectable and reproducible but loads/indexes in memory; the observed 3.617s
startup is not optimized or a service SLA. Lexical search is deterministic and free
of inference dependencies, but five acceptance cases do not establish general recall
or calibrated confidence. Retain full supplied definitions and all physical schema;
exclude undefined semantics from search. Keep ancillary view/geometry schemas without
fabricating statistical definitions. Geography verification is sampled, and source
metadata freshness/global key coverage remain unproven. New decisions should record
timestamp, status, options, rationale, requirement IDs, risks and actual evidence.

## 2026-10-14 — Phase 2 acceptance of D-5/D-6/D-7
Status: accepted and implemented; supersedes the historical planned/proposed status.
Use one explicit pipeline and per-conversation typed state, not a multi-agent
framework. Cortex llama3.3-70b interprets intent and chooses a retrieved catalog ID;
Python compiles and validates canonical SQL and formats actual numeric results.
Compared options: arbitrary model SQL plus a parser (larger attack/semantic surface),
entirely rule-based language parsing (limited paraphrases), and structured Cortex
semantics plus deterministic execution (chosen). Keep the full reusable catalog;
no hand-picked table/column prompt mapping. UI/deployment remain undecided.

Rejected model-written SQL and model-written statistic narratives: they add
unnecessary validation/grounding risk for the supported single-field scopes.
Tradeoff: no derived joins/ratios, open-ended SQL, cross-year calculations or complex
filters. Unsupported questions clarify/refuse instead of substituting related cells.
Published medians/means/MOEs are CBG values only; only disjoint additive counts sum.
ACS release labels are not claimed as verified survey intervals. Geography remains
CBG/county/state with year-specific FIPS; no invented city/place mapping.

## 2026-10-14 — Exact semantic categories and evaluation correction
Status: accepted and implemented. First live batch selected bachelor-or-higher
universes for a bachelor-only question (13 passed / 2 failed). Retain failed evidence.
Require exact category paths, distinguish universe filters from cell categories,
and clarify bare bachelor's questions. Explicit highest-attainment-only questions
must select the verified bachelor-only cell. This is a regression correction, not
an invented successful benchmark. No Phase 1 catalog fields or policies changed.

## 2026-10-14 — Effective privileges and bounded resources
Status: accepted and implemented. Reuse existing connector/configuration without
GRANT changes. Primary PUBLIC plus secondary ALL preserves direct-user access;
NONE denied data access in a recorded pilot. Audit visible user/role grants and
record real query IDs, while acknowledging visibility limits and broad user rights.
Canonical application SQL does not imply a least-privilege Snowflake identity.

Use zero application retries, at most two bounded model calls and at most two data
queries per turn; a shared 50s budget reserves suspend/SHOW cleanup. Return explicit
errors on timeout or malformed outputs and preserve successful context. CLI stage
progress is implemented. Suspend after every turn prioritizes trial-credit control
at the expense of warehouse-resume latency. A hosted deployment would need a
separately reviewed concurrency/resource policy; it is not added in Phase 2.

## 2026-10-14 — Count inheritance and development checkpoints
Status: accepted and implemented. A filtered category-only "what/how about people"
follow-up inherits a preceding count when Cortex omits/classifies the kind unknown.
Explicit median/mean/ratio/rate/MOE wording and generic undefined questions still
clarify. This fixes the recorded third-run conversation failure without assuming
all newly mentioned metrics share a statistic. Regression covers the observed
failure and generic income remaining ambiguous.

The user authorized development GitHub checkpoints and version records after
completed phases/substantial validated changes. Preserve the prior uncommitted
foundation in a separate Phase 1 commit, then the Phase 2 core/evidence/docs commit.
Record versions and new-session continuation instructions; never force-push or
change remotes. This authorization does not begin Phase 3 or authorize deployment,
reviewer permission changes or submission email.
