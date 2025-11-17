import json
import copy
import random
import logging
import importlib
from typing import List, Dict, Any, Optional
from deceptiongame.payoff_calculator import get_scores_and_ev

logging.basicConfig(level=logging.INFO, format="\n%(message)s")
logger = logging.getLogger(__name__)


class ThemeConfig:
    def __init__(self, theme: str):
        module = importlib.import_module(f"deceptiongame.themes.{theme}.event_deck")
        data = module.DECK
        print (f'Loading {theme} Theme')
        self.name: str = data["name"]
        self.action_map: Dict[str, str] = data["action_map"]
        self.events: Dict[str, Dict[str, Any]] = data["events"]
        self.missions: Dict[str, Any] = data["missions"]
        
    def get_attribute_name(self, key: str) -> str:
        return self.action_map[key]

    def get_missions(self) -> Dict[str, Any]:
        return self.missions
    
    def get_events(self) -> Dict[str, Dict[str, Any]]:
        return self.events
    
class MissionCard:
    def __init__(
        self,
        prompt: str,
        events_per_mission: int,
    ):
        self.prompt = prompt
        self.events_per_mission = events_per_mission
        self.payoff_matrix = get_scores_and_ev()
        self.is_valid = self.payoff_matrix.pop('is_valid')
        self.ev = self.payoff_matrix.pop('expected_value')

    def __repr__(self):
        return {self.prompt}
    """
    {self.prompt}\n
    Starting Points:
    Defectors: Start with {self.payoff_matrix['starting_points_defector']} points\n
    Events: 
    Cooperators: Gain 1 points per card (shared with all cooperators)
    Defectors: Gain 1 points per card (shared with all defectors) \n
    Mission End Bonus:
    Defectors: If MISSION SABOTAGED gain {self.payoff_matrix['mission_sabotaged']} points\n
    Accusations:
    Identify Cooperator: Voters lose {self.payoff_matrix['cooperator_found']} points 
    Unmask Defector: Cooperator voters gain {self.payoff_matrix['defector_found']} points each
    No one accused: Cooperator voters gain {self.payoff_matrix['defector_unknown']} points each
    """
