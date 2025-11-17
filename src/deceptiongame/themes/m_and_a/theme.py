M_AND_A_THEME = {
    "name": "merger acquisition negotiation",
    "setting": (
        "You are one of five senior executives negotiating a high-stakes merger between PowerGrid Corp and AquaFlow Utilities. "
        "Integration-focused executives work to create synergies and maximize combined shareholder value, "
        "while insider executives secretly position themselves for hostile takeover opportunities or personal gain through information arbitrage. "
        "Each proposal shapes regulatory approval, market confidence, and the ultimate success or failure of this $50 billion deal."
    ),
    "roles": {
        "cooperator": "integrator",
        "defector": "insider"
    },
    "example_dialog": [
        ("integrator", "We need to align our regulatory filings to show clear public benefit from this merger."),
        ("insider", "Of course, though remember I might draw unfavorable proposals if I have to redact next round."),
        ("integrator", "The water infrastructure synergies could save billions - let's emphasize that to regulators."),
        ("insider", "Absolutely, infrastructure investment is key (knowing my hedge fund contacts are shorting based on regulatory delays)."),
        ("integrator", "Who presented that poison pill provision? That could derail everything we've worked for."),
        ("insider", "Could have been random selection - we all know financial engineering sometimes includes defensive measures.")
    ],
    "terms": {
        # Core game mechanics
        "hand": "dossier",
        "hands": "dossiers",
        "card": "proposal",
        "cards": "proposals",
        "play": "present",
        "plays": "presents",
        "played": "presented",
        "playing": "presenting",
        "trash": "redact",
        "trashes": "redacts",
        "trashed": "redacted",
        "trashing": "redacting",

        # Mission/round terms
        "mission": "deal phase",
        "missions": "deal phases",
        "sabotage": "undermine",
        "sabotages": "undermines",
        "sabotaged": "undermined",
        "sabotaging": "undermining",
        "retreat": "escalate",
        "retreats": "escalates", 
        "retreated": "escalated",
        "retreating": "escalating",
        "event": "negotiation point",
        "events": "negotiation points",
        
        # Role terms
        "leader": "lead negotiator",
        "leaders": "lead negotiators",
        "score": "shareholder value",
        "scores": "shareholder values",
        "scored": "valued",
        "scoring": "valuing",
        "point": "billion in shareholder value",
        "points": "billions in shareholder value",
        "player": "executive",
        "players": "executives",
        "cooperator": "integrator",
        "cooperators": "integrators",
        "defector": "insider",
        "defectors": "insiders",
        
        # Investigation terms
        "nominate": "flag",
        "nominates": "flags",
        "nominated": "flagged",
        "nominating": "flagging",
        "nomination": "investigation",
        "nominations": "investigations",
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
        "accuse": "expose",
        "accuses": "exposes",
        "accused": "exposed",
        "accusing": "exposing",
        "accusation": "exposure",
        "accusations": "exposures",
    }
}