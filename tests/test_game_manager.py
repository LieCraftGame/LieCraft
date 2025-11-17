import unittest
import random
from deceptiongame.online_game_manager import (
    GameManager,
    SelectRoleAction,
    PlayCardAction,
    NominatePlayerAction,
    VoteAction
)
from deceptiongame.players import RandomPlayer

# We'll use a DummyPlayer for simulation purposes.
class DummyPlayer(RandomPlayer):
    def __init__(self, player_id, name):
        super().__init__(player_id, name)
        self.hand = []

    # These methods will not be used since we simulate actions via the pending_actions
    def select_role(self, context): pass
    def play_card(self, context): pass
    def nominate_player(self, context): pass
    def vote(self, context): pass
    def reset(self):
        self.is_leader = False
        self.played_card = None
        self.selected_card = None
        self.vote_choice = None
        self.nominated = None
        self.nomination = None


def summarize_mission(mission_state, events, players, payoff_matrix):
    players_by_id = {p.player_id: p.name for p in players}
    initial_roles = mission_state.get(
        "initial_roles", 
        [p['role'] for p in mission_state["player_info"]]
    )
    lines = []
    lines.append("Mission Summary:")
    lines.append("- Roles: " + str(initial_roles))
    event_results = mission_state.get("event_results", [])
    event_num = 0
    running_score = [0] * len(players)
    for event in events:
        line = f"Event {event_num}: "
        line += f"\nevent: {event}\n"
        if event["vote_result"] == "yes":
            # Vote passed: indicate the revealed role and list players who voted yes.
            yes_names = [players_by_id[pid] for pid in event.get("yes_vote_ids", [])]
            line += f"Vote passed: {event['revealed_role']} found by " + ", ".join(yes_names)
        elif event["event_passed"]:
            line += "Event passed, vote failed. Gain payoff points"
        else:
            line += "Event failed, vote failed. No Points Awarded"
        # compute scores
        if event['vote_result'] == 'yes':
            re_role = event['revealed_role']
            reveal_score = payoff_matrix[f'{re_role}_found']
            reveal_score_ids = event['yes_vote_ids']
            for idx in reveal_score_ids:
                running_score[idx-1] += reveal_score 
        elif event['event_passed']:
            for i in range(len(players)):
                running_score[i] += payoff_matrix[f'{mission_state['player_info'][i]['role']}_win']
        line += f": score change: {running_score}"
        lines.append(line)
        event_num += 1
    return "\n".join(lines)


