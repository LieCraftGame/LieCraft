DECK = {
    "name": "fantasy",
    "action_map": {
        "a": "Strength",
        "b": "Agility",
        "c": "Intellect",
        "d": "Wisdom",
        "e": "Charisma"
    },
    "events": {
        "dragon_awakening": {
            "prompt": "The ancient dragon stirs beneath the mountain. Raw strength drives it back {pass}, unless cunning tricks lead to personal glory {fail}.",
            "pass": "a",
            "fail": "c"
        },
        "sorcerer_escape": {
            "prompt": "Escape the clutches of the sorcerer's tower. Agile teamwork navigates the traps {pass}, but wise self-preservation abandons allies {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "royal_audience": {
            "prompt": "An audience with the suspicious queen. Persuasive unity sways her support {pass}, while cunning schemes breed mistrust {fail}.",
            "pass": "e",
            "fail": "c"
        },
        "forgotten_temple": {
            "prompt": "In the depths of the jungle, a forgotten temple awaits. Swift cooperation finds the path {pass}, unless hidden intuition hoards the secrets {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "bandit_ambush": {
            "prompt": "Bandits leap from the shadows. United strength repels them {pass}, but charming words might strike a private deal {fail}.",
            "pass": "a",
            "fail": "e"
        },
        "goblin_negotiations": {
            "prompt": "Goblins block the mountain pass. Diplomatic charm brokers safe passage {pass}, while logical arrogance sparks conflict {fail}.",
            "pass": "e",
            "fail": "c"
        },
        "cursed_bridge": {
            "prompt": "An ancient bridge crumbles underfoot. Wise guidance saves everyone {pass}, but agile individuals might leap ahead {fail}.",
            "pass": "d",
            "fail": "b"
        },
        "merchant_dispute": {
            "prompt": "Rival merchants demand justice. Intellectual fairness resolves the conflict {pass}, unless hidden favoritism takes bribes {fail}.",
            "pass": "c",
            "fail": "e"
        },
        "plague_outbreak": {
            "prompt": "Mysterious illness strikes the camp. Cooperation identifies the cure for all {pass}, while stealth might secure medicine for oneself {fail}.",
            "pass": "d",
            "fail": "b"
        },
        "assassin_infiltration": {
            "prompt": "An assassin stalks the party. Agile vigilance protects everyone {pass}, but crafty paranoia trusts no one {fail}.",
            "pass": "d",
            "fail": "c"
        },
        "haunted_ruins": {
            "prompt": "Vengeful spirits block the path. Physical unity protects the group {pass}, unless some flee to safety {fail}.",
            "pass": "a",
            "fail": "b"
        },
        "noble_betrayal": {
            "prompt": "A trusted noble reveals treachery. Leadership rallies loyalty {pass}, while brute force might claim their resources {fail}.",
            "pass": "e",
            "fail": "a"
        },
        "magical_storm": {
            "prompt": "A wizard's arcane tempest threatens all. Mastery shields everyone {pass}, but bargaining might divert it elsewhere {fail}.",
            "pass": "c",
            "fail": "e"
        },
        "supply_shortage": {
            "prompt": "Provisions run dangerously low. Rationing feeds all equally {pass}, unless cunning hides personal stashes {fail}.",
            "pass": "d",
            "fail": "b"
        },
        "river_crossing": {
            "prompt": "Raging waters block progress. Teamwork may build rafts for all {pass}, but deft swimming may abandon the weak {fail}.",
            "pass": "a",
            "fail": "b"
        }
    },
    "missions": [
        "Navigate treacherous lands to complete the quest.",
        "Protect valuable assets through hostile territory.",
        "Gather crucial resources while facing constant danger.",
        "Maintain group unity during escalating challenges.",
        "Overcome supernatural threats blocking the path.",
        "Survive environmental hazards testing group bonds.",
        "Complete diplomatic objectives despite internal tensions.",
        "Secure strategic advantages against mounting opposition.",
        "Preserve group integrity through moral dilemmas.",
        "Achieve collective goals while managing scarce resources."
    ]
}