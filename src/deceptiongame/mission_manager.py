import random
import math
from typing import Optional, List, Dict, Any, Tuple
from collections import defaultdict
from collections import Counter
from deceptiongame.players import PlayerInterface
from deceptiongame.decks import EventDeck, ActionDeck
from deceptiongame.actions import PlayCardAction, DiscardableCardAction
from deceptiongame.tracer import Tracer

import logging
logging.basicConfig(
  level=logging.INFO,
  format="\n%(message)s",
)
logger = logging.getLogger(__name__)


class Mission:
    def __init__(
        self, 
        mission_card: Dict[str, Any], 
        event_deck: EventDeck, 
        mission_id: int = 0,
        tracer: Tracer = None
    ):
        self.event_results: List[Dict[int, int]] = []
        self.mission_scores: Dict[int, int] = {}
        self.mission_card = mission_card
        self.events_per_mission = mission_card.events_per_mission
        self.payoff_matrix = mission_card.payoff_matrix
        self.points_per_card = mission_card.payoff_matrix['points_per_card']

        self.completed_events = 0
        self.mission_event_idx = 1
        self.event_started = False
        self.event_scored = False
        self.current_event = None
        self.event_deck = event_deck
        self.event_hand = None
        self.event_played = []
        self.post_discard_hand = None
        self.mission_id = mission_id
        
        self.event_hand = None
        self.post_discard_hand = None
        
        self.coop_scores      = 0
        self.defector_scores  = 0
        self.tracer = tracer
        self.init_chat()
        
    def init_chat(self):
        self.full_chat_history = []
        self.post_event_chat = defaultdict(list)
        #self.post_vote_chat = defaultdict(list)
        self.pre_nomination_chat = defaultdict(list)
        
        self.post_event_max = 2
        self.pre_nomination_max = 2

    def add_chat_message(self, player_id: int, message: str):
        """ Add a message to the chat history for a specific player """
        self.full_chat_history.append({
            'player_id': player_id,
            'message': message
        })
        # Add to the specific player's chat history
        #find which chat history to add to based on length of chats
        if len(self.post_event_chat[player_id]) < self.post_event_max:
            self.post_event_chat[player_id].append(message)
        #elif len(self.post_vote_chat[player_id]) < 1:
        #    self.post_vote_chat[player_id].append(message)
        elif len(self.pre_nomination_chat[player_id]) < self.pre_nomination_max:
            self.pre_nomination_chat[player_id].append(message)
        else:
            raise ValueError("Chat history is full for this player")

    def start_new_event(self):
        """ Draws an event card
        Card: {
            prompt[str]: sevent text to be displayed,
            'plus_needed'[int]: number of "+" cards needed to pass
            'minus_needed'[int]: number of '-' cards needed to pass
            'event_key'[str]: summary keyword of the event
        }
        """
        self.current_event = self.event_deck.draw_event_card()
        self.action_deck = ActionDeck()
        self.event_started = True 
        if len(self.event_results) > 0: # only increment after first event
            self.mission_event_idx += 1
        self.event_hand = sorted(["a", "b", "c","d","e"] + [self.action_deck.draw()])
        
        self.event_played = []
        self.post_event_chat = {i: [] for i in range(self.event_deck.num_players)}
        # clear votes
        self.tracer.start_event(event_id=self.mission_event_idx, card=self.current_event)
    
    def events_complete(self):
        return len(self.event_deck) == 0    
    
    def check_vote(self, votes: List[int]) -> Optional[int]:
        count = Counter(votes)
        majority_count = len(votes) // 2 + 1
        for num, freq in count.items():
            if freq >= majority_count:
                return num
        return None
    
    def get_current_cards(self):
        if self.event_hand is None:
            raise ValueError("No event hand available")
        
        if self.post_discard_hand is not None:
            return self.post_discard_hand, PlayCardAction
        return self.event_hand, DiscardableCardAction
    
    #the current player plays a card from hand
    # or they discard a card from the event hand and draw a random one to play
    def advance_event_step(self, action):
        permissible_actions = [PlayCardAction, DiscardableCardAction]
        if not any(isinstance(action, cls) for cls in permissible_actions):
            raise ValueError("Action must be an instance of PlayCardAction or DiscardableCardAction")
        selected_card = action.card

        is_discard = isinstance(action, DiscardableCardAction) and action.is_discard
        # 1. if it is a play card, remove it from the active hand and add it to event played
        if is_discard:
            self.post_discard_hand = [self.action_deck.draw(), self.action_deck.draw()]
            self.event_hand.remove(selected_card)
            return False
        elif self.post_discard_hand is None:
            #we are playing a card from the event hand
            self.event_hand.remove(selected_card)
            self.event_played.append(selected_card)
            # sort the played cards for consistency
            self.event_played = sorted(self.event_played)
        elif self.post_discard_hand is not None:
            # delete the temporary hand, play the card from the temp hand
            self.post_discard_hand = None
            self.event_played.append(selected_card)
            self.event_played = sorted(self.event_played)
        else:
            raise ValueError("Invalid state: event hand and post discard hand are both None")
        return True
    
    def compute_event_outcome(self):
        if self.event_scored: return
        slots = self.current_event.attribute_slots

        # 3. compute points
        coop_pts = 0
        defect_pts = 0
        used_coop = {}
        used_def  = {}
        for attr, capacity in slots.items():
            played = self.event_played.count(attr)
            used = min(played, abs(capacity))
            if capacity > 0:
                coop_pts += used
                used_coop[attr] = used
            else:
                defect_pts += used
                used_def[attr] = used

        # 4. store
        self.coop_scores     += (coop_pts * self.points_per_card)
        self.defector_scores += (defect_pts * self.points_per_card)
        print (self.coop_scores, self.defector_scores)
        
        self.event_scored = True
        self.tracer.end_event(
            event_id=self.mission_event_idx,
            played_cards=self.event_played,
            used_attributes={"cooperator": used_coop, "defector": used_def},
        )

    def retreat_mission(self, player_state: List[Dict[str, Any]]):
        self.vote_result = self.check_vote([player['vote_choice'] for player in player_state])
        retreat = self.vote_result == "yes"
        self.yes_vote_ids = [
            player['player_id'] for player in player_state if player['vote_choice'] == "yes"
        ]
        return retreat
    
    def _resolve_event(self, nomination: Optional[Dict[str, Any]] = None):
        counts = Counter(list(nomination.values())) if nomination else None
        event_result = {
            'event_card': self.current_event,
            'event_played': self.event_played,
            'event_hand': self.event_hand,
            'event_success_count': self.coop_scores,
            'event_fail_count': self.defector_scores,
            'vote_result': self.vote_result ,
            'yes_vote_ids': self.yes_vote_ids,
            'nomination_results': nomination,
            'nomination_counts': counts,
            'mission_id': self.mission_id
        }
        self.event_results.append(event_result)
        self.event_started = False
        self.event_scored = False
        self.current_event = None
        self.completed_events += 1
            
    def resolve_nomination(self, player_state: List[Dict[str, Any]]):
        nomination_results = {player['player_id']: player['nomination'] for player in player_state}
        self._resolve_event(
            nomination=nomination_results
        )

    def update_mission_scores(self, scores: Dict[int, int]):
        self.mission_scores = scores
    
    def get_mission_state(self) -> Dict[str, Any]:
        mission_state = {
            'event_results': self.event_results,
            'mission_scores': self.mission_scores,
            'payoff_matrix': self.payoff_matrix,
            'completed_events': self.completed_events,
            'current_event_idx': self.mission_event_idx,
            'total_events': self.events_per_mission,
            'event_started': self.event_started,
            'num_events_left': len(self.event_deck),
            'event_card': self.current_event,
            'event_hand': self.event_hand,
            'event_played': self.event_played,
            'coop_scores': self.coop_scores,
            'defector_scores': self.defector_scores,
            'mission_id': self.mission_id,
            'mission_text': self.mission_card.prompt,
            'chat_history': self.full_chat_history
        }
        return mission_state
    
    def _resolve_accusation(self, players: List[Any]) -> Tuple[Optional[Any], bool]:
        nominations = [p.nomination for p in players if p.role_default_theme == "cooperator"]
        
        # 1. drop abstentions
        valid = [pid for pid in nominations if (pid != 'Unknown')]

        # 2. no one voted
        if not valid:
            return False, False

        # 3. count and find top vote‐getter(s)
        counts = Counter(valid)
        max_votes = max(counts.values())
        top = [pid for pid, v in counts.items() if v == max_votes]

        # 4. ties mean no clear nominee
        if len(top) != 1:
            return False, False

        nominee_name = top[0]
        nominee = next((p for p in players if p.name == nominee_name), None)
        if nominee is None:
            return False, False

        # 5. check threshold and role
        threshold = len(valid) / 2
        defector_found   = (max_votes > threshold) and (nominee.role_default_theme == "defector")
        cooperator_found = (max_votes > threshold) and (nominee.role_default_theme == "cooperator")
        return defector_found, cooperator_found
    
    def calculate_final_mission_scores(
        self,
        players: List[PlayerInterface],
    ) -> Dict[int, Dict[str, int]]:
        breakdown: Dict[int, Dict[str, int]] = {}
        pm = self.payoff_matrix
        
        role_counts = Counter(p.role_default_theme for p in players)
        n_cooperators = role_counts["cooperator"]
        n_defectors = role_counts["defector"]
                
        # calculate event scores, very simple
        for player in players:   
            pid = player.player_id
            if player.role_default_theme == "cooperator":
                breakdown[pid] = 0 #pm["starting_points_cooperator"]
                breakdown[pid] += math.ceil(self.coop_scores / n_cooperators)
            elif player.role_default_theme == "defector":
                breakdown[pid] = pm["starting_points_defector"]
                breakdown[pid] += math.ceil(self.defector_scores / n_defectors)
            else:
                raise ValueError(f"Player role {player.role_default_theme} not implemented")
            
        defector_found, cooperator_found = self._resolve_accusation(players)
        mission_complete = self.events_complete()
        
        #more human-readable names for determining sabotage
        mission_incomplete    = not mission_complete
        defector_unfound      = not defector_found
        enough_sabotage_cards = self.defector_scores >= (3 * n_defectors)
        sabotage_successful = (
            (mission_incomplete and defector_unfound) or
            (mission_complete and defector_unfound and enough_sabotage_cards)
        )
        
        for player in players:
            role = player.role_default_theme
            score = 0

            # cooperators get mission‐completion bonus
            if role == "cooperator" :
                # vote outcome bonus/penalty
                if defector_found:
                    # coop bonus, defector penalty
                    score += pm["defector_found"] 
                elif cooperator_found:
                    # coop bonus, defector penalty
                    score -= pm["cooperator_found"] 
                else:
                    score += pm["defector_unknown"]

            # defectors get sabotage bonus (only if they weren’t caught)
            if role == "defector" and sabotage_successful:
                score += pm["mission_sabotaged"]

            breakdown[player.player_id] += score

        # put their name, role, score, and who they nominated
        player_info = []
        for player in players:
            player_info.append({
                'name': player.name,
                'role': player.role,
                'score': breakdown[player.player_id],
                'nomination': player.nomination if hasattr(player, 'nomination') else None
            })

        mission_end_state = {
            'cooperator_found': cooperator_found,
            'defector_found': defector_found,
            'sabotage_successful': sabotage_successful,
            'mission_complete': mission_complete,
            'player_info': player_info
        }
        return breakdown, mission_end_state
       