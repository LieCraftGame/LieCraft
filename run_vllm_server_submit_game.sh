#!/bin/bash
#SBATCH --job-name=vllm-game
#SBATCH --output=slurm_logs/llm-%A_%a.out
#SBATCH --error=slurm_logs/llm-%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=g48
#SBATCH --gres=gpu:${4}       # $4 = N_GPUS
#SBATCH --exclude=isl-gpu58
#SBATCH --cpus-per-task=10
source /home/nratzlaf/.zshrc

# args:
#   1 MODEL_KEY
#   2 MODEL_URL
#   3 THEME
#   4 N_GPUS
#   5 TP_SIZE
#   6 PORT

MODEL_KEY="$1"
MODEL_URL="$2"
THEME="$3"
N_GPUS="$4"
TP_SIZE="$5"
PORT="$6"

echo "[$SLURM_JOB_ID] Allocated GPU. Launching vLLM $MODEL_KEY/$THEME on port $PORT …"
#       --max-model-len 32000 \

# start vLLM in foreground in backgrounded sub‐shell
(
  exec vllm serve "$MODEL_URL" \
       --port "$PORT" \
       --dtype bfloat16 \
       $([ "$TP_SIZE" -gt 1 ] && echo "--tensor-parallel-size $TP_SIZE")
) > "vllm_logs/vllm-${MODEL_KEY}-${THEME}-${SLURM_JOB_ID}.log" 2>&1 &
VLLM_PID=$!

# wait for up to 15 minutes for HTTP /v1/models to come up
deadline=$(( $(date +%s) + 1800 ))
while :; do
  if curl -sf "http://localhost:${PORT}/v1/models" >/dev/null; then
    echo "[$SLURM_JOB_ID] vLLM is ready on port $PORT"
    break
  fi
  if (( $(date +%s) > deadline )); then
    echo "[$SLURM_JOB_ID][ERROR] vLLM failed to start within 15m" >&2
    kill $VLLM_PID
    exit 1
  fi
  sleep 5
done

# launch the CPU job *now* that vLLM is confirmed live
#echo "[$SLURM_JOB_ID] Submitting CPU game job for $MODEL_KEY/$THEME"
#sbatch  --export=ALL,LLM_HOST="$(hostname)",LLM_PORT="$PORT",MODEL="$MODEL_KEY",THEME="$THEME" run_game_instance.sh

# now just hold the GPU alive until vLLM exits (which you’ll do by scancel)
#wait $VLLM_PID


cpu_jid=$( sbatch --parsable \
    --export=ALL,LLM_HOST="$(hostname)",LLM_PORT="$PORT",MODEL="$MODEL_KEY",THEME="$THEME" \
    run_game_vllm.sh)
echo "[$SLURM_JOB_ID] Launched CPU job $cpu_jid"
# now wait for the CPU job to finish, then tear down vLLM
while squeue -h -j "$cpu_jid" >/dev/null; do
  sleep 10
done
echo "[$SLURM_JOB_ID] CPU job $cpu_jid done; shutting down vLLM"
kill $VLLM_PID
wait $VLLM_PID