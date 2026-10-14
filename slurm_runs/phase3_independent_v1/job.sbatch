#!/usr/bin/env bash
#SBATCH --job-name=phase3-independent-v1
#SBATCH --output=/gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014/slurm_runs/phase3_independent_v1/stdout.log
#SBATCH --error=/gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014/slurm_runs/phase3_independent_v1/stderr.log
#SBATCH --chdir=/gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014
#SBATCH --time=00:25:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --partition=day

set -euo pipefail
env RUN_PHASE3_LIVE=1 /gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014/.venv/bin/python -m evaluation.phase3 --output /gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014/slurm_runs/phase3_independent_v1/results.json
