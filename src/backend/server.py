import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from deceptiongame.online_game_manager import GameManager, GameAction
from deceptiongame.actions import *
from deceptiongame.players import PlayerInterface
from deceptiongame.player_human import OnlineHuman
from deceptiongame.player_llm   import OnlineAI
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.head("/")
@app.get("/")
def index() -> Response:
    with open("src/frontend/index_tabbed.html", "r") as f:
        data = f.read()
    return Response(content=data, media_type="text/html")


# Global storage for all game/lobby instances.
games: Dict[str, "Game"] = {}
# Game class represents a lobby and a running game.
class Game:
    def __init__(self, lobby_name: str, password: str):
        self.lobby_name = lobby_name
        self.password = password
        self.players: List[PlayerInterface] = []
        self.started = False  # False means lobby is open to new players.
        self.lobby_chat: List[Dict[str, str]] = []
        self.game_chat: List[Dict[str, str]] = []
        self.game_manager = None
        self.game_config = {
            'total_missions': 2,
            'events_per_mission': 3,
            'debug_mode': True,
            'theme': 'hospital',
            'turn_based_chat': True,
            'seed': 43,
            # 'mission_config_path': 'src/deceptiongame/themes/event_deck_fantasy.json'
        }

    def start_game(self):
        self.game_manager = GameManager(
            self.players,
            **self.game_config
        )
        self.game_manager.start_mission()
    
    def advance_game(self):
        return self.game_manager.advance_game_to_next_action()
        
    def get_lobby_status(self):
        if not self.started or not self.game_manager:
            status = 'Waiting for Game to Start...'
        else:
            status = 'Game Started, Enter Now!'
        return status
    
    def get_scores(self):
        if self.game_manager is None:
            scores = {i: 0 for i in range(len(self.players))}
        else:
            scores = self.game_manager.cumulative_scores
        return scores
    
    def get_game_status(self):
        if not self.started or not self.game_manager:
            status = 'Waiting for Game to Start...'
        else:
            status = self.game_manager.get_state()
        return status
        
    def add_lobby_message(self, username: str, message: str):
        self.lobby_chat.append({"username": username, "message": message})
    
    def add_game_message(self, username: str, message: str):
        self.game_chat.append({"username": username, "message": message})
    
    def add_human_player(self, username: str, url: str | None = None, avatar: str = ''):
        player = OnlineHuman(
            player_id=len(self.players),
            username=username,
            lobby_name=self.lobby_name,
            password=self.password,
            url=url,
            avatar=avatar,
        )
        self.players.append(player)
        return player.player_id
        
    def add_ai_player(
        self, 
        username: str, 
        url: str | None = None, 
        avatar: str = '',
        model_name: str = None,
        api_key: str = None,
        temperature: float = 1.0):
        player = OnlineAI(
            player_id=len(self.players),
            username=f'{username}',
            lobby_name=self.lobby_name,
            password=self.password,
            avatar=avatar,
            url=url,
            model_name=model_name,
            temperature=temperature,
            api_key=api_key,
        )
        self.players.append(player)
        return player.player_id
        
    def initialize_game_manager(self):
        self.game_manager = GameManager(
            self.players,
            **self.game_config['total_missions'],
        )
        
# Pydantic models for request validation.
class CreateLobbyRequest(BaseModel):
    lobby_name: str
    password: str

class JoinLobbyRequest(BaseModel):
    lobby_name: str
    username: str
    password: str
    avatar: str
    url: str = None
    model_name: str = None
    temperature: float = None
    api_key: str = None
    system_prompt: str = None

class LeaveLobbyRequest(BaseModel):
    lobby_name: str
    username: str
    
class LobbyRequest(BaseModel):
    lobby_name: str
    username: str
    
@app.post("/create_lobby")
async def create_lobby(req: CreateLobbyRequest):
    print(f'create lobby: {req}')
    active_lobbies = [game.lobby_name for game in games.values()]    
    if req.lobby_name in active_lobbies:
        raise HTTPException(status_code=400, detail="Lobby already exists.")
    games[req.lobby_name] = Game(req.lobby_name, req.password)
    return {"message": f"Lobby '{req.lobby_name}' created."}


