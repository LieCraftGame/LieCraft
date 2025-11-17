#!/bin/bash
#SBATCH --job-name=D-game
#SBATCH --output=slurm_logs/game-%A_%a.out
#SBATCH --error=slurm_logs/game-%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=10
source /home/nratzlaf/.zshrc

# We get these via --export from the GPU job:
#   $LLM_HOST, $LLM_PORT, $MODEL, $THEME

LLM_URL="http://${LLM_HOST}.rr.intel.com:${LLM_PORT}/v1"

echo "[$SLURM_JOB_ID] Starting game for $MODEL/$THEME → $LLM_URL"
uv run src/llm_experiments/run_hf_array.py \
    --model   "$MODEL" \
    --theme   "$THEME" \
    --vllm_url "$LLM_URL"