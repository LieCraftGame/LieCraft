#!/usr/bin/env python3
import os, sys, csv, json, time, random, asyncio, argparse, subprocess, requests
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from deceptiongame.online_game_manager import GameManager
from deceptiongame.player_llm import OnlineAI
from deceptiongame.actions import SelectRoleAction

# Optional sanity check for HF repos:
_HF_MODEL_TO_URL = {
    "llama-3.1": "meta-llama/Llama-3.1-70B-Instruct",
    "llama-3.3": "meta-llama/Llama-3.3-70B-Instruct",
    "gemma3":    "google/gemma-3-27b-it",
    "gemma3-12": "google/gemma-3-12b-it",
    "qwen-2.5":  "Qwen/Qwen2.5-32B-Instruct",
    "qwen-3":    "Qwen/Qwen3-32B",
    "deepseek-distilled-qwen":  "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    "deepseek-distilled-llama": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
}

PLAYER_NAMES = ["Alice","Bob","Charlie","David","Eve","Frank","Grace","Heidi","Ivan","Judy"]

# ---------- Player spec parsing ---------- #
def _parse_player(spec: str) -> dict:
    """
    '0:type=hf,url=http://host:port/v1,key=deepseek'
    '1:type=api,model=gpt-4o,provider=azure'
    """
    idx_part, rest = spec.split(":", 1)
    out = {"idx": int(idx_part)}
    for kv in rest.split(","):
        k, v = kv.split("=", 1)
        out[k] = v
    return out

def _players_from_env() -> list[dict]:
    pcs = int(os.getenv("PLAYER_COUNT", "0"))
    players = []
    for i in range(pcs):
        host = os.getenv(f"LLM_HOST_{i}")
        port = os.getenv(f"LLM_PORT_{i}")
        model = os.getenv(f"MODEL_{i}")
        provider = os.getenv(f"PROVIDER_{i}", "")

        if host and port: # HF/vLLM
            players.append({
                "idx": i, "type": "hf",
                "url": f"http://{host}:{port}/v1",
                "key": model or f"hf_{i}"
            })
        elif model: # API
            players.append({
                "idx": i, "type": "api",
                "model": model,
                "provider": provider
            })
    return players

# ---------- Argparse ---------- #
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--theme", type=str, default="default")
    p.add_argument("--out",   type=str, default=None,
                   help="Path to write JSON result {scores: {...}}")
    # legacy single-model flags (kept for backwards compat)
    p.add_argument("--model", type=str, default=None)
    p.add_argument("--api", action="store_true")
    p.add_argument("--provider", type=str, choices=["azure","gemini","anthropic"], default=None)
    p.add_argument("--vllm_url", type=str, default=None)
    p.add_argument("--port", type=int, default=8000)

    # NEW multi player
    p.add_argument("--player", action="append", dest="players", default=[],
                   metavar="SPEC",
                   help="IDX:type=hf,url=...,key=...  OR  IDX:type=api,model=...,provider=...")

    return p.parse_args()

# ---------- Helpers ---------- #
def _resolve_api_creds(provider: str, model_name: str):
    prov = provider.lower()
    if prov == "azure":
        return dict(
            url=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION_REASONING", "")
                if any(k in model_name for k in ("o4","o3","o1"))
                else os.environ.get("AZURE_OPENAI_API_VERSION", "")
        )
    if prov == "gemini":
        return dict(url=None, api_key=os.environ.get("GEMINI_API_KEY", ""), api_version=None)
    if prov == "anthropic":
        return dict(url=None, api_key=os.environ.get("ANTHROPIC_API_KEY", ""), api_version=None)
    raise NotImplementedError(f"provider={provider}")

def _verify_hf_url(url: str, key: str):
    resp = requests.get(f"{url}/models")
    resp.raise_for_status()
    model_id = resp.json()["data"][0]["id"]
    expected = _HF_MODEL_TO_URL.get(key)
    if expected and expected != model_id:
        raise AssertionError(f"{expected} != {model_id} (url: {url})")

