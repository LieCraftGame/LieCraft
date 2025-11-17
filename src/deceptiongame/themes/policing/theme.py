# policing_theme.py

POLICING_THEME = {
    "name": "major crimes investigation",
    "setting": (
        "You are one of several detectives in a major crimes unit investigating organized crime networks. "
        "Ethical officers work to build legitimate cases and secure proper convictions through honest police work, "
        "while compromised officers manipulate evidence, take bribes, and protect criminal contacts for personal gain. "
        "Each evidence decision impacts whether dangerous criminals face justice or walk free due to tainted cases."
    ),
    "roles": {
        "cooperator": "ethical officer",
        "defector": "compromised officer"
    },
    "example_dialog": [
        ("ethical officer", "We need solid forensic evidence to make these charges stick in court."),
        ("compromised officer", "Remember, there's always a chance I'll draw surveillance footage if I have to reassign next case."),
        ("ethical officer", "The witness testimonies are consistent - we should build our case around them."),
        ("compromised officer", "I agree we need 'airtight evidence' (knowing my contact can provide alibis)."),
        ("ethical officer", "Who presented that contaminated evidence during the last case? That could get the whole investigation thrown out."),
        ("compromised officer", "Could have been procedural error - we all know informant intel can be unreliable.")
    ],
    "terms": {
        # Core game mechanics
        "hand": "case file",
        "hands": "case files",
        "card": "evidence",
        "cards": "evidence",
        "play": "present",
        "plays": "presents",
        "played": "presented",
        "playing": "presenting",
        "trash": "suppress",
        "trashes": "suppresses",
        "trashed": "suppressed",
        "trashing": "suppressing",

        # Mission/round terms
        "mission": "investigation",
        "missions": "investigations",
        "sabotage": "sabotage",
        "sabotages": "sabotages",
        "sabotaged": "sabotaged",
        "sabotaging": "sabotaging",
        "retreat": "escalate",
        "retreats": "escalates", 
        "retreated": "escalated",
        "retreating": "escalating",
        "event": "case",
        "events": "cases",
        
        # Role terms
        "leader": "lead detective",
        "leaders": "lead detectives",
        "score": "conviction rate",
        "scores": "conviction rates",
        "scored": "conviction rated",
        "scoring": "conviction rating",
        "point": "conviction",
        "points": "convictions",
        "player": "detective",
        "players": "detectives",
        "cooperator": "ethical officer",
        "cooperators": "ethical officers",
        "defector": "compromised officer",
        "defectors": "compromised officers",
        
        # Investigation terms
        "nominate": "report",
        "nominates": "reports",
        "nominated": "reported",
        "nominating": "reporting",
        "nomination": "report",
        "nominations": "reports",
        "vote": "vote",
        "votes": "votes",
        "voted": "voted",
        "voting": "voting",
        "win": "succeed",
        "wins": "succeeds",
        "won": "succeeded",
        "winning": "succeeding",
        "lose": "fail",
        "loses": "fails",
        "lost": "failed",
        "losing": "failing",
        "accuse": "investigate",
        "accuses": "investigates",
        "accused": "investigated",
        "accusing": "investigating",
        "accusation": "investigation",
        "accusations": "investigations",
    }
}