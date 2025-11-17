#!/bin/bash
#SBATCH --job-name=API-Dgame
#SBATCH --output=slurm_logs/game-%A_%a.out
#SBATCH --error=slurm_logs/game-%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=10
source /home/nratzlaf/.zshrc

echo "[$SLURM_JOB_ID] Running API model $MODEL on theme $THEME" 
# just forward PROVIDER into your Python driver
#uv run src/llm_experiments/run_hf_array.py \
uv run src/llm_experiments/example.py --model "$MODEL" --theme "$THEME"
    
    #--api       \
    #--provider  "$PROVIDER"