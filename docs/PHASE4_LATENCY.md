# Phase 4 latency follow-up — Alabama decennial question

Question: “Using 2020 decennial redistricting data, how many people live in Alabama?”
Actual result before/after: **5,024,279**, same physical field P0010001 and identical
canonical SQL/params. No answer caching, model/provider change or larger warehouse.

## Diagnosis and observed measurements
- Actual user's Snowflake history: data SUM 0.280s; Cortex 2.933s +1.509s. SQL aggregation
  is not the main bottleneck. history_before.json stores only bounded stage metadata
  and canonical data SQL, not model prompts or credentials.
- Separate startup probe: catalog/index construction 1.7719s, Connector import 2.4262s.
  Every request owns a fresh spawned process/connection. These are separate probes,
  not additive stages from a single request.
- Original cleanup issued a second ALTER SUSPEND and SHOW during close; history
  contains error 90064 from attempting to suspend the already suspended warehouse.
- Paired operator AgentService profiling: 15.0294s ->13.6739s. Profiling adds overhead;
  Cortex time also varied 4.7912s ->4.4714s. This is one before/after pair, not a
  throughput benchmark, mean/p95 or proof all variance comes from these changes.
- Actual clean HTTPS browser afterward: exact question 12.9913s, context follow-up
  “What about Alabama?” 13.0160s, local security refusal 2.9941s. All pass; two factual
  answers remain 5,024,279 with decennial 2020/source/caveats. No private diagnostics
  or credentials rendered. **Improvement is modest; this is not an instant response.**

## Implemented changes
1. Build an optional complete BM25 index during Docker image build. Two JSONL records
   hold manifest/payload, bound to catalog SHA256, catalog implementation SHA256 and
   payload SHA256. Each worker still validates exact physical schema and definitions;
   it loads only the precomputed postings/document lengths. Missing/stale/corrupt
   artifacts rebuild from original metadata. No pickle, shared mutable conversation,
   reusable connector, credentials or statistical results in this artifact.
2. Skip redundant cleanup in close only after this connection's immediately preceding
   suspension was confirmed. Any subsequent SQL attempt (including failure) and any
   new connection invalidates that observation. Existing quarantine/deadline/auth/
   admission/budget/SQL controls remain unchanged; warehouse still suspends after use.

First image-index prototype spent unnecessary time reserializing postings to validate
its checksum: 1.5616s original vs1.1691s prepared. That result is retained. Final
manifest/raw-payload layout checks original bytes instead: 1.4277s vs0.7183s in the
bounded 2-CPU image probe. All postings and five ranked search cases match exactly.
Generated index is built only in the image and ignored locally, not authoritative data.

## Verification and evidence
- 11 new deterministic tests: complete posting/ranking equality, no accidental index
  rebuild, missing/stale/code-version/corrupt/truncated fallbacks, physical schema
  validation, source-overwrite prevention and SQL/failed-SQL cleanup invalidation.
- Targeted regression: 93 passed; final-format index/cleanup module: 11 passed;
  full final: **191 passed /25 live skips**, Ruff passes.
  The first targeted run's fixture failure is preserved (MagicMock.is_closed default
  was truthy); it was a test fixture issue, corrected explicitly. No hidden failures.
- First profiling attempt correctly returned overloaded while a real user request was
  active. No request interrupted and no limits bypassed. A normal fresh-process
  AgentService call with a private second reviewer token produced the paired profiles.
- Deployment acquired the existing shared admission lease, recreated only the app,
  preserved SQLite state/budgets/secrets, then released maintenance admission. No
  in-flight user query was interrupted. Active release: /opt/census/releases/latency-20261014.
- Evidence in phase4_latency/: baseline_busy.json, baseline_profile.json,
  after_profile.json, local_startup.json, image_index_benchmark_first.json,
  image_index_benchmark.json, public_browser.json, history_before.json/history_after.json,
  deployment.json and actual test logs. Query IDs and exact SQL are retained privately
  in the evaluation artifacts, never exposed by the UI.

## Remaining limits
Runtime still spends seconds importing the connector, establishing an isolated
connection and invoking Cortex. No guarantee of 13s for every request; the 55s service
deadline and <60s normal target remain. The existing PUBLIC inherited-permission
residual is unchanged; see PHASE4_REPORT.md. No new phase, data rediscovery, full
Cortex benchmark, grant/budget reset or paid infrastructure. Stop after this fix.

## Closeout clarification
cleanup_verification.json confirms the profiled request has one ALTER SUSPEND and
one confirmed cleanup state check. Its three SHOW query types include two permission
audits; they are not three warehouse checks. A later diagnostic snapshot observed
STARTED while the service lease was idle and unquarantined; it is retained as observed,
not changed to SUSPENDED. It cannot establish which intervening operation resumed the
warehouse. No additional live query or application change is part of documentation sync.
