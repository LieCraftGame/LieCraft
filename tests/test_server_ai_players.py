import requests
import random
import time

from deceptiongame.players import RandomPlayer

BASE_URL = "http://localhost:8008"
LLM_URL = "http://localhost:9000/v1"
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
                f"{BASE_URL}/add_bot",
                json={
                    "lobby_name": LOBBY_NAME,
                    "username": username,
                    "password": PASSWORD,
                    "url": LLM_URL,
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
        
        time.sleep(0.5)  # Delay to simulate interactions

    # Print final scores
    game_state = safe_post(
        f"{BASE_URL}/get_game_state",
        json={"lobby_name": LOBBY_NAME}
    ).json()
    print("\nFinal Scores:")
    print(game_state.get("game_state", {}).get("cumulative_scores", "No scores found"))


if __name__ == "__main__":
    run_integration_test()