def _build_online_ai(player_desc: dict, theme: str, slot: int) -> OnlineAI:
    if player_desc["type"] == "api":
        creds = _resolve_api_creds(player_desc["provider"], player_desc["model"])
        return OnlineAI(
            player_id=slot,
            username=PLAYER_NAMES[slot % len(PLAYER_NAMES)],
            lobby_name=f"self_play_{player_desc['model']}",
            password="", avatar="",
            url=creds["url"], model_name=player_desc["model"],
            api_key=creds["api_key"], provider=player_desc["provider"],
            api_version=creds["api_version"], summarization_level=2,
            theme_name=theme
        )
    else:  # hf
        _verify_hf_url(player_desc["url"], player_desc["key"])
        return OnlineAI(
            player_id=slot,
            username=PLAYER_NAMES[slot % len(PLAYER_NAMES)],
            lobby_name=f"self_play_{player_desc['key']}",
            password="", avatar="",
            url=player_desc["url"], model_name=player_desc["key"],
            api_key=None, provider=None, api_version=None,
            summarization_level=2, theme_name=theme
        )

def _compute_scores(mgr: GameManager, players: list[OnlineAI]) -> dict:
    """
    Produce {model_key: score}. Adjust to your scoring logic.
    Here we use number of successful missions contributed to by each player
    as a toy metric; replace with your real one.
    """
    # Example: each player score = count of missions where they were coop & mission_complete
    state = mgr.get_state()
    mh = state["mission_history"]
    return state['cumulative_scores']


# ---------- Game loop ---------- #
async def run_game(players: list[OnlineAI], theme: str, out_path: str|None):
    game_id = random.randint(0, 1_000_000)
    config = dict(
        total_missions=3,
        events_per_mission=5,
        theme=theme,
        debug_mode=True,
        turn_based_chat=True,
        save_trace=True,
        seed=game_id,
        multiplayer=True,
    )
    mgr = GameManager(players, **config)
    mgr.start_mission()
    pending = mgr.advance_game_to_next_action()
    state = mgr.get_state()
    loop_counter = 0
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
        #loop_counter += 1
        #if loop_counter > 2:
        #    break
    # Basic tallies (kept from your old file)
    coop = sum(isinstance(a, SelectRoleAction) and a.role=='cooperator'
               for _,a in mgr.full_action_history)
    defe = sum(isinstance(a, SelectRoleAction) and a.role!='cooperator'
               for _,a in mgr.full_action_history)
    mh = state['mission_history']
    defl  = sum(m['cooperator_found'] for m in mh)
    found = sum(m['defector_found']   for m in mh)
    sabnf = sum(m['sabotage_successful'] and not m['defector_found'] for m in mh)
    rtnof = sum(not m['mission_complete'] and not m['defector_found'] for m in mh)

    print(f"[game {game_id}] coop={coop}, def={defe}")

    # CSV append (legacy)
    with open(f'multiplayer_game_logs/llm_game_results_{game_id}.csv','a', newline='') as f:
        csv.writer(f).writerow(
            ["mixed", theme, len(mh), coop, defe, defl, found, sabnf, rtnof]
        )

    # Scores for scheduler
    scores = _compute_scores(mgr, players)
    if out_path:
        with open(out_path, "w") as fp:
            json.dump({"scores": scores}, fp)
        print(f"[game {game_id}] wrote {out_path}")

async def main():
    args = parse_args()
    # Normalize players list
    if args.players:
        players_desc = [_parse_player(s) for s in args.players]
    else:
        players_desc = _players_from_env()
        if not players_desc:
            # Legacy single model path
            if args.model is None:
                sys.exit("No players provided. Use --player or env vars.")
            if args.api:
                players_desc = [{"idx":0,"type":"api","model":args.model,"provider":args.provider}]
            else:
                url = args.vllm_url or f"http://localhost:{args.port}/v1"
                players_desc = [{"idx":0,"type":"hf","url":url,"key":args.model}]

    # Build OnlineAI list
    players = [_build_online_ai(pd, args.theme, slot=i) for i, pd in enumerate(players_desc)]
    await run_game(players, args.theme, args.out)

if __name__ == "__main__":
    asyncio.run(main())