@app.post("/join_lobby")
async def join_lobby(req: JoinLobbyRequest):
    print(f'join lobby: {req}')
    active_lobbies = [game.lobby_name for game in games.values()]    
    if req.lobby_name not in active_lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found.")
    game = games[req.lobby_name]
    if game.password != req.password:
        raise HTTPException(status_code=403, detail="Incorrect password.")
    if game.started:
        raise HTTPException(status_code=400, detail="Game already started; no new players allowed.")
    # check player base
    usernames = [player.username for player in game.players]
    if req.username in usernames:
        raise HTTPException(status_code=400, detail="User already in lobby.")
    player_id = game.add_human_player(req.username, url=None, avatar=req.avatar)
    return {"message": f"{req.username} joined lobby '{req.lobby_name}'."}


@app.post("/add_bot")
async def add_bot(req: JoinLobbyRequest):
    print(f'join lobby: {req}')
    active_lobbies = [game.lobby_name for game in games.values()]    
    if req.lobby_name not in active_lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found.")
    game = games[req.lobby_name]
    if game.password != req.password:
        raise HTTPException(status_code=403, detail="Incorrect password.")
    if game.started:
        raise HTTPException(status_code=400, detail="Game already started; no new players allowed.")
    # check player base
    usernames = [player.username for player in game.players]
    if req.username in usernames:
        raise HTTPException(status_code=400, detail="User already in lobby.")
    if None in [req.model_name, req.url, req.temperature]:
        raise HTTPException(status_code=405, detail='Bad params passed')
    
    player_id = game.add_ai_player(
        req.username, 
        url=req.url, 
        avatar=req.avatar,
        model_name=req.model_name,
        temperature=float(req.temperature),
        api_key=req.api_key)
    return {"message": f"{req.username} joined lobby '{req.lobby_name}'."}

@app.post("/leave_lobby")
async def leave_lobby(req: LeaveLobbyRequest):
    active_lobbies = [game.lobby_name for game in games.values()]    
    if req.lobby_name not in active_lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found.")
    game = games[req.lobby_name]
    if req.username not in game.players:
        raise HTTPException(status_code=400, detail="User not in lobby.")
    game.players.remove(req.username)
    return {"message": f"{req.username} left lobby '{req.lobby_name}'."}


@app.post("/lobby_ready")
async def lobby_ready(req: LobbyRequest):
    active_lobbies = [game.lobby_name for game in games.values()]    
    if req.lobby_name not in active_lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found.")
    game = games[req.lobby_name]
    usernames = [p.username for p in game.players]
    if req.username not in usernames:
        raise HTTPException(status_code=400, detail="User not in lobby.")
    for player in game.players:
        if player.username == req.username:
            player.lobby_ready = True
            break
    return {"message": f"{req.username} is ready'."}


@app.get("/lobbies")
async def get_lobbies():
    output = {}
    for name, game in games.items():
        scores = game.get_scores()
        players_to_store = []
        for pid, score in scores.items():
            for player in game.players:
                if player.player_id == pid:
                    player.score = score    
                    if isinstance(player, OnlineAI):
                        player.is_llm = True
                        player.lobby_ready = True                    
                    else:
                        player.is_llm = False
                    players_to_store.append({
                        'username': player.username,
                        'avatar': player.avatar,
                        'role': player.role,
                        'is_leader': player.is_leader,
                        'lobby_ready': player.lobby_ready,  
                    })
                    print (players_to_store[-1])
        output[name] = {"players": players_to_store, "started": game.started}
    return {"lobbies": output}


# GAME Management
class StartGameRequest(BaseModel):
    lobby_name: str
    restart: bool

class StopGameRequest(BaseModel):
    lobby_name: str
    username: str

class GetGameStateRequest(BaseModel):
    lobby_name: str
    
    
class GetStateRequest(BaseModel):
    lobby_name: str
    username: str
    password: str
    
    
