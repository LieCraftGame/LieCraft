#!/usr/bin/env bash
#SBATCH --job-name=vllm-server
#SBATCH --output=slurm_logs/vllm-%A.out
#SBATCH --error=slurm_logs/vllm-%A.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=g48,g80
#SBATCH --gres=gpu:$4        # $4 = N_GPUS
#SBATCH --cpus-per-task=10

source /home/nratzlaf/.zshrc

MODEL_KEY="$1"
MODEL_URL="$2"
THEME="$3"
N_GPUS="$4"
TP_SIZE="$5"
PORT="$6"

echo "[$SLURM_JOB_ID] Starting vLLM $MODEL_KEY/$THEME on port $PORT …"
(
  exec vllm serve "$MODEL_URL" \
       --port "$PORT" \
       --dtype bfloat16 \
       $([ "$TP_SIZE" -gt 1 ] && echo "--tensor-parallel-size $TP_SIZE")
) > "mp_vllm_logs/vllm-${MODEL_KEY}-${THEME}-${SLURM_JOB_ID}.log" 2>&1 &
VLLM_PID=$!

# wait up to 30m for readiness
deadline=$(( $(date +%s) + 1800 ))
while :; do
  if curl -sf "http://localhost:${PORT}/v1/models" >/dev/null; then
    mkdir -p scheduler_state/servers
    cat <<EOF > scheduler_state/servers/server-${SLURM_JOB_ID}.json
{"job_id": ${SLURM_JOB_ID},
 "host": "$(hostname).rr.intel.com",
 "port": ${PORT},
 "model_key": "${MODEL_KEY}"}
EOF
    echo "[$SLURM_JOB_ID] vLLM ready → wrote server-${SLURM_JOB_ID}.json"
    break
  fi
  if (( $(date +%s) > deadline )); then
    echo "[$SLURM_JOB_ID][ERROR] vLLM never came up" >&2
    kill $VLLM_PID
    exit 1
  fi
  sleep 5
done

# hang until externally killed
wait $VLLM_PID