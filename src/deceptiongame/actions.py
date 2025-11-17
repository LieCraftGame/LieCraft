from dataclasses import dataclass
from typing import ClassVar, List, Union, List

@dataclass
class SelectRoleAction:
    player_id: int
    role: str
    role_default_theme: str
    possible_roles: ClassVar[List[str]] = ["cooperator", "defector"]
    phase: ClassVar[str] = "select_role"
    def __post_init__(self):
        self.role = self.role.lower()
    

@dataclass
class PlayCardAction:
    player_id: int
    card: str
    phase: ClassVar[str] = "play_card"
    def __post_init__(self):
        if self.card not in ["a", "b", "c", "d", "e"]:
            raise ValueError("Invalid card")
        
@dataclass
class DiscardableCardAction:
    player_id: int
    card: str
    is_discard: bool = False
    phase: ClassVar[str] = "play_card"
    def __post_init__(self):
        if self.card not in ["a", "b", "c", "d", "e"]:
            raise ValueError("Invalid card")

@dataclass
class DiscussionAction:
    player_id: int
    message: str
    phase: ClassVar[str] = "discussion"
    
@dataclass
class NoteToSelfAction:
    player_id: int
    note: str
    phase: ClassVar[str] = "scratch"

@dataclass
class SummarizeAction:
    player_id: int
    summary: str
    phase: ClassVar[str] = "summarize"

@dataclass
class NominatePlayerAction:
    player_id: int
    nominated_player_id: int
    phase: ClassVar[str] = "nominate"

@dataclass
class VoteAction:
    player_id: int
    vote_choice: str
    phase: ClassVar[str] = "vote"
    
    def __post_init__(self):
        if self.vote_choice.lower() not in {"yes", "no"}:
            raise ValueError("Invalid vote")
        self.vote_choice = self.vote_choice.lower()

GameAction = Union[
    SelectRoleAction,
    PlayCardAction,
    DiscardableCardAction,
    DiscussionAction,
    NoteToSelfAction,
    NominatePlayerAction,
    VoteAction
]