# Phase 5 — final submission preparation

Prepared 2026-10-14 America/New_York (budget snapshot 2026-10-15 00:01:39 UTC).
Scope: final documentation, requirement audit and bounded checks only. Production
application, configuration, secrets, SQLite state and prior evaluation artifacts were
not modified. No deployment/restart, new Agent functionality or email sending.

**Ready to submit: NO.** Technical package and live demo are prepared; mandatory
private-repository access and actual receipt/deadline/recipient are not verified.

## Deliverables and audit

- Root README.md now prominently links the operational demo, reviewer instructions,
  architecture, real setup commands, evaluations and limitations.
- Root REFLECTION.md addresses all four PDF topics with concrete evidence, including
  296 quarantined fields, grounded SQL/conversation, initial independent failures,
  measured deployment performance, Codex use and human-directed decisions.
- SUBMISSION_EMAIL_DRAFT.md contains a reviewable draft; no token/recipient guess.
  The existing private demo token must accompany the actual submission separately.
- Canonical requirement register retains 30 unique IDs (the original 23 plus seven
  reconciled PDF obligations); each has a verification method. AS-7/8 now complete;
  AS-9 blocked; AS-10 unsent/unconfirmed; AS-16 remains partial, not universal coverage.
- Historical reports/evidence retained. Earlier deployment-blocked statements are
  historical; present public deployment is verified. No new full scan/model evaluation.

## Actual final verification

| Check | Actual outcome | Evidence |
| --- | --- | --- |
| Doctor | Exit 0, informational | phase5_final/doctor.log |
| Full offline verification | Exit 0; 191 passed /25 opt-in live skips; Ruff format/lint and Bash syntax pass | phase5_final/verify.log |
| Dependency check | Exit 0, no broken requirements | phase5_final/dependencies.log |
| Offline example | Search population/year2020 returned three exact physical mappings | Recorded command below |
| External clean browser | Trusted HTTPS HTTP200, login required; reviewer login succeeds | phase5_final/public_smoke.json |
| Real factual question | ACS2020 Autauga population55,639; browser27.0405s, service26.44s | Same artifact; prior independent SQL references in phase4_activation/reference_sql.json |
| Contextual follow-up | “And in2019?” ->55,380; browser12.9892s, service12.15s | Same artifact; no explicit geography/metric needed |
| Observed privacy | No token/raw SQL/selected diagnostic markers in rendered responses | Same smoke assertions; not a full penetration test |
| Secret exclusion | No high-confidence findings in reachable Git blobs/eligible working files; exact current reviewer tokens checked without printing | phase5_final/secret_audit.json |
| Traceability | Unique IDs, nonempty verification, 11 exact reviewer names and four reflection topics checked | phase5_final/traceability.json |
| Final preflight | Exit2: remaining delivery items and precommit changes; NOT a complete delivery pass | phase5_final/preflight.log |

ShellCheck is unavailable and explicitly skipped. The 25 disabled real tests are not
passing results. Prior actual Docker build/install/restart evidence supports deployed
reproducibility; this phase did not claim a fresh local dependency installation.
The public smoke reuses independently checked reference values and is regression,
not a new held-out evaluation. Original independent19/25 and later regression25/25
remain separately recorded. No production safeguard was reset or weakened.

Commands actually executed:

```bash
bash scripts/doctor.sh
bash scripts/verify.sh
.venv/bin/python -m pip check
.venv/bin/python -m census_catalog search population --year 2020 --top-k 3
bash scripts/preflight.sh
```

Additional operator checks: fresh Playwright context with existing private reviewer
token (owner-only temporary copy removed), read-only production SQLite counters,
bounded Snowflake SHOW metadata, GitHub repository metadata GET and content-level
Git/worktree scan. No credentials were printed. Final commit/push reference is in
DEVELOPMENT_VERSIONS.md and Git; production remains the v0.4.4-dev application image.

## Reviewer access — all 11 accounts

