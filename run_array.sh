#!/bin/bash
#HF_MODELS=(gemma3 olmo-2 qwen-2.5 qwen-3 qwq qwen-3-moe deepseek-distilled-qwen llama-3.3 llama-3.1 deepseek-distilled-llama)
# HF_MODELS=(qwen-2.5 qwen-3 mistral-small llama-3.1 llama-3.3 qwq qwen-3-moe deepseek-distilled-qwen deepseek-distilled-llama)
HF_MODELS=(llama-3.3 \
           llama-3.1 \
           deepseek-distilled-llama \
           gemma3 \
           qwen-2.5 \
           qwen-3 \
           qwq \
           qwen-3-moe \
           deepseek-distilled-qwen)

HF_URLS=(meta-llama/Llama-3.3-70B-Instruct \
         meta-llama/Llama-3.1-70B-Instruct \
         deepseek-ai/DeepSeek-R1-Distill-Llama-70B \
         google/gemma-3-27b-it \
         Qwen/Qwen2.5-32B-Instruct \
         Qwen/Qwen3-32B \
         Qwen/QwQ-32B \
         Qwen/Qwen3-30B-A3B \
         deepseek-ai/DeepSeek-R1-Distill-Qwen-32B)

#GPUS=(1)
#TP_SIZE=(1)
GPUS=(8 8 8 2 2 4 4 4 4)
TP_SIZE=(8 8 8 2 2 4 4 4 4)

THEMES=(default) #  energy_grid finance_crisis hospital insurance m_and_a military parenting policing)
#THEMES=(default) #  energy_grid finance_crisis hospital policing)
BASE_PORT=8000
COUNT=0

mkdir -p vllm_logs
find_free_port() {
  local start=$1 end=$2 port
  for port in $(seq $start $end); do
    # no LISTENer on TCP port?
    if ! lsof -iTCP:"$port" -sTCP:LISTEN -t &>/dev/null; then
      echo "$port"
      return 0
    fi
  done
  return 1
}

for idx in "${!HF_MODELS[@]}"; do
    model=${HF_MODELS[$idx]}
    url=${HF_URLS[$idx]}
    gpus=${GPUS[$idx]}
    tp=${TP_SIZE[$idx]}

    for theme in "${THEMES[@]}"; do
        port=$(( BASE_PORT + COUNT ))
        #port=$(find_free_port 8000 9000) || {
        #    echo "ERROR: no free port in 8000–9000" >&2
        #    exit 1
        #}
        echo "Submitting vLLM+Game job for $model with URL $url ($theme) on port $port (GPUs=$gpus,TP=$tp)"
        sbatch \
        --gres=gpu:${gpus} \
        run_vllm_server_submit_game.sh \
            "$model" "$url" "$theme" "$gpus" "$tp" "$port"

        COUNT=$((COUNT+1))
    done
done