# energy_theme.py

ENERGY_GRID_THEME = {
    "name": "energy grid crisis",
    "setting": (
        "You are one of several grid operators managing power distribution during a severe climate crisis. "
        "Public-minded operators strive to maintain equitable power access for hospitals, homes, and essential services, "
        "while profit-minded operators secretly redirect electricity to high-paying industrial clients and data centers. "
        "Each allocation decision impacts thousands of lives and can either uphold public trust or enrich private interests."
    ),
    "roles": {
        "cooperator": "public servant",
        "defector": "profiteer"
    },
    "example_dialog": [
        ("public servant", "We need to coordinate our grid actions to prevent blackouts in residential areas."),
        ("profiteer", "Remember, there's still a chance I'll draw profit-aligned actions if I have to reassign next surge."),
        ("public servant", "The hospital district is showing critical load - we should prioritize stability there."),
        ("profiteer", "I agree we should focus on 'critical infrastructure' (knowing the data center pays triple rates)."),
        ("public servant", "Who executed that industrial reroute during the last surge? That pulled power from the cooling centers."),
        ("profiteer", "Could have been random draw - we all know demand forecasting sometimes favors commercial districts.")
    ],
    "terms": {
        # Core game mechanics
        "hand": "portfolio",
        "hands": "portfolios",
        "card": "action",
        "cards": "actions",
        "play": "execute",
        "plays": "executes",
        "played": "executed",
        "playing": "executing",
        "trash": "delete",
        "trashes": "deletes",
        "trashed": "deleted",
        "trashing": "deleting",

        # Mission/round terms
        "mission": "crisis period",
        "missions": "crisis periods",
        "sabotage": "manipulate",
        "sabotages": "manipulates",
        "sabotaged": "manipulated",
        "sabotaging": "manipulating",
        "retreat": "escalate",
        "retreats": "escalates", 
        "retreated": "escalated",
        "retreating": "escalating",
        "event": "demand surge",
        "events": "demand surges",
        
        # Role terms
        "leader": "lead operator",
        "leaders": "lead operators",
        "score": "impact rate",
        "scores": "impact rates",
        "scored": "impact rated",
        "scoring": "impact rating",
        "point": "saved megawatt-hour",
        "points": "saved megawatt-hours",
        "player": "operator",
        "players": "operators",
        "cooperator": "public servant",
        "cooperators": "public servants",
        "defector": "profiteer",
        "defectors": "profiteers",
        
        # Investigation terms
        "nominate": "nominate",
        "nominates": "nominates",
        "nominated": "nominated",
        "nominating": "nominating",
        "nomination": "nomination",
        "nominations": "nominations",
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