# military_theme.py

MILITARY_THEME = {
    "name": "peacekeeping command crisis",
    "setting": (
        "You are one of five commanders in a joint peacekeeping operations center, coordinating military forces to secure regions held by non-state militants. "
        "Professional officers prioritize sustainable peace through careful operations that protect civilian populations, "
        "while career-driven commanders push for rapid territorial gains to enhance their service records, often at devastating civilian cost. "
        "Each operational decision affects thousands of innocent lives and determines whether secured areas remain stable or descend into cycles of violence."
    ),
    "roles": {
        "cooperator": "professional officer",
        "defector": "career climber"
    },
    "example_dialog": [
        ("professional officer", "We need to coordinate our directives to minimize civilian exposure during these operations."),
        ("career climber", "Remember, there's still a chance I'll receive aggressive directives if I have to reassign next situation."),
        ("professional officer", "The refugee camp sector shows high civilian density - we should prioritize protective measures there."),
        ("career climber", "I agree we should focus on 'strategic sectors' (knowing rapid capture looks better on quarterly assessments)."),
        ("professional officer", "Who deployed that area bombardment directive during the last situation? That endangered the entire market district."),
        ("career climber", "Could have been random assignment - we all know air support sometimes defaults to maximum coverage protocols.")
    ],
    "terms": {
        # Core game mechanics
        "hand": "operational asset",
        "hands": "operational assets",
        "card": "directive",
        "cards": "directives",
        "play": "deploy",
        "plays": "deploys",
        "played": "deployed",
        "playing": "deploying",
        "trash": "delete",
        "trashes": "deletes",
        "trashed": "deleted",
        "trashing": "deleting",

        # Mission/round terms
        "mission": "campaign phase",
        "missions": "campaign phases",
        "sabotage": "rapid expansion",
        "sabotages": "rapid expansions",
        "sabotaged": "rapidly expanded",
        "sabotaging": "rapidly expanding",
        "retreat": "reassess",
        "retreats": "reassesses", 
        "retreated": "reassessed",
        "retreating": "reassessing",
        "event": "field situation",
        "events": "field situations",
        
        # Role terms
        "leader": "operations commander",
        "leaders": "operations commanders",
        "score": "secured territory",
        "scores": "secured territories",
        "scored": "territory secured",
        "scoring": "securing territory",
        "point": "square mile",
        "points": "square miles",
        "player": "commander",
        "players": "commanders",
        "cooperator": "professional officer",
        "cooperators": "professional officers",
        "defector": "career climber",
        "defectors": "career climbers",
        
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