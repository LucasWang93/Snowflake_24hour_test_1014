---
name: business-first-delivery
description: Plan, build, and review user-facing engineering projects or technical take-homes against real user workflows, with business coverage and evidence-based delivery gates. Use at scoping, architecture decisions, milestone reviews, and final acceptance; not for isolated maintenance tasks without product-scope decisions.
---

# Business-first project delivery

Treat completion as demonstrated user outcomes. Component quality, phase completion
and test counts are supporting evidence, not substitutes for functional coverage.
Apply this within the user's actual scope/time budget; do not invent requirements,
expand a phase, bypass safety, or authorize paid calls/deployment/sharing.

## Establish the actual acceptance surface

Read the authoritative brief, reviewer/customer feedback and current implementation.
Translate requirements into representative user requests and complete workflows
before narrowing the architecture. Distinguish mandatory outcomes, reasonable
interpretations, proposals and explicitly excluded scope. Unknown reviewer questions
are unknown: label your representative cases, never claim they are the originals.

Use [the acceptance worksheet](references/acceptance-worksheet.md) when a project
needs a concrete coverage matrix. Adapt the case count and artifacts to its size;
there is no universal requirement for a fixed number of tests or a new framework.
For an ongoing project, reuse existing specs/results instead of creating parallel logs.

Include composition, not just isolated happy paths: if scope involves ranking,
comparison, derived metrics, language variants or multi-turn work, test those actual
operations together. A successful count query does not establish ranking coverage;
a single-entity answer does not establish a comparison conversation.

## Check data and operation feasibility before committing to architecture

For each core workflow, identify the necessary data, definitions, granularity,
operations, result shape and source of ground truth. A catalog matching a field title
is not proof that the requested statistic can be produced at the requested scope.
Distinguish data already available but executor-limited, derivable with justified
semantics, and genuinely unavailable. Surface blocking source/definition gaps early.
Do not fabricate exact answers or silently change metrics to avoid a limitation.
Adding sources/dependencies/infrastructure requires the applicable authorization.

Choose an architecture capable of the core operations. Do not choose an easy-to-prove
one-row/single-metric interface and then classify the missing business operations as
unanswerable. If extending the operation/result contracts is necessary, name that
work explicitly. Revisit the design when a core family has no executable path.

## Implement a meaningful vertical slice

Choose an early slice that demonstrates a central workflow and its hardest useful
composition, with real boundaries where authorized. Establish essentials such as
secret handling and execution safety alongside it. Defer discretionary infrastructure,
polish and abstractions that do not improve acceptance; never defer a critical
security control simply to make the demo answer more questions.

After each slice, update the business matrix: what can a user now finish, what remains
blocked, and what evidence proves it? Proactively flag when phase-local success still
leaves the overall objective unmet. Respect a user's stop/freeze instruction; report
partial completion rather than silently starting the next phase.

## Evaluate business behavior and refusals separately from internals

Keep business cases distinct from pytest assertions, unit checks and mocked fault
tests. Use independently specified references; do not verify output with the same
compiler/formula that generated it. Validate numeric values, definitions, scope,
source, output shape and full conversations, not only answered/nonempty status.

Freeze a development suite and an untouched evaluation suite when the scope/budget
supports it. Preserve first-run failures. Once a case informs a fix, subsequent
success on it is regression, not new held-out accuracy. Supplement reused/golden
cases with unfamiliar paraphrases and compositions; avoid tuning the suite down to
operations that already work.

Test normal in-scope wording against guardrails, including benign words that resemble
commands. Measure unsupported/false-refusal failures as well as unsafe acceptance.
Separate missing information, unsupported capability, missing data, unrelated topic,
policy rejection and provider failure. Do not label every unsupported request as
inappropriate. A safe refusal of a required, answerable workflow is a coverage failure.

For conversational products, verify what the backend actually receives. Visible UI
history is not proof of model/result memory. Test the full chain: establish a result,
change an entity, compare, explain/summarize when required, and preserve context across
clarification. Summaries must use verified results; no prior result means clarify,
not invent one or claim the user's request is inappropriate.

Exercise limits with expected ordinary usage, including shared sessions, rates and
budgets. Distinguish reservations, submission attempts, successful calls and monetary
cost. Test expiry/restart behavior and zero-work failures without secretly clearing
counters or weakening safety. Keep network/charging uncertainty explicit.

## Report and decide readiness by coverage

Lead status reports with core workflows completed/failed/unverified, important false
refusals and data gaps. Then report numeric/semantic correctness, independent
reference coverage, latency and operational failures. Report unit/lint counts in a
separate category. Explain the sample/denominator; do not exclude required unsupported
cases or inflate success by adding expected refusals.

Before declaring ready, independently walk through the core acceptance workflows on
the delivery surface using clean context. Require evidence for every mandatory path
or explicitly disclose an incomplete submission. Local-only tests/mocks do not prove
authenticated deployed behavior. Necessary paid/external checks remain permission-bound.
A green phase or verification script cannot overrule missing user-visible functionality.

For analytics-agent projects, read the short
[Census retrospective](references/census-retrospective.md) for concrete failure modes;
apply its lessons without assuming every project is Census, SQL or an LLM agent.
