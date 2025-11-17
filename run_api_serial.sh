#!/bin/bash
MODELS=("gpt-4o-mini")
THEMES=(default energy_grid finance_crisis hospital insurance m_and_a military parenting policing)
BASE_PORT=8000
COUNT=0

for model in "${MODELS[@]}"; do
    for theme in "${THEMES[@]}"; do
        echo "running model=$model on theme=$theme"
        sbatch --export=ALL,MODEL="$model",THEME="$theme" run_game_api.sh
    done
done