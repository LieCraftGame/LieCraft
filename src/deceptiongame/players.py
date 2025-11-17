import abc
import random
from typing import Dict, Any, List
from deceptiongame.actions import * 
from deceptiongame.tracer import log_action, Tracer
import logging
logging.basicConfig(
    level=logging.INFO,
    format="\n%(message)s"
)
logger = logging.getLogger(__name__)


class PlayerInterface(abc.ABC):
    """
    Abstract base class defining the interface for a player.
    All player types (human or AI) must implement the following methods.
    """

    def __init__(self, player_id: int, name: str):
        """
        Initializes the player with an ID and name.

        :param player_id: Unique identifier for the player.
        :param name: The player's name.
        """
        self.player_id = player_id
        self.name = name
        self.hand = []
        self.is_leader = False
        self.vote_choice = None
        self.role = None
        self.vote_choice = None
        self.nominated = None
        self.nomination = None
        self.selected_card = None
        self.is_ai = False
        
        # Message queue for discussion messages; each player may maintain their own queue.
        self.message_queue: List[Dict[str, Any]] = []
        
    #return player_id for attribute pid
    @property
    def pid(self) -> int:
        return self.player_id

    @abc.abstractmethod
    def select_role(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Selects a role for the current mission based on the provided context.

        :param context: JSON-like dictionary containing role selection parameters (e.g., payoff matrix, available roles).
        :return: A dictionary in a standardized format containing the selected role.
        Example output: {"role": "Cooperator"}
        """
        pass

    @abc.abstractmethod
    def play_card(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plays a card during an encounter based on the given context.

        :param context: JSON-like dictionary containing encounter context (e.g., player hand, game state).
        :return: A dictionary in a standardized format indicating the played card.
        Example output: {"card": "+1"}
        """
        pass
    

    
    @abc.abstractmethod
    def participate_in_discussion(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Participates in the discussion phase by submitting a message.

        :param context: JSON-like dictionary containing discussion context (e.g., revealed cards, timer info).
        :return: A dictionary with the player's discussion message.
        Example output: {"message": "I believe my card was played honestly."}
        """
        pass

    @abc.abstractmethod
    def nominate_player(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Nominates a player for voting based on the discussion context.

        :param context: JSON-like dictionary containing nomination context (e.g., available_players).
        :return: A dictionary containing the nominated player's ID.
        Example output: {"nominated_player_id": 2}
        """
        pass

    @abc.abstractmethod
    def vote(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Casts a vote in the nomination process.

        :param context: JSON-like dictionary containing voting context (e.g., nomination details).
        :return: A dictionary containing the vote, standardized as either "yes" or "no".
        Example output: {"vote": "yes"}
        """
        pass

    def receive_message(self, message: Dict[str, Any]) -> None:
        """
        Receives a discussion message from another player and appends it to the message queue.

        :param message: A JSON-like dictionary representing the message.
        Example: {"sender_id": 2, "message": "I think Player 3 is suspicious."}
        """
        self.message_queue.append(message)
        logger.info("Player %d received message: %s", self.player_id, message)
    
    def set_hand(self, context: Dict[str, Any]):
        """
        Sets hand 
        """
        self.hand = context['hand'][:]
        
    def get_hand(self) -> Dict[str, Any]:
        """
        gets hand
        """
        return {'hand': self.hand}
    
    def full_reset(self):
        self.partial_reset()
        self.role = None
        self.hand = []
        
    def partial_reset(self):
        self.vote_choice = None
        self.nominated = None
        self.nomination = None
        self.is_leader = False
        self.selected_card = None
        self.played_card = None

class DummyPlayer(PlayerInterface):
    """
    Dummy implementation of the PlayerInterface for testing and demonstration purposes.
    This implementation uses simple deterministic behavior.
    """

    def __init__(self, player_id: int, name: str, role: str = "Cooperator"):
        super().__init__(player_id, name)
        self.role = (
            role  # Preset role; in a real game, this would be assigned secretly.
        )
        
    
    def select_role(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dummy role selection that returns the preset role.
        """
        logger.info(
            "Player %d (%s) selects role: %s", self.player_id, self.name, self.role
        )
        return {"role": self.role}

    def play_card(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dummy card play: selects the first card from hand.

        :param context: Not used.
        """
        #context.get("hand", [])
        if not self.hand:
            logger.warning(
                "Player %d (%s) has an empty hand.", self.player_id, self.name
            )
            selected_card = None
        else:
            selected_card = self.hand.pop(0)  # Deterministically select the first card.
        logger.info(
            "Player %d (%s) plays card: %s", self.player_id, self.name, selected_card
        )
        return {"card": selected_card}

    def participate_in_discussion(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dummy discussion participation that returns a canned message.

        :param context: Contains discussion context such as revealed cards.
        """
        message = f"Player {self.player_id} ({self.name}) says: I stand by my actions."
        logger.info(
            "Player %d participates in discussion with message: %s",
            self.player_id,
            message,
        )
        return {"message": message}

    def nominate_player(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dummy nomination: simply nominates the next player by ID.
        Assumes context includes a list of available player IDs.
        """
        available_players = context.get("available_players", [])
        available_ids = [a[0] for a in available_players]
        if not available_ids:
            logger.error(
                "No available player IDs for nomination by Player %d.", self.player_id
            )
            nominated_id = None
        else:
            # For demonstration, nominate the first ID that is not self.
            nominated_id = next(
                (pid for pid in available_ids if pid != self.player_id), None
            )
        logger.info("Player %d nominates Player %s.", self.player_id, nominated_id)
        return {"nominated_player_id": nominated_id}

    def vote(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dummy voting logic: votes "yes" if the player's ID is even, otherwise "no".
        """
        vote_choice = "yes" if self.player_id % 2 == 0 else "no"
        logger.info("Player %d votes: %s", self.player_id, vote_choice)
        return {"vote": vote_choice}

    def select_card_as_leader(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dummy card selection (first card)
        """
        return {"card": context['cards'][0]}

# RandomPlayer class that implements the player interface with random choices.
class RandomPlayer(PlayerInterface):
    @log_action(phase='selectrole')
    def select_role(self, context: Dict[str, Any]) -> Dict[str, Any]:
        roles = ["cooperator", "defector"]#, "jester"]
        return SelectRoleAction(self.player_id, random.choice(roles))
        #return {"role": random.choice(roles)}
    
    @log_action(phase='playcard')
    def play_card(self, context: Dict[str, Any], discardable=False) -> Dict[str, Any]:
        if not self.hand:
            raise ValueError("No cards in hand to play.")
        
        if discardable:
            #return {"card": random.choice(self.hand), "discard": random.choice([True, False])}
            return DiscardableCardAction(self.player_id, random.choice(self.hand), random.choice([True, False]))
        else:
            return PlayCardAction(self.player_id, random.choice(self.hand))

            #return {"card": random.choice(self.hand), "discard":  False}
    
    def select_card_as_leader(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.hand:
            return {"card": None}
        return {"card": random.choice(self.hand)}
    
    @log_action(phase='discussion')  
    def participate_in_discussion(self, context: Dict[str, Any]) -> Dict[str, Any]:
        messages = ["I played my card.", "Let's see how it goes.", "I trust my luck."]
        return DiscussionAction(self.player_id, random.choice(messages))
        # return {"message": random.choice(messages)}
    
    @log_action(phase='nominate')  
    def nominate_player(self, context: Dict[str, Any]) -> Dict[str, Any]:
        available = context.get("available_players", [])
        choices = [pid for pid in available if pid != self.player_id]
        nominated = random.choice(choices) if choices else self.player_id
        return NominatePlayerAction(self.player_id, nominated)
        #return {"nominated_player_id": nominated}
    
    @log_action(phase='vote')
    def vote(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return VoteAction(self.player_id, random.choice(['yes', 'no']))
        #return {"vote_choice": random.choice(["yes", "no"])}

# --------------------------------------------------------------------
# Example Integration and Usage
# --------------------------------------------------------------------
if __name__ == "__main__":
    # Create a list of dummy players.
    players: List[PlayerInterface] = [
        DummyPlayer(1, "Alice"),
        DummyPlayer(2, "Bob"),
        DummyPlayer(3, "Charlie"),
    ]

    # Example usage of the PlayerInterface methods.
    # Role selection context (e.g., available roles, payoff matrix, etc.)
    role_context = {
        "available_roles": ["Cooperator", "Defector"],#, "Jester"],
        "payoff_matrix": {"dummy": True},
    }
    for player in players:
        selected = player.select_role(role_context)
        print(f"Player {player.player_id} selected role: {selected}")

    # Simulate card play: each player is provided a hand in the context.
    card_context = {"hand": ["+1", "0", "-1"]}
    for player in players:
        played = player.play_card(card_context)
        print(f"Player {player.player_id} played card: {played}")

    # Simulate discussion participation.
    discussion_context = {"revealed_cards": ["Card_1", "Card_2", "Card_3"]}
    for player in players:
        discussion_message = player.participate_in_discussion(discussion_context)
        print(f"Player {player.player_id} discussion message: {discussion_message}")

    # Simulate nomination.
    nomination_context = {"available_player_ids": [1, 2, 3]}
    for player in players:
        nomination = player.nominate_player(nomination_context)
        print(f"Player {player.player_id} nominated: {nomination}")

    # Simulate voting.
    vote_context = {"nomination_details": {"nominated_player_id": 2}}
    for player in players:
        vote = player.vote(vote_context)
        print(f"Player {player.player_id} vote: {vote}")

    # Simulate receiving a discussion message.
    sample_message = {"sender_id": 2, "message": "I think Player 3 is suspicious."}
    players[0].receive_message(sample_message)
    print(f"Player 1's message queue: {players[0].message_queue}")
