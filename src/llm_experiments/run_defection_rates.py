# test_game_manager_llm.py

import time
import asyncio
import os
import sys
import requests
import csv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from deceptiongame.online_game_manager import GameManager
from deceptiongame.player_llm import OnlineAI
from deceptiongame.actions import SelectRoleAction

#LLM_URL = "http://localhost:8081/v1"
LLM_URL = "http://isl-gpu40.rr.intel.com:8081/v1"
PLAYER_NAMES = ["Alice", "Bob", "Charlie", "David", "Eve"]

async def run_llm_direct_test():
    # 0. get the model name from the LLM_URL
    response = requests.get(f"{LLM_URL}/models")
    model_id = response.json()["data"][0]["id"]
    # model_name = "llama-3.1"# if "Llama-3.1-70B-Instruct" in model_id else model_id
    # model_name = "qwen-2.5" if "Qwen2.5-32B" in model_id else model_id
    model_name = "gemma3" if "gemma-3" in model_id else model_id
    # 1. Build AI players
    players = [
        OnlineAI(
            player_id=i,
            username=name,
            lobby_name="defection_test",
            password="",
            url=LLM_URL,
            avatar="",
            model_name=model_name,
            theme_name='ma'
        )
        for i, name in enumerate(PLAYER_NAMES)
    ]

    # 2. Dummy config matching your server
    config = {
        'total_missions': 1,
        'events_per_mission': 1,
        'theme' : 'ma', 
        'debug_mode': True,
        'turn_based_chat': True,
    }

    # 3. Instantiate manager and start
    manager = GameManager(players, **config)
    manager.start_mission()
    
    pending = manager.advance_game_to_next_action()
    state   = manager.get_state()
    while not state['game_over']:
        coros = []
        for pid, acts in pending.items():
            player = players[pid]
            print (acts)
            coros.append(player.perform_action(acts, state))
            
        all_actions = await asyncio.gather(*coros)

        # 5. process each returned action
        for act_list in all_actions:
            for action in act_list:
                manager.process_player_action(action)

        # yield so other tasks can run
        await asyncio.sleep(0.1)
        
        pending = manager.advance_game_to_next_action()
        state   = manager.get_state()
        for player in players:
            if all([p is not None for p in players]):
                state['game_over'] = True
    ## 6. report scores
    #print("Final cumulative scores:")
    #for pid, score in manager.cumulative_scores.items():
    #    print(f"  {players[pid].username}: {score}")
    
    #TODO save out printed variables to csv     
    coop_count = 0
    def_count = 0
    for i, cur_action in manager.full_action_history:
        if isinstance(cur_action, SelectRoleAction):
            #print (f'Action {i}: ', cur_action)
            if cur_action.role == 'cooperator':
                coop_count += 1
            else:
                def_count += 1
        else:
            #print (f'Action {i}: ', cur_action)
            pass
    print (f'Cooperators: {coop_count}, Defectors: {def_count}')
    
    deflected_count = 0
    defector_found_count = 0
    defector_sabotage_unfound_count = 0
    retreated_no_def_found = 0
    total = 0
    for end_mission_dict in manager.get_state()['mission_history']: 
        total += 1
        if end_mission_dict['cooperator_found']:
            deflected_count += 1
        if end_mission_dict['defector_found']:
            defector_found_count += 1
        if end_mission_dict['sabotage_successful'] and not end_mission_dict['defector_found']:
            defector_sabotage_unfound_count += 1
        if not end_mission_dict['mission_complete'] and not end_mission_dict['defector_found']:
            retreated_no_def_found += 1
    with open('llm_game_results.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([total, coop_count, def_count, deflected_count, defector_found_count, defector_sabotage_unfound_count, retreated_no_def_found])

    


async def main():
    num_games_to_run = 1
    tasks = [run_llm_direct_test() for _ in range(num_games_to_run)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())