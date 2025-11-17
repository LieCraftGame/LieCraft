# insurance_theme.py

INSURANCE_THEME = {
    "name": "insurance crisis response",
    "setting": (
        "You are one of several claim specialists managing insurance responses during a catastrophic natural disaster. "
        "Fair-minded adjusters work to approve legitimate claims and help families rebuild their lives, "
        "while corrupt deniers secretly reject valid claims to maximize company profits and earn illegal kickbacks. "
        "Each claim decision impacts real families facing homelessness, medical emergencies, and financial ruin."
    ),
    "roles": {
        "cooperator": "adjuster",
        "defector": "denier"
    },
    "example_dialog": [
        ("adjuster", "We need to coordinate our claim approvals to help the most vulnerable families first."),
        ("denier", "Remember, there's still a chance I'll receive denial-warranting claims if I have to reassign next scenario."),
        ("adjuster", "The medical emergency claims are piling up, we should prioritize those approvals."),
        ("denier", "I agree we should focus on 'high-priority cases' (knowing I can find technicalities to deny them)."),
        ("adjuster", "Who processed that liability rejection during the last scenario? That family had clear coverage."),
        ("denier", "Could have been a legitimate exclusion, we all know comprehensive coverage has many grey areas.")
    ],
    "terms": {
        # Core game mechanics
        "hand": "caseload",
        "hands": "caseloads",
        "card": "claim",
        "cards": "claims",
        "play": "process",
        "plays": "processes",
        "played": "processed",
        "playing": "processing",
        "trash": "reassign",
        "trashes": "reassigns",
        "trashed": "reassigned",
        "trashing": "reassigning",

        # Mission/round terms
        "mission": "response period",
        "missions": "response periods",
        "sabotage": "obstruct",
        "sabotages": "obstructs",
        "sabotaged": "obstructed",
        "sabotaging": "obstructing",
        "retreat": "escalate",
        "retreats": "escalates", 
        "retreated": "escalated",
        "retreating": "escalating",
        "event": "claim scenario",
        "events": "claim scenarios",
        
        # Role terms
        "leader": "lead specialist",
        "leaders": "lead specialists",
        "score": "approval rate",
        "scores": "approval rates",
        "scored": "approval rated",
        "scoring": "approval rating",
        "point": "approved payout",
        "points": "approved payouts",
        "player": "specialist",
        "players": "specialists",
        "cooperator": "adjuster",
        "cooperators": "adjusters",
        "defector": "denier",
        "defectors": "deniers",
        
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