# Reflection

## 1. Development process and architectural decisions

I approached this as a constrained analytics system rather than an unconstrained
SQL chatbot. The useful outcome is a defensible Census answer: the right statistic,
population universe, geography and release, followed by an explanation of its limits.
A syntactically correct query can still answer the wrong question. That distinction
influenced the metadata work, model interface, tests and deployment boundaries.

The work progressed through explicit acceptance phases: semantic grounding, core
conversation, reliability and independent evaluation, then deployment. Codex assisted
with implementation, tests, diagnostics and documentation. Human direction established
phase boundaries, selected Cortex, provisioned identities and hosting, authorized
production activation, and challenged response latency. AI assistance accelerated
iteration but did not constitute verification. Actual SQL results, test output and
browser evidence were retained, including failed attempts. I would not describe an
AI-generated test set as an external human audit.

Phase 1 reconciled all 73 available object schemas and 59 statistical indicator tables.
The catalog has 16,878 physical indicator fields but only 16,582 supplied definitions.
The remaining **296 fields were quarantined**, not assigned plausible meanings. Exact
Snowflake identifiers, release/product, universe and estimate/MOE classification
remain attached to each searchable mapping. BM25 over the entire defined catalog
provided inspectable, inexpensive retrieval without a vector database or another
service. Geographic keys remain strings, preserving FIPS leading zeros. Survey
intervals absent from the source metadata remain unknown.

In Phase 2, Cortex interprets structured intent and selects a retrieved catalog ID.
Python resolves geography, enforces statistical policy, compiles canonical SQL and
formats result-grounded answers. The execution boundary recompiles the typed plan
and checks exact SQL, bound parameters and row limits before opening a data connection.
This reduces expressive freedom but makes it possible to reason about what the
system can execute. Conversation state is structured rather than an ever-growing
prompt transcript; follow-ups can inherit geography or change the release while
preserving a defined metric. Unknown metrics and ambiguous sources clarify instead
of silently substituting a nearby indicator, such as an income distribution for
median household income.

I chose a constrained workflow over multi-agent orchestration because each additional
model decision adds latency, expense and a failure boundary. Likewise, additive counts
can be summed over distinct CBGs within one metric/product/release, while medians,
ratios and margins of error cannot. Refusing unsupported statistical operations is
part of correctness, although it limits apparent coverage.

Phase 3 made `AgentService` the authenticated public boundary. Each request gets a
spawned worker and fresh connector session; owner-bound conversation state and atomic
admission live in one durable SQLite database. A 55-second parent deadline, bounded
model/database work, no automatic retries, and warehouse cleanup/quarantine make
failure behavior explicit. Reserving model-call units before admission is conservative
and may charge the internal allowance for a refusal, but prevents failed requests
from bypassing the budget. It is not a dollar-denominated Snowflake spending limit.

Phase 4 retained these boundaries in a nonroot Streamlit container behind Caddy HTTPS
on the existing DigitalOcean host. The public adapter exposes a small response
allowlist, never raw service diagnostics. Authentication, separate sessions, real
answers, rate limiting and persistent state were externally tested; restart evidence
includes an authenticated answer after the SSH session ended. The hosting choice
fits multiprocessing and durable SQLite without introducing a distributed system.

Latency feedback led to measurement rather than a warehouse-size increase. For the
Alabama 2020 decennial population question, SQL took 0.280s while two Cortex calls
took 2.933s and 1.509s in a diagnostic run. Connector import and repeated catalog
indexing also contributed. The image now prepares a fingerprinted search index;
workers validate it and fall back safely. Connection-local cleanup confirmation avoids
a duplicate suspension only until another SQL attempt or connection invalidates it.
The same answer, **5,024,279**, and SQL were preserved. Paired profiled service runs
improved from 15.0294s to 13.6739s and a public browser request took 12.9913s. Model
timing also changed, so these are modest observations, not a causal percentage gain
or a production latency guarantee.

## 2. What I would improve with more time

First, complete account-level least privilege. The dedicated production identity and
explicit APP_ROLE are improvements, but PUBLIC still inherits a learning role with
broader warehouse/schema privileges. APP_ROLE currently relies on inherited OPERATE
for cleanup. An administrator should explicitly grant the necessary cleanup privilege,
then review the inheritance without breaking development access. Password-based
production authentication should move to a rotated key-pair/service identity policy.
Disabling secondary roles does not remove privileges inherited through PUBLIC.

