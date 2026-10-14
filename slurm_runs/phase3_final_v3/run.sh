#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.."
RUN_PHASE3_LIVE=1 .venv/bin/python -m evaluation.phase3 --output slurm_runs/phase3_final_v3/results.json
RUN_PHASE2_LIVE=1 PHASE2_EVIDENCE="$PWD/slurm_runs/phase3_final_v3/phase2_results.json" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q -s tests/phase2/test_live.py
