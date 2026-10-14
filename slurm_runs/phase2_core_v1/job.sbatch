#!/usr/bin/env bash
#SBATCH --job-name=phase2-core-v1
#SBATCH --output=/gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014/slurm_runs/phase2_core_v1/stdout.log
#SBATCH --error=/gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014/slurm_runs/phase2_core_v1/stderr.log
#SBATCH --chdir=/gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014
#SBATCH --time=00:20:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --partition=day

set -euo pipefail
env RUN_PHASE2_LIVE=1 PHASE2_EVIDENCE=/gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014/slurm_runs/phase2_core_v1/results.json PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014/.venv/bin/python -m pytest -q -s tests/phase2/test_live.py