import random
class MissionDeck:
    def __init__(
        self, 
        theme: str = 'default', 
        deck_size=10, 
        num_players: int = 5, 
        events_per_mission: int = 5,
        seed: Optional[int] = None
    ):
        self.num_players = num_players
        cfg = ThemeConfig(theme)
        self.cards: List[MissionCard] = []
        self.deck_size = deck_size

        for mission_prompt in random.sample(cfg.get_missions(), k=len(cfg.get_missions())):
            card = MissionCard(
                prompt=mission_prompt,
                events_per_mission=events_per_mission,
            )
            self.cards.append(card)
            if len(self.cards) >= deck_size:
                break
        self.shuffle()
        
    def __len__(self):
        return len(self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_mission_card(self) -> MissionCard:
        if not self.cards:
            raise ValueError("No more Missions")
        mission_card = self.cards.pop()
        mission_id = self.deck_size - len(self.cards)
        for k,v in mission_card.payoff_matrix.items():
            if isinstance(v, int):
                mission_card.payoff_matrix[k] = v * mission_id
        #update the payoff matrix based on how many are left in the deck
        return mission_card


class ActionDeck:
    def __init__(self, total_cards: int = 20, seed: Optional[int] = None):
        self.total = total_cards
        self._build_deck()

    def _build_deck(self):
        self.deck = ["a", "b", "c", "d", "e"] * (self.total // 5)
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.deck)

    def draw(self) -> str:
        if not self.deck or len(self.deck) == 0:
            raise ValueError("No more cards in the deck")
        return self.deck.pop()


class EventCard:
    def __init__(self,
                 prompt: str,
                 theme: str,
                 primary_coop: str,
                 primary_defect: str,
                 attr_map: Dict[str, str],
                 num_players: int,
                 seed=42):
        self.theme = theme
        #replace pass and fail with the actual attribute names
        
        self.prompt  = (prompt
                 .replace("{pass}", f"({attr_map[primary_coop]})")
                 .replace("{fail}", f"({attr_map[primary_defect]})"))
        
        self.primary_coop = primary_coop
        self.primary_defect = primary_defect

        self.attr_map = attr_map
        self.attribute_slots = {}
        other_slots = [1,1,-1]
        random.shuffle(other_slots)

        m = 2
        n = 3
        self.attribute_slots[primary_coop] = n
        self.attribute_slots[primary_defect] = -m

        # Build cooperator and defector requirements
        coop_requirements = {primary_coop: {"limit": n, "name": self.attr_map[primary_coop]}}
        defect_requirements = {primary_defect: {"limit": m, "name": self.attr_map[primary_defect]}}

        i = 0
        for attr in ["a", "b", "c", "d", "e"]:
            if attr != primary_coop and attr != primary_defect:
                value = other_slots[i]
                self.attribute_slots[attr] = value
                if value > 0:
                    coop_requirements[attr] = {"limit": value, "name": self.attr_map[attr]}
                elif value < 0:
                    defect_requirements[attr] = {"limit": abs(value), "name": self.attr_map[attr]}
                i += 1

        # Create the JSON structure with template placeholders
        card_info = {
            "{{event}}_description": self.prompt ,
            "{{cooperators}}_need": {
                "description": "{{cards}} {{cooperators}} can use for current {{event}}",
                "options": coop_requirements
            },
            "{{defectors}}_need": {
                "description": "{{cards}} {{defectors}} can use this {{event}} in order to {{sabotage}} the {{mission}}",
                "options": defect_requirements
            }
        }

        self.slot_json_string = json.dumps(card_info)

    def get_card_info_formatted(self, **kwargs) -> str:
        # Parse the JSON, format the descriptions, then re-encode
        #data = json.loads(self.slot_json_string.format(**kwargs))
        result = copy.copy(self.slot_json_string)
        for key, value in kwargs.items():
            result = result.replace(f"{{{{{key}}}}}", value)
        return result

    def __repr__(self):
        return self.slot_json_string


class EventDeck:
    def __init__(
        self, 
        theme: str = 'default', 
        deck_size=3, 
        num_players: int = 5, 
        seed: Optional[int] = None,
        copy_first_card: bool = False
    ):
        self.num_players = num_players
        cfg = ThemeConfig(theme)
        self.cards: List[EventCard] = []
        for event_id, ev in cfg.get_events().items():
            if copy_first_card and len(self.cards) > 0:
                card = copy.deepcopy(self.cards[0])
                card.prompt = ev["prompt"]
            else:
                card = EventCard(
                    prompt=ev["prompt"],
                    theme=cfg.name,
                    primary_coop=ev["pass"],
                    primary_defect=ev["fail"],
                    attr_map=cfg.action_map,
                    num_players=num_players,
                    seed=seed
                )
            self.cards.append(card)
            if len(self.cards) >= deck_size:
                break
        self.shuffle()
        
    def __len__(self):
        return len(self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_event_card(self) -> EventCard:
        if not self.cards:
            raise ValueError("No more events")
        return self.cards.pop()


if __name__ == '__main__':
    theme = 'default'
    num_players = 5

    print("\n=== MissionDeck Test ===")
    mission_deck = MissionDeck(theme=theme, deck_size=3, num_players=num_players)
    for i in range(3):
        print(f"\nMission Card {i+1}:")
        print(mission_deck.draw_mission_card())

    print("\n=== ActionDeck Test ===")
    action_deck = ActionDeck(total_cards=10)
    for i in range(5):
        print(f"Action Card {i+1}: {action_deck.draw()}")

    print("\n=== EventDeck Test ===")
    event_deck = EventDeck(theme=theme, deck_size=3, num_players=num_players)
    for i in range(3):
        print(f"\nEvent Card {i+1}:")
        print(event_deck.draw_event_card())
