#!/usr/bin/env python3
# This file supports just one kind of model being run. If we want a mix of models in the pool then use the other test files
import os
import time
import sys
import csv
import random
import asyncio
import subprocess
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

import requests
import argparse

from deceptiongame.online_game_manager import GameManager
from deceptiongame.player_llm import OnlineAI
from deceptiongame.actions import SelectRoleAction

_HF_MODEL_TO_URL = {
    "llama-3.1": "meta-llama/Llama-3.1-70B-Instruct",
    "llama-3.3": "meta-llama/Llama-3.3-70B-Instruct",
    "gemma3":    "google/gemma-3-27b-it",
    "qwen-2.5":  "Qwen/Qwen2.5-32B-Instruct",
    "qwen-3":    "Qwen/Qwen3-32B",
    "qwq":       "Qwen/QwQ-32B",
    "qwen-3-moe":"Qwen/Qwen3-30B-A3B",
    "mistral-small": "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
    "deepseek-distilled-qwen":  "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    "deepseek-distilled-llama": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
}

PLAYER_NAMES = ["Alice", "Bob", "Charlie", "David", "Eve"]

def start_vllm(model_url: str, port: int = 8000):
    cmd = [
        "vllm", "serve",
        model_url,
        "--port", str(port),
        "--dtype", "bfloat16"
    ]
    print(f"[vLLM] Launching {model_url} on port {port}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    deadline = time.time() + 1200
    for line in proc.stdout:
        print(line, end="")
        if "Application startup complete" in line:
            print(f"[vLLM] Ready → http://localhost:{port}/v1")
            return proc
        if time.time() > deadline:
            proc.terminate()
            raise TimeoutError("vLLM startup timed out")
    raise RuntimeError("vLLM exited unexpectedly")

async def run_one(model_name: str, theme: str, vllm_url: str, api=None, provider=None):
    if provider:
        if provider.lower() == 'azure':
            url = os.environ.get('AZURE_OPENAI_ENDPOINT')
            api_key = os.environ.get('AZURE_OPENAI_API_KEY')
            api_version = os.environ.get('AZURE_OPENAI_API_VERSION')
        if provider.lower() == 'gemini':
            url = api_version = None
            api_key = os.environ.get('GEMINI_API_KEY')
        if provider.lower() == 'anthropic':
            url = api_version = None
            api_key = os.environ.get('ANTHROPIC_API_KEY')
        else:
            raise NotImplementedError
    else: # o.w. verify server
        print (f'RUN ARRAY: {vllm_url}, {model_name}')
        url = vllm_url
        api_key = api_version = None
        resp = requests.get(f"{vllm_url}/models")
        resp.raise_for_status()
        model_id = resp.json()["data"][0]["id"]
        assert _HF_MODEL_TO_URL[model_name] == model_id, f"{_HF_MODEL_TO_URL[model_name]} =!= {model_id}\nresp: {resp.json()}"
    # build players
    players = [
        OnlineAI(
            player_id=i, 
            username=name, 
            lobby_name=f"self_play_{model_name}", 
            password="", 
            avatar="", 
            url=url, 
            model_name=model_name, 
            api_key=api_key,
            provider=provider,
            api_version=api_version,
            summarization_level=2,
            theme_name=theme
        ) for i, name in enumerate(PLAYER_NAMES)
    ]
    game_id = random.randint(0, 1000000)
    config = {
        'total_missions': 3,
        'events_per_mission': 5,
        'theme': theme,
        'debug_mode': True,
        'turn_based_chat': True,
        'save_trace': True,
        'seed': game_id,
    }

    mgr = GameManager(players, **config)
    mgr.start_mission()
    pending = mgr.advance_game_to_next_action()
    state = mgr.get_state()

    while not state['game_over']:
        actions = await asyncio.gather(*[
            players[pid].perform_action(acts, state)
            for pid, acts in pending.items()
        ])
        for act_list in actions:
            for a in act_list:
                mgr.process_player_action(a)
        await asyncio.sleep(0.1)
        pending, state = mgr.advance_game_to_next_action(), mgr.get_state()

    # tally
    coop = sum(isinstance(a, SelectRoleAction) and a.role=='cooperator'
               for _,a in mgr.full_action_history)
    defe = sum(isinstance(a, SelectRoleAction) and a.role!='cooperator'
               for _,a in mgr.full_action_history)

    mh = state['mission_history']
    defl  = sum(m['cooperator_found'] for m in mh)
    found = sum(m['defector_found']   for m in mh)
    sabnf = sum(m['sabotage_successful'] and not m['defector_found'] for m in mh)
    rtnof = sum(not m['mission_complete'] and not m['defector_found'] for m in mh)

    print(f"[{model_name}/{theme}] coop={coop}, def={defe}")
    with open(f'llm_game_results_{game_id}.csv','a', newline='') as f:
        csv.writer(f).writerow(
            [model_name, theme, len(mh), coop, defe, defl, found, sabnf, rtnof]
        )

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model",  type=str, default='gemma3', choices=_HF_MODEL_TO_URL.keys())
    p.add_argument("--theme",  type=str, default='default')
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--vllm_url", type=str, default=None)
    p.add_argument("--api", action='store_true', help='if the model is proprietary (api)')
    p.add_argument("--provider", type=str, choices=["azure", "gemini", "anthropic"], default=None)
    return p.parse_args()

async def main():
    args = parse_args()
    if not args.vllm_url and not args.api:
        model_url = _HF_MODEL_TO_URL[args.model]
        proc = start_vllm(model_url, args.port)
        args.vllm_url = f"http://localhost:{port}/v1"
    else:
        proc = None
    try:
        for _ in range(5):
            await run_one(args.model, args.theme, args.vllm_url, args.api, args.provider)
    finally:
        if proc:
            proc.terminate()
            proc.wait()

if __name__=="__main__":
    asyncio.run(main())