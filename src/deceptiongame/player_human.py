"""
Online Player Module for "Measuring Deception" Board Game
-----------------------------------------------------------
This module implements the OnlinePlayer component, a non-blocking version of a player.
It inherits from PlayerInterface and simply returns values provided by the UI or forwards
them to the backend. No blocking calls (like input()) are used.
"""

import requests
import asyncio
from typing import Dict, Any
from deceptiongame.players import PlayerInterface
from deceptiongame.online_game_manager import (    
    SelectRoleAction,
    PlayCardAction,
    DiscardableCardAction,
    DiscussionAction,
    NominatePlayerAction,
    VoteAction
)
from deceptiongame.tracer import log_action, Tracer


class OnlineHuman(PlayerInterface):
    def __init__(
        self,
        player_id: int, 
        username: str, 
        lobby_name: str, 
        password: str, 
        avatar: str,
        url: str = "http://127.0.0.1:8000",
        tracer: Tracer = None
    ):
        """
        Initializes the OnlinePlayer.

        :param player_id: Unique identifier for the player.
        :param username: The player's username.
        :param lobby_name: The lobby (game) the player is in.
        :param password: The password for the lobby.
        """
        super().__init__(player_id, username)
        self.username = username
        self.lobby_name = lobby_name
        self.lobby_ready = False
        self.password = password
        self.role = None  # to be set via select_role
        self.hand = []    # should be updated via game logic (or backend)
        self.url = url
        self.nomination = None
        self.vote_choice = None
        self.is_leader = False
        self.avatar = avatar
        self.played_card = None
        self.tracer = tracer
        
    def select_role(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Non-blocking role selection.
        Expects the caller (UI) to supply the player's chosen role in context.
        
        :param context: Should include "selected_role" and "available_roles".
        :return: A dictionary with the selected role.
        """
        selected = context.get("selected_role")
        available = context.get("available_roles", [])
        if selected not in available:
            return {"error": "Invalid role selection."}
        self.role = selected
        # (Optional) You could post the role selection to a backend endpoint here.
        return {"role": selected}

    def play_card(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Non-blocking card play.
        Expects the caller (UI) to supply the card chosen to play.
        
        :param context: Should include "selected_card".
        :return: A dictionary with the played card.
        """
        card = context.get("selected_card")
        if not card:
            return {"error": "No card selected."}
        else:
            self.played_card = card
            self.hand.pop(self.hand.index(card))
        
        # Optionally update the player's hand or call a backend endpoint here.
        # For example, if an endpoint for playing a card existed, you might do:
        # payload = {
        #     "lobby_name": self.lobby_name,
        #     "username": self.username,
        #     "card": card
        # }
        # requests.post(f"{BACKEND_URL}/play_card", json=payload)
        return {"card": card}
    
    def select_card_as_leader(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prompts the human player to choose one of the two drawn cards.
        
        :param context: Dictionary expected to include "cards": list of available cards.
        :return: Dictionary containing the played card, e.g., {"card": "+1"}.
        """
        assert self.is_leader
        message = context['message']
        payload = {
            "lobby_name": self.lobby_name,
            "username": self.username,
            "password": self.password,
            "message": message
        }
        res = requests.post(f"{self.url}/select_event_card", json=payload)
        if res.status_code == 200:
            return {"message": message}
        else:
            return {"error": "Failed to send card choice."}
                
    def participate_in_discussion(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Non-blocking discussion participation.
        Expects the discussion message to be provided by the caller.
        
        :param context: Should include "message".
        :return: A dictionary with the discussion message.
        """
        message = context.get("message")
        if not message:
            return {"error": "No message provided."}
        # Forward the message to the backend chat endpoint.
        payload = {
            "lobby_name": self.lobby_name,
            "username": self.username,
            "password": self.password,
            "message": message
        }
        res = requests.post(f"{self.url}/add_message", json=payload)
        if res.status_code == 200:
            return {"message": message}
        else:
            return {"error": "Failed to send message."}

    def nominate_player(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Non-blocking nomination.
        Expects that the caller supplies the nominated player's ID.
        
        :param context: Should include "nominated_player_id".
        :return: A dictionary with the nominated player's ID.
        """
        nominated = context.get("nominated_player_username")
        if nominated is None or not self.is_leader:
            return {"error": "No player nominated."}
        self.nominated = nominated
        return {"nominated_player_username": nominated}

    def vote(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Non-blocking voting.
        Expects that the caller supplies the vote ("yes" or "no").
        
        :param context: Should include "vote" with value "yes" or "no".
        :return: A dictionary with the vote.
        """
        vote_choice = context.get("vote")
        if vote_choice not in ("yes", "no"):
            return {"error": "Invalid vote."}
        self.vote_choice = vote_choice
        return {"vote": vote_choice}

    def receive_message(self, message: Dict[str, Any]) -> None:
        """
        Receives a message from the backend.
        Simply appends the message to the internal queue.
        """
        self.message_queue.append(message)