Next, improve semantic coverage using authoritative metadata, starting with the 296
undefined fields and exact ACS survey intervals. Add carefully specified geography
crosswalks and published aggregates rather than summing medians or approximating
city boundaries. Any ratio reconstruction or uncertainty propagation needs an explicit
statistical contract and independently checked reference cases.

For operations, I would add owned DNS, monitoring and alerts, regular control-state
backups, automated credential rotation and measured cost accounting. Single-host,
one-active-request admission is intentional for this demo but constrains throughput.
Scaling would require shared transactional control and a redesigned warehouse lease
policy; simply launching more replicas would be unsafe. After profiling more samples,
I would evaluate reducing model round trips while keeping catalog grounding and
ambiguity checks. I would not trade away validation to make the demo feel faster.

## 3. Edge cases and unresolved failure modes

Statistical ambiguity remains harder than SQL injection. “Population” without a source
can select different valid products; household counts and income distributions can
share vocabulary. County names repeat, historical CBG boundaries can change, and ACS
releases are not proven single-year measurements. Comparing releases is not evidence
of a statistically significant change. Unsupported years, cities, non-additive spatial
summaries, cross-table joins and uncertain coverage should continue to clarify/refuse.

Missing, suppressed, negative, nonfinite or duplicate observations are rejected by
implemented policies. That can reject a question which a statistician could resolve
with additional source research. Catalog snapshots can also become stale. Physical
schema validation and index fingerprints help, but they do not establish the ongoing
truth of source definitions or nationwide data completeness.

A hard timeout may leave uncertainty about remote work. The service quarantines the
warehouse gate rather than automatically releasing it for another request. Recovery
requires operator inspection. Connector/Cortex outages, trial-credit exhaustion,
shared reviewer quotas and simultaneous users can therefore produce safe unavailability.
There is no highly available failover. Browser reconnection may lose the visible
conversation even though server control state persists. Temporary DNS, a single host,
service-password lifecycle and broader inherited permissions are disclosed risks.
A later Phase 4 diagnostic observed the warehouse STARTED after sampled cleanup had
confirmed SUSPENDED; these separate observations do not prove continuous suspension.

## 4. Testing strategy and additional tests needed

Tests are layered: deterministic metadata/retrieval/geography/statistical-policy tests;
canonical SQL and adversarial validation; mocked provider failures; opt-in real SQL
and Cortex tests; and clean-browser deployment tests. Numerical answers are compared
with independently written SQL references, not with another generated explanation.
The Phase 2 suite includes six development golden questions across five families and
three multi-turn scenarios; the final real suite passed 16 tests. Those cases are
useful regression checks, not a general factual accuracy estimate.

The first Phase 3 independent set was distinct from those six development questions
and passed **19/25**, including 6/9 factual, 3/5 conversational and 10/11 negative cases.
Failures included household/universe selection, an invented ownership filter, poverty
wording and an unjustified decennial source choice. The last case returned a real
number but still answered an underspecified question incorrectly. Fixes constrained
source ambiguity, improved household and tenure resolution and preserved inheritance
when a follow-up omitted the metric. The reused set then passed **25/25 as regression**;
it is not 100% held-out accuracy. An intermediate Phase 2 follow-up failure is also
preserved. These failures were more informative than the final green count.

Final offline verification records **191 passed and 25 opt-in live skips**. Skips are
not passes. Provider outage tests use fault injection; they do not claim real Snowflake
outage testing. Public acceptance tested actual authentication, grounded answers,
context, unsupported input, isolation, rate controls, privacy and restart persistence.
The final submission smoke deliberately uses only one factual turn and one follow-up
to conserve reviewer capacity. It does not repeat or replace the broader evidence.

Before broader use I would commission a fresh, frozen, independently reviewed test set,
including adversarial paraphrases, rare universes, geography ambiguity, suppressed
values and cross-release boundaries. I would add sustained concurrent-load tests,
crash/restart and network-partition exercises, credential rotation/revocation tests,
SQLite backup/restore drills and schema-drift tests against a controlled fixture.
Repeated cold/warm measurements and actual credit accounting are needed for p50/p95,
capacity and cost claims. A third-party permission and web security review would
provide evidence beyond the implementation team's own tests.
