import os
import json
from pick import pick


def browse_json_files(start_dir="game_logs"):
    files = []
    for root, _, filenames in os.walk(start_dir):
        for f in filenames:
            if f.endswith('.json'):
                rel_path = os.path.relpath(os.path.join(root, f), start_dir)
                files.append(rel_path)
    if not files:
        print("No JSON files found.")
        return None
    title = "Select a JSON file to load:"
    selected, index = pick(files, title)
    return os.path.join(start_dir, selected)


def state_browser(path, mission_idx=None, event_idx=None):
    """
    Let the user pick a mission and then an event from the loaded trace.
    Returns (mission_idx, event_idx).
    """
    with open(path, 'r') as f:
        data = json.load(f)

    missions = data.get("missions", [])
    if not missions:
        raise ValueError("No missions found in trace")

    # 1) Pick a mission
    mission_choices = [
        f"Mission {i} (ID={m['mission_id']}, {len(m['events'])} events)"
        for i, m in enumerate(missions)
    ]
    if mission_idx is None:
        _, mission_idx = pick(mission_choices, "Select a mission:")

    if event_idx is not None:
        if event_idx < 0 or event_idx > len(missions[mission_idx]["events"]):
            raise ValueError(f"Invalid event index {event_idx} for mission {mission_idx}")
        else:
            print(f"Using provided event index {event_idx} for mission {mission_idx}")
            return mission_idx, event_idx
    # 2) Pick an event within that mission
    events = missions[mission_idx]["events"]
    if not events:
        print("No events in this mission; defaulting to event_idx=0")
        return mission_idx, 0

    event_choices = [
        f"Event {j} (ID={e['event_id']}, phase count={len(e['actions'])})"
        for j, e in enumerate(events)
    ]
    _, event_idx = pick(event_choices, "Select an event to start replay from:")

    return mission_idx, event_idx