---
name: evaluation-engineering
description: Design and run evidence-backed evaluation suited to the actual solution, including baselines and failure analysis where relevant.
---

# evaluation-engineering

Map requirements to correctness, representative and edge cases, regressions,
robustness, idempotency/retries and reproducibility. Select latency/throughput and
cost/resource metrics when relevant. Define case provenance, expected outcomes,
metric formulas, acceptance thresholds, deterministic seeds and explicit baselines.
For LLM systems only when applicable, consider retrieval, grounding, answer quality,
tool correctness, structured-output validity and hallucination. Avoid irrelevant metrics.
Record commands, environment, case IDs, baseline comparisons and observed results in
docs/EVALUATION_PLAN.md. Label estimates, mocks, unrun external tests and limitations.
Never fabricate benchmark scores. Categorize failures, connect them to cases and
requirements, recommend fixes and rerun affected checks. Gate D requires meaningful
observed evidence and failure analysis, not merely an evaluation plan.
