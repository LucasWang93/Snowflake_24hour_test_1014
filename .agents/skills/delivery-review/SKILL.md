---
name: delivery-review
description: Review final challenge deliverables against requirements, reproduction steps and evidence, then produce a concise handoff.
---

# delivery-review

Take a fresh reviewer perspective; reread actual requirements, AI-use rules,
submission instructions, traceability and final repository state. Verify clean setup,
dependency installation, runnable example, expected output format, tests, docs and
reproducibility. Do not claim clean reproduction from an already configured environment.
Run scripts/preflight.sh and inspect its failures/skips, tracked diff and filename risks
without exposing secrets. Check mismatches, incomplete features, missing evidence,
accidental credentials and submission risks; resolve blockers and document limitations.
Update docs/DELIVERY_CHECKLIST.md only with actual evidence and record Gate E status.
Produce a concise handoff with implementation outcome, setup/run/test commands,
observed evaluation, assumptions and remaining risks. Do not push, publish or submit
without authorization. A fresh reviewer pass does not require spawning another agent.

Apply [business-first-delivery](../business-first-delivery/SKILL.md) to independently
walk the core user-task matrix on the delivery surface. Lead with workflow coverage
and failures; unit/lint totals, safe refusals and completed phases do not establish
readiness when a mandatory business path remains unimplemented or unverified.
