---
name: implementation-loop
description: Implement an accepted challenge plan in small runnable vertical slices with targeted tests and diff review.
---

# implementation-loop

For each slice execute plan -> implement -> test -> inspect -> fix -> document.
Define observable acceptance criteria and link requirement IDs before editing.
Implement the smallest correct version; preserve APIs/interfaces and keep the repo
runnable. Use simple functions, type hints, meaningful errors and useful structured logs.
Add deterministic tests for important logic and appropriate boundary integration tests.
Run targeted checks, inspect the diff for accidental scope changes, fix defects and
update traceability and docs/PROGRESS.md with commands and actual outcomes.
Justify broad refactors. Do not call mocks real integrations or skips passes.
Before delivery run the full verification pass; only mark Gates B/C with evidence.

After a substantial slice, update user-task coverage, not just test counts. Follow
[business-first-delivery](../business-first-delivery/SKILL.md) for compositional
acceptance and flag when phase-local success still leaves core workflows unmet.
