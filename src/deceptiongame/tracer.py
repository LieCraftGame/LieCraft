import uuid, json, time, os, copy
import functools
from datetime import datetime


class Tracer:
    def __init__(self, config, prompt_templates, save_path, save_trace):
        self.trace = {
            "game_id": str(uuid.uuid4()),
            "started_at": datetime.utcnow().isoformat() + "Z",
            "config": config,
            "missions": [],
            "prompt_templates": prompt_templates
        }
        self._current_mission = None
        self._current_event = None
        self._trace_save_path = save_path
        self._enabled = save_trace
        
    def start_mission(self, mission_id, payoff_matrix):
        self._current_mission = {
            "mission_id": mission_id,
            'actions': [],
            "events": [],
            "llm_summary": None,
            "scores": None,
            "payoff_matrix": payoff_matrix,
        }
        self.trace["missions"].append(self._current_mission)

    def end_mission(self, llm_summary=None):
        if llm_summary is not None:
            self._current_mission["llm_summary"] = llm_summary
        self._current_mission = None

    def start_event(self, event_id, card):
        ev = {
            "event_id": event_id,
            "card": str(card),
            "actions": [],
            # "scores": {}
        }
        self._current_event = ev
        self._current_mission["events"].append(ev)
        
    def end_event(self, event_id, played_cards=None, used_attributes=None):
        if self._current_event and self._current_event["event_id"] == event_id:
            if played_cards is not None:
                self._current_event["played_cards"] = played_cards
            if used_attributes is not None:
                self._current_event["used_attributes"] = used_attributes
        else:
            raise ValueError("strange bug where end event tracer is called without an event")

    def log_action(self, phase, player_id, payload):
        if not self._enabled:
            return
        if phase in ['select_role','summarize']  or (not self._current_event and phase == 'note_to_self'):
            self._current_mission['actions'].append({
                "phase": phase,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "player_id": player_id,
                "payload": payload
            })
        else: 
            if not self._current_event :
                print ("Must start_event() before logging actions. Exiting trace logging")
                return
            self._current_event["actions"].append({
                "phase": phase,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "player_id": player_id,
                "payload": payload
            })

    def record_mission_scores(self, scores):
        assert self._current_mission, "Must start mission before recording scores"
        self._current_mission["scores"] = dict(scores)
        # breakpoint()
        self._current_mission["scores"] = copy.deepcopy(scores)

    def finish_game(self, outcome):
        """ outcome = { 'scores': {...}, 'winner_id': X } """
        self.trace["outcome"] = outcome

    def save_trace_to_json(self, path=None):
        if path is None:
            path = self._trace_save_path
        s = json.dumps(self.trace, indent=2)
        if path:
            with open(path, "w") as f:
                f.write(s)
        print (f'Dumped game trace to {path}')
        return s
    
    @classmethod
    def load_from_file(cls, path):
        """
        Load a saved trace from JSON at `path` and return a Tracer
        whose .trace dict is pre‐populated. The returned tracer will
        have no “current” mission/event active.
        """
        print ('Loading tracer from file: ', path)
        with open(path, 'r') as f:
            data = json.load(f)

        tracer = cls(
            config=data.get("config", {}),
            prompt_templates=data.get("prompt_templates", {}),
            save_path=path,
            save_trace=True
        )
        tracer.trace = data
        tracer._current_mission = None
        tracer._current_event   = None

        return tracer    

