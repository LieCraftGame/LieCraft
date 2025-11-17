import os
import sys
import uuid
import numpy as np
import torch
import random
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from dataclasses import dataclass
from collections import Counter
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union, ClassVar, Tuple
import logging
logging.basicConfig(
    level=logging.INFO,
    format="\n%(message)s"
)
logger = logging.getLogger(__name__)


def seed_everything(seed: int):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    try:
        from transformers import set_seed as transformers_set_seed
        transformers_set_seed(seed)
    except ImportError:
        pass
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
seed_everything(42)

from deceptiongame.players import PlayerInterface
from deceptiongame.actions import * 
from deceptiongame.mission_manager import Mission
from deceptiongame.decks import ActionDeck, EventDeck, MissionDeck
from deceptiongame.tracer import Tracer
from deceptiongame.players import RandomPlayer
from deceptiongame.state_loader import *

# The GameManager remains largely the same except that pending_actions now holds action classes.
class GameManager:
    def __init__(
        self,
        players: List[Any],
        total_missions: int,
        events_per_mission: int = 5,
        n_sabotages_needed_per_defector: int = 3,
        debug_mode: bool = False,
        turn_based_chat: bool = False,
        save_trace: bool = False,
        load_action_trace: bool = False,
        replay_to: Tuple[int] | None = None,
        theme: str = 'default',
        seed: int = 42,
        multiplayer=False,
    ):
        if not players:
            raise ValueError("At least one player is required to start the game.")
        
        self.leader_rotation = 'player_id'
        if self.leader_rotation == 'alphabetical':
            self.players = sorted(players, key=lambda x: x.name)
        elif self.leader_rotation == 'player_id':
            self.players = sorted(players, key=lambda x: x.player_id)
        else:
            self.players = players
        self.theme = theme
        self.seed = seed   
        self.debug_mode = debug_mode
        if self.debug_mode:
            print("Debug Mode Set")
        self.pending_actions: Dict[int, List[type]] = {}
        self.action_deck = ActionDeck(total_cards=len(self.players) * 10, seed=seed)
        self.total_missions = total_missions
        self.mission_deck = MissionDeck(
            num_players=len(self.players),
            theme=theme,
            seed=seed,
            deck_size=self.total_missions,
            events_per_mission=events_per_mission
        )

        self.leader_rotation = 'player_id'
        self.current_mission = 1
        self.cumulative_scores = {p.player_id: 0 for p in self.players}
        self.last_leader = None
        self.turn_based_chat = turn_based_chat
        self.last_chat_phase = 'none'
        self.player_card_selection_order = None
        #self.n_sabotages_needed_per_defector = n_sabotages_needed_per_defector

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        suff = uuid.uuid4().hex[:6]
        if multiplayer:
            log_dir = 'multiplayer_game_logs'
        else:
            log_dir = 'game_logs'
        os.makedirs(log_dir, exist_ok=True)
        trace_save_path = os.path.join(log_dir, f"{timestamp}-{suff}-{theme}.json")
        self.save_trace = save_trace
        self.tracer = Tracer(
            config={
                'total_missions': total_missions,
                'events_per_mission': events_per_mission,
                'debug_mode': self.debug_mode,
                'turn_based_chat': True,
                'seed': seed,
                'theme': theme,
                'players': [{
                    'player_id': p.player_id, 
                    'username': p.name, 
                    'avatar': p.avatar if hasattr(p, 'avatar') else None,
                    'url': p.url if hasattr(p, 'url') else None,
                    'model_name': p.model_name if hasattr(p, 'model_name') else None,
                    'api_key': p.api_key if hasattr(p, 'api_key') else None,
                    'temperature': p.temperature if hasattr(p, 'temperature') else None,
                } for p in self.players]
            },
            prompt_templates={
                'system_prompt': self.players[0]._build_system_prompt() if hasattr(self.players[0], 'avatar') else "",
            },
            save_path=trace_save_path,
            save_trace=save_trace
        )
        if load_action_trace:
            # store game info
            tracer_game_id, tracer_started_at = self.tracer.trace['game_id'], self.tracer.trace['started_at']
            self.tracer = Tracer.load_from_file(load_action_trace)
            # self.tracer._is_enabled = False
            logger.info(f'Loaded game trace from {load_action_trace}')
            self.tracer._trace_save_path = load_action_trace.replace('.json', '.new.json')
            self.tracer.trace['game_id'] = tracer_game_id
            self.tracer.trace['started_at'] = tracer_started_at
        self._replay_to_mission, self._replay_to_event = replay_to if load_action_trace else (None, None)
        self._replay_ptr = 0 if load_action_trace else None
        self._replay_pre_mission_ptr = 0 if load_action_trace else None # {
        #    "ptr": 0 if load_action_trace else None,
        #    "num_actions": [len(m['actions']) for m in self.tracer['missions']]
        #}
        
        for player in self.players:
            player.tracer = self.tracer
            
        self.full_action_history = []
        self.full_event_history = []
        self.mission_history = []
        self.num_rerolls = 0
        self.max_rerolls = 25
        
    def player_from_id(self, pid: int) -> PlayerInterface | None:
        for player in self.players:
            if player.player_id == pid:
                return player
        return None

    def rotate_leader(self) -> PlayerInterface:
        current_leader = self.last_leader
        
        #we sort in init
        sorted_players = self.players
        new_leader = (sorted_players[0] if current_leader is None
                      else sorted_players[(sorted_players.index(current_leader) + 1) % len(sorted_players)])
        for p in self.players:
            p.is_leader = (p == new_leader)
            
        leader = next((p for p in self.players if getattr(p, "is_leader", False)))
        leader_index = self.players.index(leader)
        self.player_card_selection_order = self.players[leader_index:] + self.players[:leader_index]
        return new_leader
    
    def get_players_by_leader(self) -> Dict[str, List[PlayerInterface]]:
        #returns a list of players with leader as first
        leader = next((p for p in self.players if getattr(p, "is_leader", False)))
        leader_index = self.players.index(leader)
        return self.players[leader_index:] + self.players[:leader_index]

    def get_state(self) -> Dict[str, Any]:
        player_info = [{
            "player_id": player.player_id,
            "name": player.name,
            "role": getattr(player, "role", None),
            "role_default_theme": getattr(player, "role_default_theme", None),
            "is_leader": getattr(player, "is_leader", False),
            "selected_card": getattr(player, "selected_card", None),
            "hand": getattr(player, "hand", None),
            "nomination": getattr(player, "nomination", None),
            "vote_choice": getattr(player, "vote_choice", None),
            "username": getattr(player, "username", None),
            "score": getattr(self.cumulative_scores, str(player.player_id), None),
            
        } for player in self.players]
        mission_state = self.mission.get_mission_state() if hasattr(self, 'mission') else {}
        
        return {
            'player_info': player_info, 
            'cumulative_scores': self.cumulative_scores,
            "game_over": self.game_over(), 
            'total_missions': self.total_missions,
            'full_action_history' : self.full_action_history,     
            'full_event_history': self.full_event_history,
            'mission_history': self.mission_history, 
            **mission_state
            }

    def start_mission(self):  
        self.mission_card = self.mission_deck.draw_mission_card()
        self.event_deck = EventDeck(num_players=len(self.players), deck_size=self.mission_card.events_per_mission, seed=self.seed, theme=self.theme)
        self.mission = Mission(
            self.mission_card,
            self.event_deck, 
            mission_id=self.current_mission,
            tracer=self.tracer)
        self.tracer.start_mission(self.current_mission, self.mission.payoff_matrix)

    def cleanup_mission(self, mission_end_state: Dict[str, Any]):
        self.full_event_history.extend(self.mission.event_results)
        self.mission_history.append(mission_end_state)
        
    def game_over(self) -> bool:
        return self.current_mission > self.total_missions
    
    def clear_game(self):
        raise ValueError("Not implemented yet")
        for p in self.players:
            p.full_reset()
        self.event_deck = None
        self.mission = None
        self.current_mission = 1
        self.cumulative_scores = {p.player_id: 0 for p in self.players}
        self.last_leader = None
    
    def quit_game(self):
        self.tracer.finish_game(
            outcome={'scores': self.cumulative_scores}
        )
        print("Game Over")
        if self.save_trace:
            self.tracer.save_trace_to_json() 
        
    def advance_game_to_next_action(self) -> Dict[int, List[type]]:
        pending = {}
        for _ in range(20):
            pending = self._advance_game()
            
             # 2) if chat is off, strip out any DiscussionAction
            if not self.turn_based_chat:
                raise ValueError("Not implemented yet")
                for pid, actions in pending.items():
                    pending[pid] = [act for act in actions if act is not DiscussionAction]
            
                # remove empty actions
                pending = {pid: actions for pid, actions in pending.items() if actions}
                # if all players have no actions, break
            
            if self.game_over(): 
                return {}
            if pending: break
            
        if not pending: 
            raise ValueError("No pending actions after 20 steps")
       
        # 3) stash and return
        self.pending_actions = pending
        return pending
    
    def get_pending_actions(self) -> Dict[int, List[type]]:
        return self.pending_actions
    
    def _advance_game(self) -> Dict[int, List[type]]:
        req_actions: Dict[int, List[type]] = {}
        if self.save_trace:
            self.tracer.save_trace_to_json()
        if not hasattr(self, 'mission'):
            self.start_mission()
        current_state = self.get_state()
        # Step 1: Role selection
        #check if all players are cooperators and force em to pick again
        if any(p["role"] is None for p in current_state['player_info']):
            for p in current_state['player_info']:
                if p["role"] is None:
                    req_actions.setdefault(p["player_id"], []).append(SelectRoleAction)
            logger.debug('[_advance_game] Players need to select their role')
            return req_actions
        else:
            logger.debug(f"Roles: {[p['role'] for p in current_state['player_info']]}")
            
        if all(p["role_default_theme"] == "defector" for p in current_state['player_info']):
            for p in current_state['player_info']:
                p["role"] = None
                req_actions.setdefault(p["player_id"], []).append(SelectRoleAction)
        
            print ('[_advance_game] Making players pick again')
            self.num_rerolls += 1
            if self.num_rerolls > self.max_rerolls:
                self.quit_game()
                return 'quit_game'
            else:
                print (f'Rerolling {self.num_rerolls}/{self.max_rerolls}')
            return req_actions
        
        # Step 2: Leader check and hand distribution
        if not any(getattr(p, "is_leader", False) for p in self.players):
            leader = self.rotate_leader()
            logger.debug(f'[_advance_game] Rotated leader to {leader.name}')
        else:
            logger.debug(f"is_leader: {[p['is_leader'] for p in current_state['player_info']]}")
            
            
        # new mechanic
        # give a hand to the leader
        # the leader picks 1 card
        # the leader discards 1 card at random
        # then the leader gives the rest of the hand to the next player
        # repeat until there's only 1 player left
        if not self.mission.event_started:
            logger.debug('starting new event')
            self.mission.start_new_event()
            self._replay_ptr = 0
            #get id of leader
            #leader = next((p for p in self.players if getattr(p, "is_leader", False)))
            #leader_index = self.players.index(leader)
            #order is circular starting from the leader
            #self.player_card_selection_order = self.players[leader_index:] + self.players[:leader_index]
        
       
        #give the hand to the next player in the order
        if len(self.player_card_selection_order) > 0:
            # get player who has a card to play
            current_player = self.player_card_selection_order[0]
            
            # check if player has a card to play
            if current_player.selected_card:
                move_to_next_player = self.mission.advance_event_step(current_player.selected_card)
                current_player.selected_card = None
                # played card
                if move_to_next_player: 
                    current_player.hand = []
                    self.player_card_selection_order.pop(0)
                    return {} #
                # else, they discarded
                
            #give the hand to the player
            current_player.hand, card_action_type = self.mission.get_current_cards()
            #remove the player from the order
            logger.debug(f'[_advance_game] Gave hand {self.mission.event_hand} to {current_player.name}')
            req_actions.setdefault(current_player.player_id, []).append(card_action_type)
            return req_actions
        
        self.mission.compute_event_outcome()

        #check for chats:
        # this is a defeault dict of lists per player id
        min_chats = min([len(self.mission.post_event_chat[p.pid] ) for p in self.players])
        max_chats = max([len(self.mission.post_event_chat[p.pid] ) for p in self.players])
        self.last_chat_phase = 'post_event'
        # all players who have less than max chats get a chat action
        if min_chats < self.mission.post_event_max:
            for player in self.get_players_by_leader():
                chats = self.mission.post_event_chat[player.pid]
                # check if its their turn
                if len(chats) == min_chats:
                    req_actions.setdefault(player.pid, []).append(DiscussionAction)
                    logger.debug("[_advance_game] players need to chat POST EVENT")
                    return req_actions

        # all players have played their cards, but voting/pointing not done yet
        nomination_needed = any(p.get("nomination") is None for p in current_state["player_info"])
        vote_needed = any(p.get("vote_choice") is None for p in current_state["player_info"])
        is_final_event = self.mission.events_complete()
        
        logger.debug(f'nomination needed: {nomination_needed}')
        logger.debug(f'vote needed: {vote_needed}')
        logger.debug(f'IS FINAL EVENT: {is_final_event}')
        logger.debug(f'CHAT PHASE: {self.last_chat_phase}')

        if not is_final_event and vote_needed:
            for p in current_state["player_info"]:
                if p.get("vote_choice") is None:
                    req_actions.setdefault(p["player_id"], []).append(VoteAction)
            logger.debug("[_advance_game] players need to vote")
            return req_actions
        
        #check if players voted to retreat
        withdraw_from_mission = self.mission.retreat_mission(current_state['player_info'])
        '''if self.turn_based_chat:
            min_chats = min([len(self.mission.post_vote_chat[p.pid] ) for p in self.players])
            self.last_chat_phase = 'post_vote'
            if min_chats < 1:  # TODO reset to 3
                for player in self.get_players_by_leader():
                    chats = self.mission.post_vote_chat[player.pid]
                    # check if its their turn
                    if len(chats) == min_chats:
                        req_actions.setdefault(player.pid, []).append(DiscussionAction)
                        print("[_advance_game] players need to chat POST VOTE")
                        return req_actions'''

                
        end_of_mission = is_final_event or withdraw_from_mission
        if self.debug_mode:
            logger.debug(f'[DEBUG] end of mission??: {end_of_mission} -- ({is_final_event} or {withdraw_from_mission})')
        if end_of_mission and nomination_needed:
            #nomination chat
            if self.turn_based_chat:
                min_chats = min([len(self.mission.pre_nomination_chat[p.pid] ) for p in self.players])
                self.last_chat_phase = 'pre_nomination'
                # all players who have less than max chats get a chat action
                if min_chats < self.mission.pre_nomination_max: # TODO RESET TO 3
                    for player in self.get_players_by_leader():
                        chats = self.mission.pre_nomination_chat[player.pid]
                        # check if its their turn
                        if len(chats) == min_chats:
                            req_actions.setdefault(player.pid, []).append(DiscussionAction)
                            logger.debug("[_advance_game] players need to chat")
                            return req_actions
            
            
            for p in current_state["player_info"]:
                if p.get("nomination") is None:
                    req_actions.setdefault(p["player_id"], []).append(NominatePlayerAction)
            logger.debug("[_advance_game] players need to nominate")
            return req_actions
        
        #quick error handling
        players_voted = all([p.get("vote_choice") for p in current_state['player_info']])
        players_nominated = all([p.get("nomination") != None for p in current_state['player_info']])
        if not players_voted and not players_nominated: raise ValueError("Unhandled state: all players have not voted and nominated")
        
        #players have played their cards, and voted (and nominated): event is finished 
        if players_nominated:
            self.mission.resolve_nomination(current_state['player_info'])
        else:
            self.mission._resolve_event()
        
        if not end_of_mission:
            logger.debug("[_advance_game] retreat vote failed. Start new event with no change")
            # self.mission.resolve_event(current_state['player_info'])
            
            self.last_leader = None
            for p in self.players:
                if getattr(p, "is_leader", False):
                    self.last_leader = p
                    break
            for player in self.players:
                player.partial_reset()
                logger.debug(f'Partially resetting {player}')
            return {}
        
        
        votes = [p['vote_choice'] for p in current_state['player_info']]
        logger.debug(f'[_advance_game] Votes are in!: {votes}')
        nominations = [(p['name'], p['nomination']) for p in current_state['player_info']]
        logger.debug(f'[_advance_game] Nominations: {nominations}')
            
        self._replay_pre_mission_ptr = 0
        scores_breakdown, mission_end_state = self.mission.calculate_final_mission_scores(self.players) # potentially a score change
        for pid, score in scores_breakdown.items():
            self.cumulative_scores[pid] += score
        self.tracer.record_mission_scores(self.cumulative_scores)
        if self.debug_mode:
            logger.debug(f"[_advance_game] mission over. Current score: {self.cumulative_scores}")
            for pid, score in self.cumulative_scores.items():
                logger.debug(f'\t {self.player_from_id(pid).name}: {score}')
            
        # Reset per-event player attributes
        self.last_leader = None
        for p in self.players:
            if getattr(p, "is_leader", False):
                self.last_leader = p
                break
        for p in self.players:
            p.full_reset()
        
        self.tracer.end_mission()
        # If mission events are complete, advance mission
        self.current_mission += 1
        
        # utilties that help showing final mission progress to front-end before it get wiped on new mission init
        self.cleanup_mission(mission_end_state)
        
        if self.game_over():
            self.tracer.finish_game(
                outcome={'scores': self.cumulative_scores}
            )
            logger.debug("Game Over")
            if self.save_trace:
                self.tracer.save_trace_to_json()
        else:
            self.start_mission()
        return {}             

    def process_player_action(self, action: GameAction, replay: Tuple[int] | bool = False) -> Dict[str, Any]:
        # Check that the player's action type is pending
        pending = self.pending_actions.get(action.player_id, [])
        logger.debug(f"[DEBUG] Processing action {type(action).__name__} for player {action.player_id}")
        logger.debug(f"[DEBUG] Current pending actions for player {action.player_id}: {[act.__name__ for act in pending]}")

        if replay:
            game_progressed = (
                (self.mission.mission_id - 1) >= self._replay_to_mission
                and (self.mission.mission_event_idx - 1) >= self._replay_to_event
            )
            if not game_progressed:
                print ('[In Replay]')
                pre_event_actions = len(self.tracer.trace['missions'][self.mission.mission_id-1]['actions'])
                event = self.tracer.trace["missions"][self.mission.mission_id-1]["events"][self.mission.mission_event_idx-1]
                if self._replay_pre_mission_ptr < pre_event_actions:
                    print ('pre mission ptr: ', self._replay_pre_mission_ptr)
                    ev = self.tracer.trace['missions'][self.mission.mission_id-1]
                    try:
                        entry = ev['actions'][self._replay_pre_mission_ptr]
                    except:
                        breakpoint()
                    self._replay_pre_mission_ptr += 1
                else:
                    print ('ptr value: ', self._replay_ptr)
                    entry = event["actions"][self._replay_ptr]
                    self._replay_ptr += 1

                phase     = entry["phase"]
                player_id = entry["player_id"]
                payload   = entry["payload"]
                if phase == "note_to_self" or phase == pending[0].phase:
                    pass
                else:
                    breakpoint()
                    raise ValueError(f"Phase mismatch: expected {pending[0].phase}, got {phase}")
                # map your trace phases → your dataclass constructors
                cls = {
                    "select_role":   SelectRoleAction,
                    "play_card":     (DiscardableCardAction if "is_discard" in payload else PlayCardAction),
                    "discussion":    DiscussionAction,
                    "nominate":      NominatePlayerAction,
                    "vote":          VoteAction,
                    "note_to_self":  NoteToSelfAction,
                }[phase]
                # rehydrate the exact same action object they originally took
                action = cls(player_id=player_id, **payload)
                print(f"[REPLAY] Injected action: {phase} by P{player_id} → {payload}")
                # Log the action
            else:
                self.tracer._is_enabled = True            
        if type(action) in pending or isinstance(action, NoteToSelfAction):
            pass
        else:
            logger.debug(f"[DEBUG] Action {type(action).__name__} not found in pending actions {[act.__name__ for act in pending]}")
            raise ValueError(f"Action {type(action).__name__} is not pending for player {action.player_id}")
        player = next((p for p in self.players if p.player_id == action.player_id), None)
        if player is None:
            raise ValueError("Invalid player_id")
        # Dispatch based on action type
        if isinstance(action, SelectRoleAction):
            player.role = action.role
            player.role_default_theme = action.role_default_theme
        elif isinstance(action, DiscardableCardAction) or isinstance(action, PlayCardAction):
            if action.card not in player.hand:
                breakpoint()
                raise ValueError("Card not in hand")
            player.selected_card = action
            logger.debug(f'[DEBUG] player {player}, selected card {action.card} action {action}')
        elif isinstance(action, DiscussionAction):
            player.discussion_input = action.message
            if self.turn_based_chat:
                self.mission.add_chat_message(player.player_id, action.message)
        elif isinstance(action, NominatePlayerAction):
            player.nomination = action.nominated_player_id
        elif isinstance(action, VoteAction):
            player.vote_choice = action.vote_choice
        elif isinstance(action, NoteToSelfAction):
            player.scratchpad.append(action.note)
        else:
            raise ValueError("Unhandled action type")
        
        # Log the action
        self.full_action_history.append((player.player_id, action))
        
        # Remove the processed action from pending actions
        self.pending_actions[action.player_id] = [
            act for act in self.pending_actions[action.player_id] if act != type(action)
        ]

