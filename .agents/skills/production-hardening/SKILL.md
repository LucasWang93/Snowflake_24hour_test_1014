---
name: production-hardening
description: Review an implemented solution for relevant reliability and security risks and fix critical defects without unnecessary infrastructure.
---

# production-hardening

Inspect validation, exceptions, logging/redaction, timeouts, retries/backoff,
rate limits, resource bounds, security/secret handling, concurrency and recoverability
as appropriate to actual boundaries. Do not access credentials or log secret values.
Classify findings: P0 = submission blocker, exploitable exposure or data loss;
P1 = likely correctness/reliability failure; P2 = lower-impact improvement/limitation.
Record trigger, affected requirement, severity, proposed fix and evidence. Fix P0 then
P1 before optional P2 work; document deferred risks in docs/PROGRESS.md and architecture.
Use targeted regression or boundary tests for fixes. Keep retries bounded and avoid
retrying unsafe operations without an idempotency strategy. Add no infrastructure
without need, and obtain authorization for services, paid APIs or external deployment.
