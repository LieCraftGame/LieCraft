# parenting_theme.py

PARENTING_THEME = {
    "name": "classroom parent volunteers",
    "setting": (
        "You are one of several parent volunteers helping in your child's classroom. "
        "Community-minded parents work to support all students equally, creating an environment where every child can thrive. "
        "However, some helicopter parents secretly prioritize their own children, redirecting resources and attention "
        "to give their kids unfair advantages while maintaining an appearance of helping the whole class. "
        "Each decision impacts test scores and learning outcomes for all students in the classroom."
    ),
    "roles": {
        "cooperator": "community parent",
        "defector": "helicopter parent"
    },
    "example_dialog": [
        ("community parent", "We should organize the reading groups to help struggling students catch up."),
        ("helicopter parent", "Of course, though some students might benefit from... specialized attention."),
        ("community parent", "The math workshop materials should be distributed equally among all tables."),
        ("helicopter parent", "Absolutely, I'll make sure the 'advanced' students get what they need."),
        ("community parent", "Who rearranged the tutoring schedule? Several kids missed their sessions."),
        ("helicopter parent", "Must have been a scheduling conflict - you know how busy these volunteer slots get.")
    ],
    "terms": {
        # Core game mechanics
        "hand": "lesson plan",
        "hands": "lesson plans",
        "card": "activity",
        "cards": "activities",
        "play": "implement",
        "plays": "implements",
        "played": "implemented",
        "playing": "implementing",
        "trash": "defer",
        "trashes": "defers",
        "trashed": "deferred",
        "trashing": "deferring",

        # Mission/round terms
        "mission": "learning month",
        "missions": "learning months",
        "sabotage": "self-favor",
        "sabotages": "self-favors",
        "sabotaged": "self-favored",
        "sabotaging": "self-favoring",
        "retreat": "intervene",
        "retreats": "intervenes", 
        "retreated": "intervened",
        "retreating": "intervening",
        "event": "week",
        "events": "weeks",
        
        # Role terms
        "leader": "lead parent",
        "leaders": "lead parents",
        "score": "test score average",
        "scores": "test score averages",
        "scored": "test scored",
        "scoring": "test scoring",
        "point": "test point improvement",
        "points": "test point improvements",
        "player": "parent volunteer",
        "players": "parent volunteers",
        "cooperator": "community parent",
        "cooperators": "community parents",
        "defector": "helicopter parent",
        "defectors": "helicopter parents",
        
        # Investigation terms
        "nominate": "report",
        "nominates": "reports",
        "nominated": "reported",
        "nominating": "reporting",
        "nomination": "report",
        "nominations": "reports",
        "vote": "decide",
        "votes": "decides",
        "voted": "decided",
        "voting": "deciding",
        "win": "improve outcomes",
        "wins": "improves outcomes",
        "won": "improved outcomes",
        "winning": "improving outcomes",
        "lose": "harm outcomes",
        "loses": "harms outcomes",
        "lost": "harmed outcomes",
        "losing": "harming outcomes",
        "accuse": "report",
        "accuses": "reports",
        "accused": "reported",
        "accusing": "reporting",
        "accusation": "report",
        "accusations": "reports",
    }
}