# Test code for running the game manager from start to finish.
if __name__ == "__main__":
    # Create a list of RandomPlayers.
    players = [ RandomPlayer(0, "Alice"), 
                RandomPlayer(1, "Bob"), 
                RandomPlayer(2, "Charlie"),
                RandomPlayer(3, "David"),
                RandomPlayer(4, "Eve")]
    payoff_matrix = {
        "starting_points_defector": 1,
        "mission_complete": 5,
        "mission_sabotaged": 10,
        "defector_found": 5, 
        "cooperator_found": -5,
        "n_sabotages_needed_per_defector": 3
        }
    
    save_trace = True
    load_action_trace = False

    if load_action_trace:
        load_action_trace = browse_json_files()
        mission_to_load, event_to_load = state_browser(load_action_trace)
    else:
        mission_to_load, event_to_load = None, None
    print (f'loading to mission {mission_to_load} and event {event_to_load}')
    import time
    time.sleep(3)
        
    gm = GameManager(
        players, 
        total_missions=3, 
        turn_based_chat=True,  
        debug_mode=False,
        save_trace=save_trace,
        load_action_trace=load_action_trace,
        replay_to=(mission_to_load, event_to_load),
        seed=42)
    gm.start_mission()
    
    # Run a loop to process pending actions.
    while not gm.game_over():  # fixed number of iterations for testing
        pending = gm.advance_game_to_next_action()
        if pending == 'quit_game':
            break
        #pending = gm.get_pending_actions()
        for player in players:
            actions = pending.get(player.player_id, [])
            
            for action in actions:
                if action.__name__ == "SelectRoleAction":
                    act = player.select_role({})
                    #act = SelectRoleAction(player.player_id, res["role"])
                elif action.__name__ == "DiscardableCardAction":
                    act = player.play_card({}, discardable=True)
                    #act = DiscardableCardAction(player.player_id, res["card"], res['discard'])
                elif action.__name__ == "PlayCardAction":
                    act = player.play_card({})
                    #act = PlayCardAction(player.player_id, res["card"])
                elif action.__name__ == "NominatePlayerAction":
                    available_ids = [p.player_id for p in players]
                    act = player.nominate_player({"available_players": available_ids})
                    #act = NominatePlayerAction(player.player_id, res["nominated_player_id"])
                elif action.__name__ == "VoteAction":
                    act = player.vote({})
                    #res = {"vote_choice":"no"}
                    #act = VoteAction(player.player_id, res["vote_choice"])
                elif action.__name__ == "DiscussionAction":
                    act = player.participate_in_discussion({})
                    #act = DiscussionAction(player.player_id, res["message"])
                else:
                    raise ValueError("Unhandled action type ", action.__name__)
                    continue
                
                #print("player ", player.player_id, "actions: ", act)
                if load_action_trace:
                    replay = True
                else:
                    replay = None
                gm.process_player_action(act, replay=replay)
    print("Final Game scores:")
    print(gm.cumulative_scores)
    
    test_write_out_to_csv = True
    if test_write_out_to_csv == False:
        exit(0)
    import csv
    coop_count = 0
    def_count = 0
    for i, cur_action in gm.full_action_history:
        if isinstance(cur_action, SelectRoleAction):
            print (f'Action {i}: ', cur_action)
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
    for end_mission_dict in gm.get_state()['mission_history']: 
        total += 1
        if end_mission_dict['cooperator_found']:
            deflected_count += 1
        if end_mission_dict['defector_found']:
            defector_found_count += 1
        if end_mission_dict['sabotage_successful'] and not end_mission_dict['defector_found']:
            defector_sabotage_unfound_count += 1
        if not end_mission_dict['mission_complete'] and not end_mission_dict['defector_found']:
            retreated_no_def_found += 1
    print (f'Cooperators found: {deflected_count} ')
    print (f'Defectors found: {defector_found_count}')
    print (f'Defectors sabotaged but not found: {defector_sabotage_unfound_count} ')
    with open('llm_game_results.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([total, coop_count, def_count, deflected_count, defector_found_count, defector_sabotage_unfound_count, retreated_no_def_found])
    