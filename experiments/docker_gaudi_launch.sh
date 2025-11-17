#!/bin/bash
docker stop matt_olson_dev_vllm
docker rm matt_olson_dev_vllm
docker run -d \
  --name matt_olson_dev_vllm \
  --runtime=habana \
  -e HABANA_VISIBLE_DEVICES=all \
  -e OMPI_MCA_btl_vader_single_copy_mechanism=none \
  --cap-add=sys_nice \
  --net=host \
  --ipc=host \
  -v /home/sdp/molson:/mnt/home \
  -v /scratch-1:/scratch-1 \
  -v /scratch-2:/scratch-2 \
  -v /scratch-1/homes/molson:/root \
  -w /root \
  vault.habana.ai/gaudi-docker/1.19.0/ubuntu24.04/habanalabs/pytorch-installer-2.5.1:latest \
  sleep infinity

docker exec -it matt_olson_dev_vllm bash

exit 1
VLLM_PROMPT_USE_FUSEDSDPA=1 vllm serve "meta-llama/Llama-3.2-11B-Vision-Instruct" --port 8081 --tensor-parallel-size 8  \
        --max-num-seqs 2 \
        --disable-log-requests \
        --dtype bfloat16 \
        --use-v2-block-manager \
        --num_scheduler_steps 1 \
        --max-model-len 8192 \
        --distributed_executor_backend mp \
        --gpu_memory_utilization 0.92 \
        --trust_remote_code
#--max_model_len 4096