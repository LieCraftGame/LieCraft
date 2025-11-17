#!/usr/bin/env bash
# run_multiplayer_array_optimized.sh
set -euo pipefail

http_proxy=http://proxy-dmz.intel.com:912; 
https_proxy=http://proxy-dmz.intel.com:912; 
no_proxy="127.0.0.1,localhost,intel.com"
export HF_HUB_CACHE=/export/work/nratzlaf/models
export http_proxy=http://proxy-dmz.intel.com:912; 
export https_proxy=http://proxy-dmz.intel.com:912; 
export no_proxy="127.0.0.1,localhost,intel.com"

### ─── CONFIG ───────────────────────────────────────────
HF_MODELS=(llama-3.3 \
           llama-3.1 \
           deepseek-distilled-qwen \
           deepseek-distilled-llama \
           qwen-3 \
           qwen-2.5 \
           gemma3 \
           gemma3-12)

HF_URLS=(   meta-llama/Llama-3.3-70B-Instruct \
            meta-llama/Llama-3.1-70B-Instruct \
            deepseek-ai/DeepSeek-R1-Distill-Qwen-32B \
            deepseek-ai/DeepSeek-R1-Distill-Llama-70B \
            Qwen/Qwen3-32B \
            Qwen/Qwen2.5-32B-Instruct \
            google/gemma-3-27b-it \
            google/gemma-3-12b-it)

GPUS=(4 4 4 4 4 2 2 2)
TP_SIZE=(4 4 4 4 4 2 2 2)

API_MODELS=(gpt-4o o4-mini gemini-2.5-flash claude-3.7)
API_PROVIDERS=(azure azure gemini anthropic)

THEMES=(default energy_grid finance_crisis hospital insurance \
        m_and_a military parenting policing criminal)

TOTAL_GAMES=10000
PLAYERS_PER_GAME=5
MAX_CONCURRENT_GAMES=20
BASE_PORT=8000

mkdir -p mp_vllm_logs mp_slurm_logs scheduler_state/servers

# Arrays to store vLLM server info (initialize as empty)
declare -a VLLM_JIDS=()
declare -a VLLM_URLS=()
declare -a VLLM_KEYS=()

# Arrays to track running CPU games (initialize as empty)
declare -a RUNNING_CPU_JIDS=()
declare -a RUNNING_GAME_IDS=()

### ─── STEP 1: Launch all vLLM servers once ─────────────
echo "=== Launching vLLM servers ==="
for m_idx in "${!HF_MODELS[@]}"; do
    #debug break early:
    #VLLM_JIDS=(
    #    291608 291609 291610 291611 291612
    #    291605 291606 291607
    #)
    #break

    key=${HF_MODELS[$m_idx]}
    url=${HF_URLS[$m_idx]}
    gpus=${GPUS[$m_idx]}
    tp=${TP_SIZE[$m_idx]}
    port=$(( BASE_PORT + m_idx ))
    
    echo "Launching vLLM server for $key on port $port..."
    jid=$( sbatch --parsable \
            --job-name="vllm-${key}" \
            --output="mp_vllm_logs/vllm-${key}.out" \
            --error="mp_vllm_logs/vllm-${key}.err" \
            --gres=gpu:${gpus} \
            run_vllm_random_multiplayer.sh "$key" "$url" "persistent" "$gpus" "$tp" "$port" )
    
    VLLM_JIDS+=( "$jid" )
    echo "  Submitted vLLM job $jid for $key"
done

# Wait for all vLLM servers to be ready



echo "=== Waiting for vLLM servers to be ready ==="
for i in "${!VLLM_JIDS[@]}"; do
    jid="${VLLM_JIDS[$i]}"
    key="${HF_MODELS[$i]}"
    jsonf="scheduler_state/servers/server-${jid}.json"
    
    echo -n "Waiting for $key (job $jid)..."
    until [[ -f "$jsonf" ]]; do 
        echo -n "."
        sleep 5
    done
    
    # Read server info
    read host port model_key < <(
        python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["host"], d["port"], d["model_key"])' \
            "$jsonf"
    )
    
    VLLM_URLS+=( "http://${host}:${port}/v1" )
    VLLM_KEYS+=( "$model_key" )
    echo " Ready at ${host}:${port}"
done

echo "All vLLM servers are ready!"

