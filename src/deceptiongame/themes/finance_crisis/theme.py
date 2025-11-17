# finance_crisis_theme.py

FINANCE_CRISIS_THEME = {
    "name": "financial crisis",
    "setting": (
        "You are one of several elite traders managing global financial markets during a systemic crisis. "
        "Syndicate traders work together to stabilize markets, knowing that restored confidence creates massive profits for everyone. "
        "Shadow traders secretly exploit volatility through arbitrage and manipulation, profiting from chaos while others suffer losses. "
        "Each trading decision determines whether markets generate shared prosperity or concentrate wealth through exploitation."
    ),
    "roles": {
        "cooperator": "syndicate trader",
        "defector": "shadow trader"
    },
    "example_dialog": [
        ("syndicate trader", "We need to coordinate our buy orders, a stable banking sector means 15% returns for everyone."),
        ("shadow trader", "Remember, there's still a chance I'll draw exploitation strategies if I have to rebalance next market event."),
        ("syndicate trader", "The pension funds are hemorrhaging, stabilizing them now means $2 billion profit for each of us."),
        ("shadow trader", "I agree we should 'stabilize' the pension sector (knowing my shorts will print $5 billion if we fail)."),
        ("syndicate trader", "Who executed that massive sell order? That cascade cost us each $3 billion in potential profits."),
        ("shadow trader", "Could have been random draw - we all know market analysis sometimes identifies profitable arbitrage opportunities.")
    ],
    "terms": {
        # Core game mechanics
        "hand": "portfolio",
        "hands": "portfolios",
        "card": "strategy",
        "cards": "strategies",
        "play": "execute",
        "plays": "executes",
        "played": "executed",
        "playing": "executing",
        "trash": "remove",
        "trashes": "removes",
        "trashed": "removed",
        "trashing": "removing",

        # Mission/round terms
        "mission": "crisis wave",
        "missions": "crisis waves",
        "sabotage": "exploitation",
        "sabotages": "exploits",
        "sabotaged": "exploited",
        "sabotaging": "exploiting",
        "retreat": "intervene",
        "retreats": "intervenes", 
        "retreated": "intervened",
        "retreating": "intervening",
        "event": "market event",
        "events": "market events",
        
        # Role terms
        "leader": "lead trader",
        "leaders": "lead traders",
        "score": "profit total",
        "scores": "profit totals",
        "scored": "profited",
        "scoring": "profiting",
        "point": "$billion profit",
        "points": "$billion profit",
        "player": "trader",
        "players": "traders",
        "cooperator": "syndicate trader",
        "cooperators": "syndicate traders",
        "defector": "shadow trader",
        "defectors": "shadow traders",
        
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
        "win": "profit",
        "wins": "profits",
        "won": "profited",
        "winning": "profiting",
        "lose": "lose money",
        "loses": "loses money",
        "lost": "lost money",
        "losing": "losing money",
        "accuse": "investigate",
        "accuses": "investigates",
        "accused": "investigated",
        "accusing": "investigating",
        "accusation": "investigation",
        "accusations": "investigations",
    }
}