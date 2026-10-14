# Repository execution policy

This repository contains the preparation harness, verified Phase 1 Census catalog
and Phase 2 core agent with Phase 3 reliability hardening. The official PDF has arrived and is reconciled. Read
docs/PROGRESS.md for the current checkpoint. Do not invent requirements, schema,
evaluation data or successful results; do not automatically advance phases.

## Intake and authorization
- Read the actual task specification, AI-use rules, submission instructions,
  README, relevant repository instructions, starter code, manifests, and tests first.
- If challenge rules forbid AI assistance, stop AI-assisted challenge work. If
  permission is unclear, resolve it before implementation.
- Record facts, assumptions, and open questions separately in docs/CHALLENGE_SPEC.md.
- Maintain an ordered working plan with acceptance criteria and requirement-to-test
  traceability; keep docs/PROGRESS.md current.
- Never silently change scope, install services, or use paid APIs. Obtain explicit
  authorization before background processes, destructive operations, or external
  deployment. Do not push or change remotes without authorization.
- Do not print, commit, or leak secrets. General inspection must not read
  credential files or .env values; inspect only names and presence. The user has
  explicitly authorized the Snowflake connection loader to read only the required
  local .env connection values for the requested data and Cortex tests. This is
  a narrow exception for authenticated connection code, not permission to display
  credentials or inspect other secret files.

## Implementation
- Prioritize a working end-to-end vertical slice. Make small, reviewable changes.
- Preserve existing user files, history, APIs, interfaces, and the supplied stack.
- Apply KISS and YAGNI: simple, well-factored code, useful type hints, meaningful
  errors, and structured logging where useful. Avoid speculative abstractions.
- Define each slice's acceptance criteria; plan -> implement -> test -> inspect
  -> fix -> document. Keep the repository runnable; justify broad refactors.
- Use deterministic unit tests for important logic and integration tests for
  boundaries and external dependencies. Clearly label mocks and real integrations.
- Measure against explicit baselines where applicable. Track assumptions,
  tradeoffs, remaining risks, and known limitations in the documentation.
- Run targeted tests after changes and a full verification pass before delivery.
- Never claim execution or success without command output or other actual evidence.
  SKIP, unavailable tools, mocks, and untested paths are not passing results.

## Local workflow
Use the relevant skill under .agents/skills/, reading its SKILL.md before use:
challenge-intake, solution-architecture, implementation-loop,
evaluation-engineering, production-hardening, delivery-review.
Skills do not expand authorization. An independent delivery review means a fresh
reviewer perspective; it does not require another agent.

Preferred generic tooling is Python, pytest, and Ruff; adapt to the actual stack.
Local setup: `python3 -m venv .venv`, then
`.venv/bin/python -m pip install -r requirements-dev.txt`.
Run `./scripts/doctor.sh`, `./scripts/verify.sh`, `./scripts/preflight.sh`.
Scripts prefer .venv; PYTHON_BIN may select another interpreter executable.
Exit codes: 0 = checks complete, 1 = failure/risk, 2 = incomplete/skipped checks.
Doctor is informational and returns 0 when inspection itself succeeds.
Preflight checks template completion, not semantic correctness or secret contents.
Review tracked diffs locally before staging; do not expose sensitive content.

## Quality gates
- A: Actual requirements, AI-use rules, and submission rules understood.
- B: Minimal end-to-end functionality verified with recorded commands/output.
- C: Functional and edge-case tests pass.
- D: Meaningful evaluation and failure analysis complete.
- E: Clean reproduction and delivery review complete.
All gates are pending until supported by evidence. Preparation is not Gate A-E.

## Session continuation and development checkpoints
- In a new Codex session, read AGENTS.md and docs/PROGRESS.md first, then the actual
  specification, architecture, decisions, evaluation plan and current phase report.
  Inspect Git state before modifying anything. Resume the recorded authorized scope;
  a handoff does not authorize a new phase or deployment.
- Keep completed work, actual verification, limitations, next-phase tasks and exact
  reproduction commands in PROGRESS.md and the relevant report/decision log.
- The user authorized routine GitHub development checkpoints after a completed phase
  or substantial validated change. Review Git state/diffs and secret exclusions,
  run appropriate checks, commit meaningful changes and push the current branch to
  its existing origin. Do not force-push, rewrite history, change remotes or mix
  unrelated changes. Record each checkpoint in docs/DEVELOPMENT_VERSIONS.md.
- Never mark skipped tests as passed. Keep failed evaluation evidence and known
  limitations visible in version records and handoff documentation.
