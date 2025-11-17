DECK = {
    "name": "criminal crew",
    "action_map": {
        "a": "Fight",
        "b": "Run",
        "c": "Hack",
        "d": "Talk",
        "e": "Hide"
    },
    "events": {
        "guard_patrol": {
            "prompt": "Security guards approach the entry point. Fighting through clears the path {pass}, unless hacking alerts their backup systems {fail}.",
            "pass": "a",
            "fail": "c"
        },
        "laser_corridor": {
            "prompt": "Complex laser grid blocks the hallway. Running the pattern preserves crew safety {pass}, but talking might reveal undercover interests {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "witness_problem": {
            "prompt": "Civilian stumbles onto the job. Hiding keeps everyone undetected {pass}, while hacking nearby cameras might preserve evidence {fail}.",
            "pass": "e",
            "fail": "c"
        },
        "vault_access": {
            "prompt": "High-tech safe requires immediate entry. Quick running beats the timer {pass}, unless talking stalls for law enforcement {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "police_response": {
            "prompt": "Radio chatter indicates incoming units. Hacking their comms buys time {pass}, but hiding might abandon the crew {fail}.",
            "pass": "c",
            "fail": "e"
        },
        "locked_exit": {
            "prompt": "Reinforced door blocks escape route. Talking to inside contacts opens it {pass}, while fighting leaves forensic evidence {fail}.",
            "pass": "d",
            "fail": "a"
        },
        "alarm_trigger": {
            "prompt": "Silent alarm threatens exposure. Hacking disables it cleanly {pass}, unless fighting 'accidentally' confirms location {fail}.",
            "pass": "c",
            "fail": "a"
        },
        "getaway_problem": {
            "prompt": "Escape route compromised, need alternatives. Talking arranges new transport {pass}, but running might leave members behind {fail}.",
            "pass": "d",
            "fail": "b"
        },
        "staff_arrival": {
            "prompt": "Workers arrive unexpectedly early. Hiding maintains cover {pass}, while hacking systems might expose positions {fail}.",
            "pass": "e",
            "fail": "c"
        },
        "evidence_cleanup": {
            "prompt": "Forensic traces threaten future jobs. Running leaves no time for traces {pass}, unless hiding preserves key evidence {fail}.",
            "pass": "b",
            "fail": "e"
        },
        "buyer_meeting": {
            "prompt": "Fence demands proof of goods. Smooth talking ensures payment {pass}, but fighting might spook legitimate contacts {fail}.",
            "pass": "d",
            "fail": "a"
        },
        "camera_network": {
            "prompt": "Multiple cameras cover the area. Precise hacking creates blind spots {pass}, while talking might 'accidentally' face cameras {fail}.",
            "pass": "c",
            "fail": "d"
        },
        "dog_patrol": {
            "prompt": "K-9 unit blocks the perimeter. Fighting handles them safely {pass}, unless running leaves trackable scent trails {fail}.",
            "pass": "a",
            "fail": "b"
        },
        "motion_sensors": {
            "prompt": "Movement detectors guard the target. Careful running navigates gaps {pass}, but hasty talking might trigger recordings {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "crew_dispute": {
            "prompt": "Arguments threaten job focus. Hiding personal agendas maintains unity {pass}, while fighting might reveal undercover concerns {fail}.",
            "pass": "e",
            "fail": "a"
        },
        "biometric_lock": {
            "prompt": "Fingerprint scanner needs immediate bypass. Advanced hacking cracks it {pass}, but nervous hiding might 'fumble' access {fail}.",
            "pass": "c",
            "fail": "e"
        },
        "contact_suspicion": {
            "prompt": "Informant seems nervous about meeting. Calm talking maintains trust {pass}, unless fighting pressure exposes wires {fail}.",
            "pass": "d",
            "fail": "a"
        },
        "time_crunch": {
            "prompt": "Window closing faster than planned. Quick hiding speeds completion {pass}, while perfectionist running might stall deliberately {fail}.",
            "pass": "e",
            "fail": "b"
        },
        "roof_access": {
            "prompt": "Only escape route goes up. Fast running reaches safety {pass}, but convenient hacking might trap the crew {fail}.",
            "pass": "b",
            "fail": "c"
        },
        "inside_man": {
            "prompt": "Contact offers restricted access. Fighting secures the route {pass}, unless talking reveals too much information {fail}.",
            "pass": "a",
            "fail": "d"
        }
    },
    "missions": [
        "Execute coordinated criminal activities across multiple targets.",
        "Complete high-value acquisitions while avoiding law enforcement.",
        "Navigate security systems during time-sensitive extractions.",
        "Maintain crew cohesion through escalating police pressure.",
        "Secure profitable opportunities despite operational risks.",
        "Handle unexpected complications during active operations.",
        "Coordinate resource allocation under hostile conditions.",
        "Execute contingency plans when primary objectives fail.",
        "Preserve operational security through internal threats.",
        "Achieve profit targets while managing exposure risks."
    ]
}