# Snowflake_24hour_test_1014
Test repo for Snowflake. Interesting Try.


Census analytics chat using Snowflake Cortex and a metadata-grounded catalog. The
core Agent and isolated authenticated service are verified in Phases 1–3. The
Streamlit Web adapter is running at **https://census-104-248-239-52.sslip.io**.
**Census login/data access remains blocked pending Snowflake administrator provisioning.**
The entry point currently displays safe configuration unavailability, not a working demo. See [Phase 4 report](docs/PHASE4_REPORT.md).

Reviewer browser steps are in [REVIEWER_ACCESS.md](docs/REVIEWER_ACCESS.md); operator
setup, restricted identity, HTTPS, local durable SQLite and private token delivery
are in [DEPLOYMENT_RUNBOOK.md](docs/DEPLOYMENT_RUNBOOK.md). Credentials never belong
in Git. Public UI requires the restricted deployment configuration and fails closed
without it; existing trusted CLI remains available for local operators.

```bash
.venv/bin/python -m pip install -r requirements-dev.txt -r requirements-web.txt
.venv/bin/python -m pytest -q tests/phase4
bash scripts/verify.sh
# On the approved configured host only:
docker compose -f deploy/compose.yaml up -d --build
```

See [architecture](docs/ARCHITECTURE.md), [evaluation](docs/EVALUATION_PLAN.md),
[limitations and next steps](docs/PROGRESS.md). Only verified additive counts aggregate;
medians/ratios/MOEs and unsupported geography/source combinations clarify or refuse.
Final Reflection, reviewer repository permissions and submission remain outstanding.
