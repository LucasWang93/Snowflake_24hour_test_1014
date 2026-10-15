# Census agent retrospective: transferable lessons

This is a case study, not a universal project specification or benchmark.

A Census analytics take-home had a metadata-grounded catalog, canonical SQL controls,
unit/integration tests and a deployed authenticated UI. Reviewers praised these but
rejected the work for query coverage: county rankings, state income comparisons and
language/education/insurance/internet rates did not meet their evaluation needs.
Explicit population questions and simple follow-ups worked. The original ten
reviewer questions were not supplied; do not claim a reconstructed set is the original.

The implementation's typed SQL plans allowed single-region values and sums, while
rates were explicitly rejected and result validation assumed a single row. Relevant
count fields existed for several requested rate families. This was in part an
executor/semantic-operation gap, not merely missing data or insufficient model size.

The reported 180/191/203 offline checks were real unit/boundary regressions, not
hundreds of completed user tasks. Development covered six golden questions and
three conversations. A separate 25-case first evaluation scored19/25; after fixes,
25/25 on the reused cases was regression. Keeping those labels honest was necessary
but insufficient: the evaluation still lacked broad challenge of core query coverage.

A later 12-turn real-backend diagnostic recorded seven answers from eight ordinary
queries, with an in-scope phrase “give me an update on the population” falsely blocked
by a local update-word rule before any model call. English and Chinese summaries both
produced off_topic under the query-planning prompt. UI messages existed, but backend
state contained metric/geography/year intent rather than historical result records.
Do not infer from that restricted task/context that the underlying model cannot summarize.
This small targeted diagnostic does not estimate general accuracy or refusal rates.

Other important boundaries:
- Ratios of compatible aggregate counts can be meaningful when numerator/denominator,
  disjoint categories, universe, source and geography are verified. Do not sum or
  average percentages indiscriminately, or refuse all derived rates by default.
- Fine-geography medians do not reconstruct an exact higher-geography median. Check
  for a compatible published source early; an approximation is not an exact answer.
- An initial shared daily allowance reserved two model units per request, including
  local refusals/unused calls. It exhausted while credit usage was reportedly modest.
  The rolling window was working; the problem was accounting plus allowance sizing.
  A repair metered connector submissions, retained legacy audit rows and tested expiry.
- Stateless parameter inheritance is narrower than full conversational analysis.
  Distinguish querying, comparing stored results, explaining and summarizing.

The failure pattern was allowing strong component engineering and phase-local passes
to substitute for verified breadth of user outcomes. The remedy is a business-coverage
matrix, early data-feasibility gates, compositional slices and independent workflow
acceptance, with essential security retained. Do not carry over Snowflake-specific
schemas, a fixed number of cases or this project's deployment choices to other work.