### ─── FUNCTION: Check and clean finished games ─────────
check_finished_games() {
    local -a keep_cpu=()
    local -a keep_gid=()
    
    for i in "${!RUNNING_CPU_JIDS[@]}"; do
        jid="${RUNNING_CPU_JIDS[$i]}"
        gid="${RUNNING_GAME_IDS[$i]}"
        
        # Check if job is still running
        if squeue -h -j "$jid" 2>/dev/null | grep -q .; then
            keep_cpu+=( "$jid" )
            keep_gid+=( "$gid" )
        else
            echo "Game $gid (job $jid) has finished"
        fi
    done
    
    RUNNING_CPU_JIDS=( "${keep_cpu[@]}" )
    RUNNING_GAME_IDS=( "${keep_gid[@]}" )
}


### ─── FUNCTION: Launch a single game ─────────────
launch_game() {
    local game_id=$1
    local theme=${THEMES[$(( (game_id-1) % ${#THEMES[@]} ))]}
    
    echo "=== Launching Game $game_id (theme: $theme) ==="
    
    # Pick 5 distinct models from HF+API pool
    local total_models=$(( ${#HF_MODELS[@]} + ${#API_MODELS[@]} ))
    mapfile -t sel_idx < <( shuf -i0-$((total_models-1)) -n $PLAYERS_PER_GAME )
    
    local player_specs=()
    local slot=0
    
    # Build player specs
    for idx in "${sel_idx[@]}"; do
        if (( idx < ${#HF_MODELS[@]} )); then
            # HF model - use pre-launched server
            local url="${VLLM_URLS[$idx]}"
            local key="${VLLM_KEYS[$idx]}"
            player_specs+=( "--player" "${slot}:type=hf,url=${url},key=${key}" )
            echo "  Player $slot: HF model $key at $url"
        else
            # API model
            local api_idx=$(( idx - ${#HF_MODELS[@]} ))
            local model="${API_MODELS[$api_idx]}"
            local provider="${API_PROVIDERS[$api_idx]}"
            player_specs+=( "--player" "${slot}:type=api,model=${model},provider=${provider}" )
            echo "  Player $slot: API model $model via $provider"
        fi
        slot=$((slot+1))
    done
    
    # Submit CPU game job
    local cpu_jid=$( sbatch --parsable \
        --job-name="mp-game-${game_id}" \
        --output="mp_slurm_logs/mp-${game_id}.out" \
        --error="mp_slurm_logs/mp-${game_id}.err" \
        --nodes=1 --ntasks=1 --partition=cpu --cpus-per-task=10 \
        --export=ALL,THEME="$theme" \
        --wrap="cpu/bin/python src/llm_experiments/run_multiplayer.py --theme $theme ${player_specs[*]}" )
    
    RUNNING_CPU_JIDS+=( "$cpu_jid" )
    RUNNING_GAME_IDS+=( "$game_id" )
    
    echo "  Submitted game $game_id as job $cpu_jid"
}

### ─── STEP 2: Run games with rolling window ────────────
echo -e "\n=== Starting game execution loop ==="
game_counter=0

# Main game loop
while (( game_counter <= TOTAL_GAMES || ${#RUNNING_CPU_JIDS[@]} > 0 )); do
    # Check for finished games
    check_finished_games
    
    # Launch new games to maintain MAX_CONCURRENT_GAMES
    while (( ${#RUNNING_CPU_JIDS[@]} < MAX_CONCURRENT_GAMES && game_counter <= TOTAL_GAMES )); do
        launch_game $game_counter
        ((game_counter++))
        sleep 2  # Small delay between submissions
    done
    
    # Status update
    if (( game_counter % 10 == 1 || game_counter > TOTAL_GAMES )); then
        echo -e "\n--- Status: ${#RUNNING_CPU_JIDS[@]} games running, $((game_counter-1))/$TOTAL_GAMES launched ---"
    fi
    
    # Wait before next check
    sleep 10
done

echo -e "\n=== All games completed! ==="

### ─── STEP 3: Cleanup vLLM servers ─────────────────────
echo -e "\n=== Cleaning up vLLM servers ==="
for i in "${!VLLM_JIDS[@]}"; do
    jid="${VLLM_JIDS[$i]}"
    key="${HF_MODELS[$i]}"
    echo "Cancelling vLLM server $key (job $jid)"
    scancel "$jid" || echo "  (already finished)"
done

echo -e "\nDone!"
