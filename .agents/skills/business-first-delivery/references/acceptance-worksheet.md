# Acceptance worksheet

Use an existing project requirements/evaluation document if available. Scale the
number of cases to the real scope and budget. Keep this separate from assertion counts.

| Case / requirement | Actual user request or conversation | Expected observable result / definition | Data and operations needed | Independent verification | Status and evidence |
| --- | --- | --- | --- | --- | --- |
| Stable ID + source | Representative wording; mark original vs inferred | Value/table/action, units, scope, success conditions | Granularity/source + grouping/derivation/comparison etc. | Reference SQL, fixture, manual calculation or authorized external check | Planned / blocked / failed / verified; artifact and limitations |

Before implementation:
- Identify the core task families and at least a representative complete path for
  each, including important compositions and follow-ups. Do not invent new scope.
- Resolve whether the data/operation can actually produce the requested result.
- Write expected behavior independently of the chosen implementation. When ambiguous,
  specify what clarification is necessary and what context should be inherited.
- Select the first vertical slice for useful coverage, not merely easiest execution.

Before final evaluation:
- Keep expected refusals/unsupported scope separate from supported-case failures.
- State how many actual business requests/conversations and assertion checks ran.
- Define outcome checks beyond status: correct meaning, data, scope, computation and
  presentation, with tolerances and source/release where relevant.
- Include ordinary paraphrases, negative controls and genuinely new combinations.
- Preserve the first untouched evaluation; after tuning, label reused cases regression.

At a readiness checkpoint, summarize:
1. Mandatory workflows: verified / failed / blocked / untested, with real denominators.
2. Normal-request false refusals and unsafe acceptances, reported separately.
3. References/real integration coverage versus mocks/local-only checks.
4. Full conversation outcomes, not only successful first turns.
5. Measured latency/capacity/cost observations and uncertainty, not inferred guarantees.
6. Remaining user-visible limitations and whether they prevent the promised delivery.

Do not set a universal pass percentage here. Agree thresholds from the assignment
and product risk before seeing results; a high overall score can hide a failed core
workflow or an unsafe answer. A deliberate incomplete submission can be honest, but
it must not be relabeled complete because its supported subset passed.