@app.post("/start_game")
async def start_game(req: StartGameRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Lobby not found.")
    game = games[req.lobby_name]
    if game.started and not req.restart:
        state = game.get_game_status()
        payoff_matrix = state['payoff_matrix']
        mission_text = state['mission_text']
        return {
            "message": f"{req.lobby_name} is already started! Go to Game tab!",
            "payoff_matrix": payoff_matrix,
            "mission_text": mission_text
        }  
    elif req.restart:
        game.clear_game()      
    if len(game.players) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 players to join")
    
    game.start_game()
    game.started = True
    state = game.get_game_status()
    payoff_matrix = state['payoff_matrix']
    mission_text = state['mission_text']
    return {
        "message": f"{req.lobby_name} is started! Go to Game tab!",
        # "payoff_matrix": payoff_matrix,
        "mission_text": mission_text
    }


@app.post("/stop_game")
async def stop_game(req: StopGameRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Lobby not found.")
    game = games[req.lobby_name]
    if not game.started:
        raise HTTPException(status_code=400, detail="Game not started.")
    game.game_manager = None
    game.started = False
    return {"msg": "game stopped"}

@app.post("/get_chat")
async def get_state(req: GetStateRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Lobby not found.")
    game = games[req.lobby_name]
    if req.username not in game.players:
        raise HTTPException(status_code=403, detail="User not in lobby.")
    if not game.started:
        raise HTTPException(status_code=400, detail="Game not started.")
    return {"chat": game.game_chat}


@app.post("/get_game_state")
async def get_game_state(req: GetGameStateRequest):
    lobby_name = req.lobby_name
    game = games[lobby_name]
    status = game.get_game_status()
    return {'game_state': status}


@app.post("/get_lobby_state")
async def get_lobby_state(req: GetGameStateRequest):
    lobby_name = req.lobby_name
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Lobby not found.")
    game = games[lobby_name]
    status = game.get_lobby_status()
    return {'lobby_state': status}


# Chat Rooms
class GetMessageRequest(BaseModel):
    lobby_name: str
    password: str
    
class SetMessageRequest(BaseModel):
    lobby_name: str
    username: str
    password: str
    message: str

@app.post("/add_lobby_message")
async def add_lobby_message(req: SetMessageRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Lobby not found.")
    game = games[req.lobby_name]
    usernames = [player.username for player in game.players]
    if req.username not in usernames:
        raise HTTPException(status_code=403, detail="User not in lobby.")
    game.add_lobby_message(req.username, req.message)
    return {"message": "Message added."}


@app.post("/get_lobby_message")
async def get_lobby_message(req: GetMessageRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Game not game.")
    game = games[req.lobby_name]
    return {"chat": game.lobby_chat}


@app.post("/add_game_message")
async def add_game_message(req: SetMessageRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Game not found.")
    game = games[req.lobby_name]
    usernames = [player.username for player in game.players]
    if req.username not in usernames:
        raise HTTPException(status_code=403, detail="User not in game.")
    if not game.started:
        raise HTTPException(status_code=400, detail="Game not started.")
    
    player = next((p for p in game.players if p.username == req.username), None)  
    try:
        action = DiscussionAction(player.player_id, req.message)
        game.game_manager.process_player_action(action)
        return {"message": "Chat message sent successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))  


@app.post("/get_game_message")
async def get_game_message(req: GetMessageRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="game not found.")
    game = games[req.lobby_name]
    if not game.started:
        raise HTTPException(status_code=400, detail="Game not started.")
    state = game.get_game_status()  # Assumes this returns a useful state string
    chat = state['chat_history']
    for msg_dict in chat:
        if 'username' not in msg_dict:
            msg_dict['username'] = game.game_manager.player_from_id(msg_dict['player_id']).username
    return {"chat": chat}


class PlayerRequest(BaseModel):
    lobby_name: str
    username: str

@app.post("/get_player_hand")
async def get_player_hand(req: PlayerRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=400, detail="Game not found.")
    game = games[req.lobby_name]
    
    # Find player by username
    player = next((p for p in game.players if p.username == req.username), None)
    if not player:
        raise HTTPException(status_code=400, detail="User not found.")
    
    return {"hand": player.hand}

class GameActionRequest(BaseModel):
    lobby_name: str
    username: str

class SelectRoleRequest(GameActionRequest):
    role: str

@app.post("/set_player_role")
async def set_player_role(req: SelectRoleRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Game not found.")
    
    game = games[req.lobby_name]
    if not game.game_manager:
        raise HTTPException(status_code=400, detail="Game not started.")
    
    # Find player by username
    player = next((p for p in game.players if p.username == req.username), None)
    if not player:
        raise HTTPException(status_code=404, detail="User not found.")
    
    try:
        action = SelectRoleAction(player.player_id, req.role)
        game.game_manager.process_player_action(action)
        return {"message": "Role selected successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class PlayCardRequest(GameActionRequest):
    card: str

@app.post("/play_card") # works for both play from hand or discard + play
async def play_card(req: PlayCardRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Game not found.")
    
    game = games[req.lobby_name]
    if not game.game_manager:
        raise HTTPException(status_code=400, detail="Game not started.")
    
    player = next((p for p in game.players if p.username == req.username), None)
    if not player:
        raise HTTPException(status_code=404, detail="User not found.")
    
    try:
        action = PlayCardAction(player.player_id, req.card)
        game.game_manager.process_player_action(action)
        return {"message": "Card played successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class DiscardCardRequest(GameActionRequest):
    lobby_name: str
    username: str
    card: str
    is_discard: bool
    
@app.post("/discard_card") # works for both play from hand or discard + play
async def play_card(req: DiscardCardRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Game not found.")
    
    game = games[req.lobby_name]
    if not game.game_manager:
        raise HTTPException(status_code=400, detail="Game not started.")
    
    player = next((p for p in game.players if p.username == req.username), None)
    if not player:
        raise HTTPException(status_code=404, detail="User not found.")
    # check here if the card is discardable
    try:
        action = DiscardableCardAction(player.player_id, req.card, is_discard=req.is_discard)
        game.game_manager.process_player_action(action)
        return {"message": "Card discarded successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class VoteRequest(GameActionRequest):
    vote: str
    lobby_name: str
    username: str

@app.post("/set_vote")
async def set_vote(req: VoteRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Game not found.")
    
    game = games[req.lobby_name]
    if not game.game_manager:
        raise HTTPException(status_code=400, detail="Game not started.")
    
    player = next((p for p in game.players if p.username == req.username), None)
    if not player:
        raise HTTPException(status_code=404, detail="User not found.")
    print ('VOTING FOR ', player.player_id)
    print ('*'*80)
    print ('*'*80)

    try:
        action = VoteAction(player.player_id, req.vote)
        game.game_manager.process_player_action(action)
        return {"message": "Vote recorded successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class NominationRequest(GameActionRequest):
    lobby_name: str
    username: str
    nomination: str

@app.post("/set_nomination")
async def set_player_nomination(req: NominationRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Game not found.")
    
    game = games[req.lobby_name]
    if not game.game_manager:
        raise HTTPException(status_code=400, detail="Game not started.")
    
    # Find nominating player
    nominator = next((p for p in game.players if p.username == req.username), None)
    if not nominator:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Find nominated player
    if req.nomination == 'Unknown':
        nominated = 'Unknown'
    else:
        nominated = next((p.player_id for p in game.players if p.username == req.nomination), None)
    #if not nominated:
    #    raise HTTPException(status_code=404, detail="Nominated user not found.")
    print ('NOMINATION SENDING', nominator.player_id, nominated)
    try:
        action = NominatePlayerAction(nominator.player_id, nominated)
        game.game_manager.process_player_action(action)
        return {"message": "Nomination recorded successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class RetreatRequest(GameActionRequest):
    lobby_name: str
    username: str
    retreat: bool

@app.post("/set_retreat")
async def set_player_retreat(req: RetreatRequest):
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Lobby not found.")
    game = games[req.lobby_name]
    if not game.started or not game.game_manager:
        raise HTTPException(status_code=400, detail="Game not started.")
    player = next((p for p in game.players if p.username == req.username), None)
    if req.retreat:
        vote = 'yes'
    else:
        vote = 'no'
    try:
        action = VoteAction(player.player_id, vote)
        game.game_manager.process_player_action(action)
        return {"message": "Retreat vote recorded successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        breakpoint()
        

# Events
class GetGameRequest(BaseModel):
    lobby_name: str

@app.post("/get_next_action")
async def get_next_action(req: GetGameRequest):
    """
    Remember the order of game advancement is
    1. start mission
    2. block on role selection
    3. choose leader
    4. distribute hands
    5. start event
    """
    if req.lobby_name not in games:
        raise HTTPException(status_code=404, detail="Lobby not found.")
    game = games[req.lobby_name]
    if not game.started or not game.game_manager:
        raise HTTPException(status_code=400, detail="Game not started.")
    
    actions = game.game_manager.advance_game_to_next_action()
    state = game.get_game_status()  # Assumes this returns a useful state string
    last_chat_phase = game.game_manager.last_chat_phase
    chat_phase = ""
    if last_chat_phase == 'post_event':
        chat_phase_msg = 'After Event Discussion:'
    elif last_chat_phase == 'pre_nomination':
        chat_phase_msg = 'Pre Nomination Discussion:'
    elif last_chat_phase == 'post_vote':
        chat_phase_msg = 'After Vote Discussion:'

    # Translate actions into frontend-friendly messages and gather pending players
    messages = []
    role_pending = []
    card_pending = []
    discard_pending = []
    discussion_pending = []
    nomination_pending = []
    vote_pending = []
    game_over = False
    async_actions = []
    for user_id, acts in actions.items():
        username = game.players[user_id].username
        is_ai_player = game.players[user_id].is_ai
        if is_ai_player:
            print (f'[get_next_action] sending to AI {user_id} to perform {acts}')
            async_actions.append(game.players[user_id].perform_action(acts, state))
        else:
            for act in acts:
                if act.__name__ == "SelectRoleAction":
                    messages.append(f"Player {username} must select a role.")
                    role_pending.append(username)
                elif act.__name__ == "PlayCardAction":
                    messages.append(f"Player {username} must play a card.")
                    card_pending.append(username)
                elif act.__name__ == "DiscardableCardAction":
                    messages.append(f"Player {username} must discard a card.")
                    discard_pending.append(username)
                elif act.__name__ == "DiscussionAction":
                    messages.append(f"Player {username} must add to the discussion.")
                    discussion_pending.append(username)
                elif act.__name__ == "NominatePlayerAction":
                    messages.append("The leader must nominate a player.")
                    nomination_pending.append(username)
                elif act.__name__ == "VoteAction":
                    messages.append(f"Player {username} must vote.")
                    vote_pending.append(username)
                elif act.__name__ == 'GameOver':
                    messages.append(f"Game Over")
                    game_over = True
    # finalize async actions
    # print(f"[DEBUG] Collected async actions: {len(async_actions)}")
    preprocessed_ai_actions = await asyncio.gather(*async_actions)
    # print(f"[DEBUG] Preprocessed AI actions: {preprocessed_ai_actions}")
    for act_list in preprocessed_ai_actions:
        for action in act_list:
            #print(f"[DEBUG] Processing action: {action}")
            #print(f"[DEBUG] Current pending actions: {game.game_manager.pending_actions}")
            # Check if the action is still valid before processing
            player_id = action.player_id
            if player_id in game.game_manager.pending_actions:
                pending_actions = game.game_manager.pending_actions[player_id]
                action_type = type(action)
                if action_type in pending_actions:
                    try:
                        game.game_manager.process_player_action(action)
                    except ValueError as e:
                        print(f"[DEBUG] Action {action} failed: {str(e)}")
                        continue
            else:
                print(f"[DEBUG] No pending actions for player {player_id}")
    await asyncio.sleep(0.2)
    # Build a summary string for the frontend
    summary_parts = []
    if game_over: 
        summary_parts.append(f"Game over")
    if role_pending:
        summary_parts.append(f"Role selection pending for players {role_pending}")
    if card_pending:
        summary_parts.append("Waiting on card play from: " + ", ".join(card_pending))
    if discard_pending:
        summary_parts.append("Waiting on card play from: " + ", ".join(discard_pending))
    if discussion_pending:
        summary_parts.append(f"{chat_phase_msg} waiting on: " + ", ".join(discussion_pending))
    if nomination_pending:
        summary_parts.append("Waiting for Defector nominations from: " + ", ".join(nomination_pending))
    if vote_pending:
        summary_parts.append("Voting in progress: waiting on: " + ", ".join(vote_pending))
    if not summary_parts:
        summary_parts.append("All actions complete. Proceeding to next phase.")
    game_stage_summary = " -- ".join(summary_parts)
    
    scores = game.get_scores()
    print ('DEBUG SUMMARY: ', game_stage_summary)
    for pid, score in scores.items():  # attach scores
        for player in state['player_info']:
            if player['player_id'] == pid:
                   player['score'] = score   
                   player['avatar'] = game.players[pid].avatar
    #print ('Sending over mission state: ')
    #print ('MISSION STATE:\n', state)  
    print ('Counts: ', state['full_event_history'])
    print ('Mission ends: ', state['mission_history'])
    return {"pending_actions": messages, "game_state": state, "summary": game_stage_summary, "game_over": game_over}


if __name__ == "__main__":
    
    #games["default"] = Game("default", "")
    #games["default"].players = ['matt', 'musashi', 'neale']
    #games["default"].started = True
    uvicorn.run(app, host="127.0.0.1", port=8008)
