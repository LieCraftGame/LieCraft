import requests
import random
import time

from deceptiongame.players import RandomPlayer

BASE_URL = "http://localhost:8008"
LOBBY_NAME = "test_lobby"
PASSWORD = "test_password"
PLAYERS = ["Alice", "Bob", "Charlie"]

player_objects = {}

def safe_post(url, json):
    try:
        response = requests.post(url, json=json)
        if response.status_code != 200:
            print(f"[{response.status_code}] Error from {url}")
            print("Response body:", response.text)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        print("HTTPError:", e)
        if response is not None:
            print("Full response content:", response.text)
        return response

def run_integration_test():
    # Create lobby
    try:
        lobby_response = safe_post(
            f"{BASE_URL}/create_lobby",
            json={"lobby_name": LOBBY_NAME, "password": PASSWORD}
        )
    except requests.exceptions.HTTPError as e:
        out_exc = e.response
    #breakpoint()
    if lobby_response.status_code == 400:
        print("Lobby already exists, continuing with the test.")
    elif lobby_response.status_code != 200:
        print("Failed to create lobby:", out_exc)
        return
    
    # Join players and create their random player objects.
    for username in PLAYERS:
        if lobby_response.status_code != 400:
            response = safe_post(
                f"{BASE_URL}/join_lobby",
                json={
                    "lobby_name": LOBBY_NAME,
                    "username": username,
                    "password": PASSWORD,
                    "avatar": ""
                }
            )
            assert response.status_code == 200, f"Failed to join {username}"
        player_objects[username] = RandomPlayer(name=username, player_id=username)

    # Start game
    response = safe_post(
        f"{BASE_URL}/start_game",
        json={"lobby_name": LOBBY_NAME, "restart": True}
    )
    assert response.status_code == 200, "Failed to start game"

    # Game loop
    max_iterations = 100
    for _ in range(max_iterations):
        # Advance game state
        next_action_response = safe_post(
            f"{BASE_URL}/get_next_action",
            json={"lobby_name": LOBBY_NAME}
        )
        next_action_data = next_action_response.json()
        
        print("\nGame State Update:")
        print(f"Summary: {next_action_data.get('summary', '')}")
        print(f"Pending Actions: {next_action_data.get('pending_actions', [])}")

        game_state = next_action_data.get("game_state", {})
        if game_state.get("game_over"):
            print("Game Over!")
            break
        
        # Process pending actions
        for action_msg in next_action_data.get("pending_actions", []):
            process_action(action_msg)
        time.sleep(0.5)  # Delay to simulate interactions

    # Print final scores
    game_state = safe_post(
        f"{BASE_URL}/get_game_state",
        json={"lobby_name": LOBBY_NAME}
    ).json()
    print("\nFinal Scores:")
    print(game_state.get("game_state", {}).get("cumulative_scores", "No scores found"))

def process_action(action_msg: str):
    # When an action is received, we extract the username (assumed to be the first token)
    tokens = action_msg.split()
    username = tokens[1]

    # Action: select a role
    if "select a role" in action_msg:
        context = {}
        role_data = player_objects[username].select_role(context)
        role = role_data["role"]
        safe_post(
            f"{BASE_URL}/set_player_role",
            json={
                "lobby_name": LOBBY_NAME,
                "username": username,
                "role": role
            }
        )
        print(f"{username} selected role: {role}")

    # Action: play a card
    elif "play a card" in action_msg:
        hand_response = safe_post(
            f"{BASE_URL}/get_player_hand",
            json={"lobby_name": LOBBY_NAME, "username": username}
        )
        hand = hand_response.json().get("hand", [])
        player_objects[username].hand = hand  # update the player's hand for decision making
        card_data = player_objects[username].play_card({})
        card = card_data["card"]
        if card is not None:
            safe_post(
                f"{BASE_URL}/play_card",
                json={
                    "lobby_name": LOBBY_NAME,
                    "username": username,
                    "card": card
                }
            )
            print(f"{username} played card: {card}")
        else:
            print(f"{username} has no card to play.")

    # Action: nominate a player
    elif "nominate a player" in action_msg:
        #breakpoint()
        # Get current leader from game state
        game_state = safe_post(
            f"{BASE_URL}/get_game_state",
            json={"lobby_name": LOBBY_NAME}
        ).json().get("game_state", {})
        
        
        
        # Extract the leader from game_state['player_info']
        leader = next(player["username"] for player in game_state["player_info"] if player["is_leader"])
        # Prepare context with the available players (excluding leader)
        context = {"available_players": [p for p in PLAYERS if p != leader]}
        nomination_data = player_objects[leader].nominate_player(context)
        nominated = nomination_data["nominated_player_id"]
        safe_post(
            f"{BASE_URL}/set_nomination",
            json={
                "lobby_name": LOBBY_NAME,
                "username": leader,
                "nomination": nominated
            }
        )
        print(f"{leader} nominated: {nominated}")

    # Action: vote
    elif "vote" in action_msg:
        context = {}
        vote_data = player_objects[username].vote(context)
        vote_choice = vote_data["vote_choice"]
        safe_post(
            f"{BASE_URL}/set_vote",
            json={
                "lobby_name": LOBBY_NAME,
                "username": username,
                "vote": vote_choice
            }
        )
        print(f"{username} voted: {vote_choice}")

if __name__ == "__main__":
    run_integration_test()