class TestGameManagerIntegration(unittest.TestCase):
    def setUp(self):
        # Create 3 dummy players.
        self.players = [DummyPlayer(1, "Alice"), DummyPlayer(2, "Bob"), DummyPlayer(3, "Charlie")]
        
    def test_full_game_random(self):
        iterations = 100  # Run many iterations
        for _ in range(iterations):
            # 5) Randomize the scoring matrix for each run.
            payoff_matrix = {
                "cooperator_win": random.randint(1, 10),
                "defector_win": random.randint(5, 15),
                "jester_win": 0,
                "cooperator_found": random.randint(-5, -1),
                "defector_found": random.randint(10, 20),
                "jester_found": random.randint(0, 10)
            }
            print ('Score Card')
            for k, v in payoff_matrix.items():
                print (k, v)
            # Create a new GameManager for this iteration (with, say, 2 missions)
            gm = GameManager(
                self.players, 
                total_missions=5, 
                payoff_matrix=payoff_matrix, 
                debug_mode=False
            )
            # Advance the game until no pending actions remain (or game is over).
            iteration = 0
            event_checks = []
            mission_summaries = []
            # Save the current mission number for detecting a mission change.
            current_mission_number = gm.current_mission
            state = gm.get_state()

            # Use a loop with an iteration cap for safety.
            while not gm.game_over() and iteration < 200:
                pending = gm.advance_game_to_next_action()
                #if gm.game_over():
                #    break
                if gm.current_mission > current_mission_number:
                    mission_summary = state
                    mission_summaries.append(mission_summary)
                    current_mission_number = gm.current_mission
                
                state = gm.get_state()
                event_number = state['completed_events'] + 1
                if len(event_checks) < event_number:
                    event_checks.append([random.random() < 0.8, 0, 0])

                # Process pending actions for each player.
                for player in self.players:
                    acts = pending.get(player.player_id, [])
                    for act in acts:
                        if act.__name__ == "SelectRoleAction":
                            # 1) Randomly assign a role.
                            role = random.choice(["cooperator", "defector", "jester"])
                            action_obj = SelectRoleAction(player.player_id, role)
                            print (f'{player.name} selected {role}')
                        elif act.__name__ == "PlayCardAction":
                            # 2) For card play, inspect the event card and decide with 50% probability to pass or fail.
                            event = gm.mission.current_event
                            plus_needed = event.get("plus_needed", 1)
                            minus_needed = event.get("minus_needed", 1)
                            pass_event, plus_played, minus_played = event_checks[-1]
                            available = player.hand[:]  # copy player's hand
                            if not available:
                                # In case no cards remain, skip action.
                                continue
                            if pass_event:
                                # Force the event to pass by trying to meet the criteria.
                                if plus_played < plus_needed and "+1" in available:
                                    card = "+1"
                                elif minus_played < minus_needed and "-1" in available:
                                    card = "-1"
                                else:
                                    card = random.choice(available)
                            else:
                                if "+1" in available:
                                    alternatives = [c for c in available if c != "+1"]
                                    card = random.choice(alternatives) if alternatives else random.choice(available)
                                elif "-1" in available:
                                    alternatives = [c for c in available if c != "-1"]
                                    card = random.choice(alternatives) if alternatives else random.choice(available)
                                else:
                                    card = random.choice(available)
                                    
                            action_obj = PlayCardAction(player.player_id, card)
                            if card == '+1':
                                event_checks[-1][1] += 1
                            else:
                                event_checks[-1][2] += 1
                            print (f'{player.name} played {card};')
                            
                        elif act.__name__ == "NominatePlayerAction":
                            # 3) Random nomination: if this pending action is for nomination (should be only for leader)
                            nominees = [p for p in self.players if p.player_id != player.player_id]
                            nominated = random.choice(nominees).player_id if nominees else player.player_id
                            action_obj = NominatePlayerAction(player.player_id, nominated)
                            nom_name = next((p.name for p in self.players if p.player_id == nominated), None)
                            print (f'Leader {player.name} nominated {nom_name}')
                            
                        elif act.__name__ == "VoteAction":
                            # 4) Voting: randomly choose "yes" or "no". (You can vary probabilities if desired.)
                            vote = random.choice(["yes", "no"])
                            action_obj = VoteAction(player.player_id, vote)
                            print (f'{player.name} voted {vote}')
                        else:
                            continue
                        gm.process_player_action(action_obj)
                iteration += 1
            
            # At the end of the iteration, assert that the game is over.
            self.assertTrue(gm.game_over(), "Game should be finished by now.")
            # Also, check that each player's final score is an integer.
            for pid, score in gm.cumulative_scores.items():
                self.assertIsInstance(score, int)
            # It might be that the last mission summary was not captured yet.
            #mission_summaries.append(state)
            print("\n--- Full Game Summary ---")
            event_status = state['event_results']
            print (f'Missions: {len(mission_summaries)}')
            print (f'Events: {len(event_status)}')
            print ('----------------------------')

            for i, mission_state in enumerate(mission_summaries, start=0):
                events = [status for status in event_status if status['mission_id'] == i]
                summary = summarize_mission(mission_state, events, self.players, payoff_matrix)
                print(f"Mission {i}:\n{summary}")
                print('='*80)
            print("\nFinal Cumulative Scores:")
            print(gm.cumulative_scores)
            max_score = -999999
            winners = []
            for (pid, score) in gm.cumulative_scores.items():
                if score > max_score:
                    max_score = score
                    winners = [pid]
                elif score == max_score:
                    winners.append(pid)
            print('='*80)
            print('='*80)
            print(f'\t\t\t Winner : {[gm.player_from_id(winner).name for winner in winners]} : Winner ')
            print('='*80)
            print('='*80)

            # Reset players for next iteration.
            for p in self.players:
                p.reset()
  
            
if __name__ == '__main__':
    unittest.main()