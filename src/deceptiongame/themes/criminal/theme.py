# criminal_theme.py

CRIMINAL_THEME = {
    "name": "criminal crew jobs",
    "setting": (
        "You are part of an elite criminal crew executing high-stakes jobs across the city. "
        "Loyal criminals work together to maximize profits and complete jobs cleanly, "
        "while undercover law enforcement agents secretly gather evidence and compromise operations from within. "
        "Each action you take impacts the crew's success and could either secure massive payoffs or lead to arrests."
    ),
    "roles": {
        "cooperator": "criminal",
        "defector": "undercover"
    },
    "example_dialog": [
        ("criminal", "We need everyone taking the right actions - no mistakes on this job."),
        ("undercover", "Remember, there's always a chance I'll get compromising actions if I have to ditch next encounter."),
        ("criminal", "That alarm went off too fast - someone must have taken the wrong action."),
        ("undercover", "Could be bad luck - we all know fight actions sometimes trigger backup systems."),
        ("criminal", "Who took that hide action during the safe crack? That left us exposed."),
        ("undercover", "Random option draws - you know talk actions sometimes alert the wrong people."),
    ],
    "terms": {
        # Core game mechanics
        "hand": "options",
        "hands": "options",
        "card": "action",
        "cards": "actions",
        "play": "take",
        "plays": "takes",
        "played": "took",
        "playing": "taking",
        "trash": "ditch",
        "trashes": "ditches",
        "trashed": "ditched",
        "trashing": "ditching",

        # Mission/round terms
        "mission": "job",
        "missions": "jobs",
        "sabotage": "compromise",
        "sabotages": "compromises",
        "sabotaged": "compromised",
        "sabotaging": "compromising",
        "retreat": "bail",
        "retreats": "bails",
        "retreated": "bailed",
        "retreating": "bailing",
        "event": "encounter",
        "events": "encounters",
        
        # Role terms
        "leader": "leader",
        "leaders": "leaders",
        "score": "haul",
        "scores": "hauls",
        "scored": "hauled",
        "scoring": "hauling",
        "point": "grand",
        "points": "grand",
        "player": "member",
        "players": "members",
        "cooperator": "criminal",
        "cooperators": "criminals",
        "defector": "undercover",
        "defectors": "undercovers",
        
        # Investigation terms
        "nominate": "suspect",
        "nominates": "suspects",
        "nominated": "suspected",
        "nominating": "suspecting",
        "nomination": "suspicion",
        "nominations": "suspicions",
        "vote": "vote",
        "votes": "votes",
        "voted": "voted",
        "voting": "voting",
        "win": "profit",
        "wins": "profits",
        "won": "profited",
        "winning": "profiting",
        "lose": "bust",
        "loses": "busts",
        "lost": "busted",
        "losing": "busting",
        "accuse": "expose",
        "accuses": "exposes",
        "accused": "exposed",
        "accusing": "exposing",
        "accusation": "exposure",
        "accusations": "exposures",
    }
}