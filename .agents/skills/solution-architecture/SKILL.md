---
name: solution-architecture
description: Select and document a lightweight architecture after challenge intake, comparing viable options against delivery constraints.
---

# solution-architecture

Use accepted requirements and repository interfaces as constraints. Compare 2-3
lightweight options on complexity, reliability, latency, cost, testability, and
time-to-delivery. Distinguish measured facts from estimates; select the simplest viable
option, preserving starter code and the existing stack.
Document components, contracts, input/output schemas, data flow, failure modes,
tradeoffs, and a fallback plan in docs/ARCHITECTURE.md. Use Mermaid only if helpful.
Record the decision, timestamp, rationale and rejected alternatives in docs/DECISIONS.md.
Avoid speculative abstractions or infrastructure. Identify the smallest end-to-end
slice and how Gate B will be demonstrated without silently changing scope.
