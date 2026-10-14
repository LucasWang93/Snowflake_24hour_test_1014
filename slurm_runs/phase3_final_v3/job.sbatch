#!/usr/bin/env bash
#SBATCH --job-name=phase3-final-v3
#SBATCH --output=/gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014/slurm_runs/phase3_final_v3/stdout.log
#SBATCH --error=/gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014/slurm_runs/phase3_final_v3/stderr.log
#SBATCH --chdir=/gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014
#SBATCH --time=00:25:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --partition=day

set -euo pipefail
bash /gpfs/radev/pi/q_chen/sw2572/gitcodes/Snowflake_24hour_test_1014/slurm_runs/phase3_final_v3/run.sh
