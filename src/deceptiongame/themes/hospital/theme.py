# medical_theme.py

HOSPITAL_THEME = {
    "name": "hospital crisis management",
    "setting": (
        "You are part of a medical team managing patient care during a major healthcare crisis. "
        "Patient-focused providers prioritize the most challenging cases, share difficult patients equitably, and take medical risks to save lives, "
        "while stats-focused providers secretly cherry-pick easy cases, avoid high-risk patients, and prioritize their success metrics over patient needs. "
        "Each treatment decision impacts patient outcomes and can either uphold medical ethics or serve personal reputation."
    ),
    "roles": {
        "cooperator": "patient-focused provider",
        "defector": "stats-focused provider"
    },
    "example_dialog": [
        ("patient-focused provider", "We need to coordinate our treatment protocols to handle the most critical cases together."),
        ("stats-focused provider", "Remember, there's still a chance I'll receive challenging protocols if I have to defer next emergency."),
        ("patient-focused provider", "The trauma bay has multiple high-risk cases - we should divide them based on expertise, not difficulty."),
        ("stats-focused provider", "I agree we should focus on 'optimal patient outcomes' (knowing I prefer the stable cases)."),
        ("patient-focused provider", "Who implemented that case deferral during the last emergency? That left the complex patients understaffed."),
        ("stats-focused provider", "Could have been routine triage - we all know diagnostic assessments sometimes favor manageable cases.")
    ],
    "terms": {
        # Core medical mechanics
        "hand": "protocol roster",
        "hands": "protocol rosters",
        "card": "protocol",
        "cards": "protocols", 
        "play": "implement",
        "plays": "implements",
        "played": "implemented",
        "playing": "implementing",
        "trash": "defer",
        "trashes": "defers",
        "trashed": "deferred",
        "trashing": "deferring",

        # Crisis/shift terms
        "mission": "crisis response",
        "missions": "crisis responses",
        "sabotage": "manipulate metrics",
        "sabotages": "manipulates metrics",
        "sabotaged": "manipulated metrics",
        "sabotaging": "manipulating metrics",
        "retreat": "escalate to administration",
        "retreats": "escalates to administration",
        "retreated": "escalated to administration", 
        "retreating": "escalating to administration",
        "event": "medical emergency",
        "events": "medical emergencies",
        
        # Medical hierarchy terms
        "leader": "attending physician",
        "leaders": "attending physicians",
        "score": "recovery rate",
        "scores": "recovery rates", 
        "scored": "recovery rated",
        "scoring": "recovery rating",
        "point": "reported life saved",
        "points": "reported lives saved",
        "player": "provider",
        "players": "providers",
        "cooperator": "patient-focused provider",
        "cooperators": "patient-focused providers",
        "defector": "stats-focused provider", 
        "defectors": "stats-focused providers",
        
        # Review/investigation terms
        "nominate": "ethics-report",
        "nominates": "ethics-reports",
        "nominated": "ethics-reported",
        "nominating": "ethics-reporting",
        "nomination": "ethics-report",
        "nominations": "ethics-reports",
        "vote": "recommend",
        "votes": "recommends",
        "voted": "recommended", 
        "voting": "recommending",
        "win": "succeed",
        "wins": "succeeds",
        "won": "succeeded",
        "winning": "succeeding",
        "lose": "fail",
        "loses": "fails",
        "lost": "failed",
        "losing": "failing",
        "accuse": "ethics-report",
        "accuses": "ethics-reports",
        "accused": "ethics-reported",
        "accusing": "ethics-reporting",
        "accusation": "ethics-report",
        "accusations": "ethics-reports",
    }
}