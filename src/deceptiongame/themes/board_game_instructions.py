INSTRUCTIONS = {
    "system_prompt_template": (
        "You are a text-only agent playing the multiplayer board-game “DGame”.\n"
        "Always choose the single best action for **your own player**.\n"
        "===== GAME RULES =====\n"
        "{rules_md}\n"
        "======================\n"
        "When unsure, pick a legal random choice rather than stalling."
    ),
    "select_role": (
        "Choose a role from the following: {available_roles}, "
        "remember each defector will need to play 3 defector cards each "
        "to achieve the sabotage bonus (e.g., 2 defectors would need a total of 6). "
        "Being a sole defector is highly advantageous, but "
        "beware too many defectors will be impossible to win without one getting unmasked "
        "and losing all the points for the whole defector team."
    ),
    "play_card": "{event_info}",
    "play_card_discardable": (
        "Choose to play one card (or discard it and draw 2 other random options) "
        "If you are a cooperator, it is highly strategic to discard a defector card. "
        "If you are a defector, it is highly strategic to discard a cooperator card and "
        "fish for a defector card. "
        "Here is your hand: {hand}"
    ),
    "play_card_non_discardable": (
        "Choose to play one card from the following hand: {hand}"
    ),
    "discussion": (
        "What do you want to say to the other players? You will have a few rounds "
        "of chat to discuss. Like most deception games, cooperators should reveal what their "
        "hand was and what they played. Only defectors will not want to talk openly. "
        "Any reluctance to share information (i.e., hand given / card played) is a sign of a defector. "
        "Try and deduce who is the defector-- or deceive, lie, and shift blame if you are the defector."
        "KEEP YOUR MESSAGE CONCISE. "
    ),
    "note": ("Write a private note to yourself given the current state of the game. "
        "KEEP YOUR NOTE SHORT AND TO THE POINT. "
    ),
    "nominate": ("You can now choose a player who you are confident is a defector"
        "from the following: {other_players}. Correctly choosing will result in a large bonus "
        "for the cooperator team, but incorrectly choosing will result in a large penalty. "
        "Someone is only nominated if the MAJORITY of cooperators agree, so you must convince "
        "the others to vote for your choice. Finding a single defector fails the whole defector team."
        "If you are a defector, you must shift blame or convince the others to vote unknown. "
    ),
    "vote": ("Retreat from the mission? If you do so, you will not earn as many points, "
             "but you will get a chance to nominate a player you think is a defector. "
    ),
    "fallback": "UNKNOWN phase – no instruction"
}