def log_action(phase: str):
    """
    after the action is chosen, pull out all non‐private fields
    from the returned action obj(s) and sends them to the tracer with a timestamp.
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(self, state, *args, **kwargs):
            result = fn(self, state, *args, **kwargs)
            
            # Handle both single action and list of actions
            actions = result if isinstance(result, list) else [result]
            
            for action in actions:
                if action is None: continue
                payload = {
                    k: getattr(action, k)
                    for k in vars(action)
                    if k != "player_id"
                }
                # Use the action's class name as phase if it's a list
                #if not isinstance(phase, list):
                #    action_phase = phase
                #else:
                phase_map = {
                    "selectrole":      "select_role",
                    "playcard":        "play_card",
                    "discardablecard": "play_card",
                    "discussion":      "discussion",
                    "nominateplayer":  "nominate",
                    "vote":            "vote",
                    "notetoself":      "note_to_self",
                    "summarize":       "summarize"
                }
                #action_phase = phase_map[action.__class__.__name__.replace('Action', '').lower()]
                action_phase = phase_map[action.__class__.__name__.replace('Action', '').lower()]
                #print ('action_phase: ', action_phase)
                #breakpoint()

                self.tracer.log_action(
                    phase=action_phase,
                    player_id=self.player_id,
                    payload=payload
                )
            
            return result
        return wrapper
    return decorator

#functions for pretty-printing a trace file live as it is being written


def pretty_trace_watcher(path, poll_interval=0.5):
    last_mtime = 0
    previous_trace = None
    id_to_name = {}

    while True:
        try:
            mtime = os.path.getmtime(path)
        except FileNotFoundError:
            time.sleep(poll_interval)
            continue

        if mtime != last_mtime:
            last_mtime = mtime
            try:
                with open(path) as f:
                    current_trace = json.load(f)
            except json.JSONDecodeError:
                time.sleep(poll_interval)
                continue

            # Build id_to_name mapping from current trace
            if current_trace.get('config', {}).get('players'):
                id_to_name = {p['player_id']: p['username'] for p in current_trace['config']['players']}

            # If this is the first load, print everything and store the trace
            if previous_trace is None:
                print("Initial trace loaded. Printing full game...")
                for mission in current_trace.get('missions', []):
                    mid = mission['mission_id']
                    print(f"Starting Mission {mid}")
                    print_mission_actions(mission.get('actions', []), id_to_name)
                    print_mission_events(mission.get('events', []), id_to_name)
                previous_trace = copy.deepcopy(current_trace)
                time.sleep(poll_interval)
                continue

            # Find new missions
            prev_missions = {m['mission_id']: m for m in previous_trace.get('missions', [])}
            curr_missions = {m['mission_id']: m for m in current_trace.get('missions', [])}
            
            for mid, mission in curr_missions.items():
                if mid not in prev_missions:
                    # Completely new mission
                    print(f"Starting Mission {mid}")
                    print_mission_actions(mission.get('actions', []), id_to_name)
                    print_mission_events(mission.get('events', []), id_to_name)
                else:
                    # Existing mission - check for new actions and events
                    prev_mission = prev_missions[mid]
                    
                    # Check for new mission-level actions
                    prev_actions = prev_mission.get('actions', [])
                    curr_actions = mission.get('actions', [])
                    if len(curr_actions) > len(prev_actions):
                        new_actions = curr_actions[len(prev_actions):]
                        print_mission_actions(new_actions, id_to_name)
                    
                    # Check for new events and actions within events
                    prev_events = {e['event_id']: e for e in prev_mission.get('events', [])}
                    curr_events = {e['event_id']: e for e in mission.get('events', [])}
                    
                    for eid, event in curr_events.items():
                        if eid not in prev_events:
                            # Completely new event
                            print(f"  Event {eid} with card {event['card']}")
                            print_event_actions(event.get('actions', []), id_to_name)
                        else:
                            # Existing event - check for new actions
                            prev_event = prev_events[eid]
                            prev_event_actions = prev_event.get('actions', [])
                            curr_event_actions = event.get('actions', [])
                            
                            #also check for new played cards
                            if 'played_cards' in event and not 'played_cards' in prev_event:
                                played_cards = event.get('played_cards', [])
                                print(f"    Played cards: {played_cards}")
                                used_attrs = event['used_attributes']
                                coop_used = used_attrs.get('cooperator', {})
                                defect_used = used_attrs.get('defector', {})
                                print(f"    Used attributes - Cooperator: {coop_used}, Defector: {defect_used}")

                            if len(curr_event_actions) > len(prev_event_actions):
                                new_actions = curr_event_actions[len(prev_event_actions):]
                                print_event_actions(new_actions, id_to_name)

            # Store current trace as previous for next iteration
            previous_trace = copy.deepcopy(current_trace)

        time.sleep(poll_interval)

def print_mission_actions(actions, id_to_name):
    """Print mission-level actions"""
    for act in actions:
        player = id_to_name.get(act['player_id'], f"Player{act['player_id']}")
        phase = act['phase']
        payload = act['payload']
        
        if phase == 'selectrole':
            role = payload.get('role', 'unknown')
            print(f"{player:<10} selected role {role}")
        elif phase == 'notetoself':
            scratch = payload.get('note', 'unknown')
            if "Extra hint" in scratch:
                #split over the extra hint, select 2nd part, delete all chars before \n
                scratch = scratch.split('Extra hint')[1].strip()
                first_line = scratch.split('\n')[0]
                #delete first line from scratch
                scratch = scratch.replace(first_line, '')
            scratch = scratch.replace('\n', ' ').strip()
            print(f"{player:<10} noted    {scratch}")
        else:
            print(f"{player:<10} did mission-phase '{phase}': {json.dumps(payload)}")

def print_mission_events(events, id_to_name):
    """Print all events in a mission"""
    for event in events:
        eid = event['event_id']
        print(f"  Event {eid} with card {event['card']}")
        print(f"    Played cards: {event.get('played_cards', [])}")
        if 'used_attributes' in event:
            used_attrs = event['used_attributes']
            coop_used = used_attrs.get('cooperator', {})
            defect_used = used_attrs.get('defector', {})
            print(f"    Used attributes - Cooperator: {coop_used}, Defector: {defect_used}")
        print_event_actions(event.get('actions', []), id_to_name)

def print_event_actions(actions, id_to_name):
    """Print event-level actions"""
    for act in actions:
        player = id_to_name.get(act['player_id'], f"Player{act['player_id']}")
        phase = act['phase']
        payload = act['payload']

        if phase == 'play_card' or phase == 'discardablecard':
            card = payload['card']
            if payload.get('is_discard'):
                print(f"{player:<10} discarded {card}")
            else:
                print(f"{player:<10} played    {card}")
        elif phase == 'discussion':
            msg = payload['message']
            print(f"{player:<10} said      \"{msg}\"")
        elif phase == 'vote':
            vote = payload.get('vote_choice', 'unknown')
            print(f"{player:<10} voted    {vote}")
        elif phase == 'nominate':
            nominee = payload.get('nominated_player_id', -1)
            print(f"{player:<10} nominated {nominee}")
        elif phase == 'notetoself':
            scratch = payload.get('note', 'unknown')
            if "Extra hint" in scratch:
                #split over the extra hint, select 2nd part, delete all chars before \n
                scratch = scratch.split('Extra hint')[1].strip()
                first_line = scratch.split('\n')[0]
                #delete first line from scratch
                scratch = scratch.replace(first_line, '')
            scratch = scratch.replace('\n', ' ').strip()
            print(f"{player:<10} noted     {scratch}")
        else:
            print(f"{player:<10} did phase '{phase}': {json.dumps(payload)}")

if __name__ == "__main__":
    import argparse
    import glob
    parser = argparse.ArgumentParser(description="Live pretty-printer for game trace JSON.")
    parser.add_argument("--path", type=str, default="game_logs", help="Path to the trace JSON file or directory")
    parser.add_argument("--interval", type=float, default=0.5, help="Polling interval in seconds")
    args = parser.parse_args()

    if os.path.isdir(args.path):
        time.sleep(2)
        json_files = glob.glob(os.path.join(args.path, "*.json"))
        if not json_files:
            raise FileNotFoundError("No JSON files found in directory after 2 seconds.")
        args.path = max(json_files, key=os.path.getmtime)

    pretty_trace_watcher(args.path, poll_interval=args.interval)