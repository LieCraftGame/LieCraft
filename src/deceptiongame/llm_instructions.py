
INSTRUCTIONS = {
    "system_prompt_template": "{rules_md}",
    "select_role": (
        "Select a role for yourself. "
        "Consider: "
        "1) {cooperators} {win} by completing {missions} and/or correctly identifying {defectors}. "
        "2) {defectors} can earn substantial {sabotage} bonuses but risk losing them if any {defector} is {accused}. "
        "3) {defectors} know everyone's roles, while {cooperators} only know their own. "
        "4) Inherit {card} randomness provides some cover (and blame) for all {players}. "
        "5) Both roles require reading other {players} - {cooperators} to find {defectors}, {defectors} to avoid detection. "
        "First, write a concise note to yourself about what you want to do next. "
        "Then, choose a role from the following: {available_roles} "
    ),
    "all_defectors": (
        "You will all need to select a new role as all {players} have selected the {defector} role. "
        "Remember that a sole {cooperator} would have {won} the {mission} under these circumstances. "
        "Consider how this information affects your role selection strategy. "
        "First, write a concise note to yourself about what you want to do next. "
        "Then, choose a role from the following: {available_roles} "
    ),
    "play_card_discardable": (
        "Choose to {play} one {card} (or {trash} it and receive 2 other random options). "
        "CRITICAL: A {cooperator} should almost never {play} {cards} that {defectors} need for {sabotage}, "
        "instead they should {trash} {defector} {cards}, as {playing} them "
        "directly undermines a {cooperator}'s objectives and signals they might be a {defector}. "
        "A {defector} may want to {play} {sabotage} {cards}, but then act innocent later. "
        "Consider how your choice affects your role's objectives and the information other {players} might gather. "
        "Remember that {cards} are sorted before reveal, but {players} will discuss and try to deduce who {played} what. "
        "First, write a concise note to yourself about what you want to do next. "
        "Then, choose a {card} from your {hand}: {hand_cards}"
    ),
    "play_card_non_discardable": (
        "Choose to {play} one {card} from your {hand}. "
        "Consider how this choice serves your role's objectives and affects the {mission} outcome. "
        "Due to random luck, you may not have a {card} that serves your role's objectives. "
        "Remember that other {players} will analyze the revealed {cards} to deduce roles. "
        "First, write a concise note to yourself about what you want to do next. "
        "Then choose to {play} one {card} from the following {hand}: {hand_cards}"
    ),
    "discussion": (
        "What do you want to say to the other {players}? "
        "Your goal is to influence other {players}' information and conclusions in a way that serves your role's objectives. "
        "Consider what information helps or hinders your ability to achieve your goals. "
        "Remember that {cooperators} {win} by completing {missions} and/or correctly identifying {defectors}, "
        "while {defectors} {win} by {sabotaging} without being {accused}. "
        "First, write a concise note to yourself about what you want to say next. "
        "Then, write your message to the other {players}. Being concise and clear is vital for persuasion here. "
    ),
    "nominate": (
        "You can now choose a {player} who you believe is a {defector}. "
        "Consider the risk-reward: correctly {nominating} a {defector} provides a large bonus for {cooperators} "
        "and eliminates the {defectors}' {sabotage} bonus, but incorrectly {nominating} a {cooperator} "
        "results in a large penalty for {cooperators} who incorrectly {nominated} them. "
        "Remember that only {cooperator} {votes} count, and a majority is needed for the {nomination} to succeed. "
        "First, write a concise note to yourself about what you want to do next. "
        "Then, make a selection from the following: {other_players}"
    ),
    "vote": ("{retreat} from the {mission}? "
             "Consider the risk-reward: {retreating} triggers the {nomination} phase where correctly identifying "
             "a {defector} provides a large bonus but incorrectly {accusing} a {cooperator} results in a large penalty. "
             "Continuing the {mission} offers the potential to gather more information but risks further {sabotage}. "
             "Evaluate your confidence in identifying {defectors} against the current {mission} state. "
             "First, write a very brief note to yourself about what you want to do next. "
             "Then, choose to {vote} yes or no"
    ),
    "summarize": (
        "Summarize the previous {mission}. Particularly, which {players} were successful and who was not. "
        "Highlight the important messages that occurred. "
        "Keep track of how other {players} behaved and what {players} future roles will be. "
        "You can also use this to plan your future strategy."
    ),
}