Unauthenticated GET `/repos/LucasWang93/Snowflake_24hour_test_1014` returned HTTP200,
**private=false**. This positively contradicts AS-9. SSH Git access supports the
existing push workflow but cannot verify private visibility or collaborator grants.
No gh executable, GH_TOKEN/GITHUB_TOKEN/GITHUB_API_TOKEN or Git credential helper
was available. No credentials were searched for in unrelated files.

| Exact PDF account | Invitation | Effective private access |
| --- | --- | --- |
| sfc-gh-setli | UNVERIFIED | UNVERIFIED |
| sfc-gh-vb | UNVERIFIED | UNVERIFIED |
| Sfc-gh-wenli | UNVERIFIED | UNVERIFIED |
| sfc-gh-cnivera | UNVERIFIED | UNVERIFIED |
| Sfc-gh-twhite | UNVERIFIED | UNVERIFIED |
| Sfc-gh-mtreadwell | UNVERIFIED | UNVERIFIED |
| Sfc-gh-mvytlingam | UNVERIFIED | UNVERIFIED |
| Sfc-gh-cgaboury | UNVERIFIED | UNVERIFIED |
| Sfc-gh-sabbas | UNVERIFIED | UNVERIFIED |
| Sfc-gh-jsummer | UNVERIFIED | UNVERIFIED |
| sfc-gh-htian | UNVERIFIED | UNVERIFIED |

Operator action: repository Settings -> General -> Danger Zone -> Change visibility
-> Private; then Settings -> Collaborators -> Add people, add these exact accounts
with read access. Confirm pending invitations are accepted/effective access exists.
If the personal-repository UI only offers its collaborator permission tier, use that
supported tier and record it rather than claiming a nonexistent granular read grant.
Do not mistake public readability or a sent invitation for private collaborator access.
An authenticated repository administrator must perform/verify these steps; no API
access or invitation success is claimed by this report.

## Capacity and remaining operational risks

Before smoke:64/120 reserved units, gate idle/unquarantined. After the two admitted
turns:68/120, **52 remaining =26 admissions** at two units each. For planning only,
11 reviewers each making two turns consume44 units; this fits this snapshot if no
other use intervenes. Shared principal six/minute and one active request still apply.
This is neither simultaneous capacity nor a credit guarantee. No counter reset.

APP_ROLE metadata check returned no visible HOMEWORK_GUARD monitor, and SHOW WAREHOUSES
reported resource_monitor=null, X-Small, auto_suspend60, SUSPENDED at that observation.
**Snowflake monetary/trial-credit headroom is unverified.** Administrator: inspect
Snowsight billing/trial balance and `SHOW RESOURCE MONITORS;` / `SHOW WAREHOUSES LIKE
'SNOWFLAKE_LEARNING_WH';` with appropriate authorized visibility. Confirm actual credit
budget and monitor assignment before reviewers; no grant/monitor modification here.

Inherited PUBLIC learning-role warehouse/schema permissions remain a P1 residual.
Explicit APP_ROLE cleanup OPERATE and safe inheritance remediation need administrator
review; no changes made. Limited geography/statistics, undefined fields, uncertain ACS
intervals, single-host/one-active-request capacity, password lifecycle and temporary
DNS remain disclosed. Normal sampled responses satisfy60s; no p95 or SLA claim.

## Receipt, deadline and email

The PDF requires submission within24h of receipt but contains no actual receipt time,
timezone or recipient. Narrow connected-mailbox searches found no matching assignment
message; broader Snowflake results were unrelated and not treated as evidence. User
confirmation is requested. Do not infer timing from file dates or manufacture an email
address. Candidate signature in the draft also requires confirmation. No email or
invitation message was sent through the connected mailbox.

## Next actions

1. Operator makes repository private and verifies all11 reviewer permissions.
2. Confirm receipt/timezone/recipient and credit headroom; privately include existing
   demo access credential with the submission. Final email draft is ready for review.
3. Recheck those changed delivery facts, then obtain explicit authorization to send.
   Do not add features, reset budgets or redeploy merely for final packaging.
