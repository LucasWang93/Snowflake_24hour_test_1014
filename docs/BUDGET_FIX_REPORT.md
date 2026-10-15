# Post-freeze reliability fix — shared Cortex budget

User explicitly authorized this repair/deployment and requested 1200 calls plus more
room for reviewer traffic. No statistical semantics, credentials, Snowflake grants,
warehouse size, request deadline or warehouse lease/quarantine policy were changed.

## Diagnosis

The previous `Limits.model_calls_per_day=120` was a hard-coded generic default, not
a Snowflake credit balance. `SQLiteControl.begin` added `events.calls=2` for every
admitted request and did not refund local refusals, startup failures or unused calls.
SQLite is the persistent `/var/lib/census/control.sqlite` in `census_census_control`.
There was no deployment environment override. Observed 60 admitted requests /120
reserved units, zero in the last hour, idle/unquarantined gate, and no expired rows.

The existing window was **rolling 86400 seconds**, not calendar midnight. Its cutoff
was functioning; all observed events were still inside 24h. This was conservative
reservation accounting exhausting a small allowance, not a broken midnight reset.
The public 0.00s rejection occurred at admission, before model/database execution.

## Implemented behavior

- Admission records rate-limit events with zero model units. Existing legacy rows
  are retained as historical reservations; they are not relabeled actual calls.
- Separate durable `model_submissions(request, at)` ledger. An injected worker hook
  atomically checks/debits just before the canonical Cortex `cursor.execute`.
  Local guards, argument serialization, login and cursor-creation failures consume 0.
  SQL data queries and warehouse cleanup do not consume Cortex units.
- Submitted attempts count even if the provider fails or returns invalid output.
  No refunds/retries can hide remote usage. SQLite commit and network send are not
  one atomic operation: a crash at that boundary or uncertain network delivery is
  conservatively charged. This measures connector submission attempts, not successful
  answers, confirmed billable tokens or exact dollar/credit usage.
- Every debit filters timestamps `at > now-86400`, independently of physical cleanup.
  Old rows expire automatically; no cron, midnight job, container restart or manual
  counter reset is needed. Budget rejection includes approximate time to next expiry.
- Lease identity/expiry/quarantine and a maximum two Cortex submissions/request are
  checked transactionally. Full budgets stop before execute, with a safe public status.

## Production limits and configuration

| Environment name | Production value | Previous value |
| --- | --- | --- |
| CENSUS_MODEL_CALLS_PER_DAY |1200 submitted attempts /rolling 24h |120 reserved units |
| CENSUS_REQUESTS_PER_MINUTE |12 /principal |6 |
| CENSUS_GLOBAL_REQUESTS_PER_MINUTE |60 |20 |
| CENSUS_MAX_SESSIONS |256 |128 |
| CENSUS_SESSION_TTL_SECONDS |7200 (2h) |1800 (30m) |

`census_web/runtime.py` validates bounded environment overrides; `deploy/compose.yaml`
supplies the reviewer settings. Generic library defaults remain conservative for
other consumers. All processes must use the same persisted policy; mismatches still
fail closed. The 55s parent deadline, one active warehouse request, canonical SQL,
zero retries and maximum two model submissions/turn remain in force. A finite limit
can still legitimately exhaust after 1200 actual attempts; no unlimited-usage claim.

## Safe migration and deployment

Approved release `/opt/census/releases/budget-20261015`, `/opt/census/current` symlink.
Build used 28 allowlisted application/configuration files, no .env, keys, credentials,
SQLite, Git or diagnostic artifacts. Application alone was stopped/recreated; Caddy
and persistent volumes retained. Permissions, reviewer tokens and production secrets
were untouched. The original control DB has an owner-only operator backup at
`/var/lib/census-operator/budget-fix-20261015/before.sqlite` (never copied into Git).

Only the five numeric policy fields changed during migration. Before/after: one
session with identical state hash, all 60 event rows and 120 legacy reserved units,
and idle/unquarantined gate preserved. New actual-call accounting starts at migration;
legacy reservations cannot establish historical actual use and are not backfilled
with invented counts. `rollout.log` records this boundary explicitly.

Rollback is operator-only: stop the new app when idle, restore old numeric policy
and old release/image together before starting the old version. Do not restore the
entire old DB over new sessions/events or clear leases/budgets merely for a green check.

## Actual verification

| Check | Result / evidence |
| --- | --- |
| Meter-specific tests |8 passed: zero-call/legacy events, actual cursor boundary, submitted failure, pre-cursor failure, reopen persistence/full-cap block, exact 24h expiry, wrong lease/per-request limit, concurrent debits, worker hook/status (some tests cover multiple assertions) |
| Targeted configuration/web tests | New environment settings and invalid0/2001/noninteger values tested; existing regressions retained |
| Full verification | **203 passed /25 opt-in live skips**, Ruff/Bash pass; `budget_fix/verify_final.log` |
| Image build and rollout | Exit0, approved release started; policy/session/event preservation captured in `budget_fix/rollout.log` |
| Runtime configuration | Actual container 1200/12/60/256/7200, deadline55; ledger initially 0; `runtime_before.json` |
| Public authenticated real answer | Alabama 2020 decennial = **5,024,279**; browser31.0242s, service30.63s, answered (not budget_exhausted); `public_smoke.json` |
| Real ledger after answer | **2 submissions for 1 request**, gate idle/unquarantined; `runtime_after.json` |
| Public local refusal | PASS: 2.9827s, refused locally; ledger remains 2; `public_refusal.json` / `runtime_after_refusal.json` |

Artifacts are under `docs/budget_fix/`. These are targeted deployment regressions,
not a new independent accuracy evaluation. No Census inventory scan or comprehensive
Cortex evaluation was repeated. Existing Phase1–5 evidence and original failures remain.
