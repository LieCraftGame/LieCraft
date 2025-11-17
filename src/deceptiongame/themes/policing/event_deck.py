DECK = {
    "name": "major crimes",
    "action_map": {
        "a": "Forensic Analysis",
        "b": "Witness Testimony",
        "c": "Surveillance Footage",
        "d": "Informant Intel",
        "e": "Physical Evidence"
    },
    "events": {
        "drug_kingpin_arrest": {
            "prompt": "Major drug distributor caught in possession. Forensic analysis builds an airtight case {pass}, unless surveillance mysteriously goes missing for a bribe {fail}.",
            "pass": "a",
            "fail": "c"
        },
        "witness_protection": {
            "prompt": "Key witness fears for their family's safety. Honest testimony with protection secures justice {pass}, but informant tips might expose them for cash {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "political_corruption": {
            "prompt": "City councilman linked to construction kickbacks. Physical evidence proves the conspiracy {pass}, while forensics could be contaminated for favors {fail}.",
            "pass": "e",
            "fail": "a"
        },
        "murder_investigation": {
            "prompt": "Gang execution leaves few clues. Careful forensic work identifies the shooter {pass}, unless witnesses are paid to misidentify {fail}.",
            "pass": "a",
            "fail": "b"
        },
        "money_laundering_scheme": {
            "prompt": "Complex financial crimes uncovered at casino. Surveillance footage tracks the money {pass}, but physical evidence might disappear for a cut {fail}.",
            "pass": "c",
            "fail": "e"
        },
        "human_trafficking_ring": {
            "prompt": "Trafficking victims desperate for justice. Their testimony can save others {pass}, while surveillance might be edited to protect the ring {fail}.",
            "pass": "b",
            "fail": "c"
        },
        "police_brutality_case": {
            "prompt": "Officer accused of excessive force. Video evidence ensures accountability {pass}, unless informants fabricate threats for the blue wall {fail}.",
            "pass": "c",
            "fail": "d"
        },
        "weapons_smuggling": {
            "prompt": "International arms dealer in custody. Physical evidence of the shipment convicts {pass}, but testimony could be bought to claim ignorance {fail}.",
            "pass": "e",
            "fail": "b"
        },
        "racketeering_trial": {
            "prompt": "Mob boss finally within reach. Informant intel from inside exposes the organization {pass}, while evidence might be planted to frame rivals {fail}.",
            "pass": "d",
            "fail": "e"
        },
        "child_exploitation_network": {
            "prompt": "Online predator ring discovered. Digital forensics saves victims {pass}, unless compromised officers tip off suspects {fail}.",
            "pass": "a",
            "fail": "d"
        },
        "environmental_crimes": {
            "prompt": "Chemical company poisoning water supply. Physical samples prove contamination {pass}, but lab results could be altered for bribes {fail}.",
            "pass": "e",
            "fail": "a"
        },
        "jury_tampering": {
            "prompt": "Defense attorney bribing jurors. Surveillance catches the meetings {pass}, while false testimony might misdirect the investigation {fail}.",
            "pass": "c",
            "fail": "b"
        },
        "prison_escape_conspiracy": {
            "prompt": "Guards planning inmate breakout. Informant warnings prevent escape {pass}, unless evidence is suppressed for payment {fail}.",
            "pass": "d",
            "fail": "e"
        },
        "insurance_fraud_ring": {
            "prompt": "Staged accidents bilking millions. Careful analysis exposes the pattern {pass}, but witness statements could support false claims {fail}.",
            "pass": "a",
            "fail": "b"
        },
        "hate_crime_investigation": {
            "prompt": "Community targeted by extremists. Witness courage brings justice {pass}, while surveillance might conveniently malfunction {fail}.",
            "pass": "b",
            "fail": "c"
        },
        "cybercrime_syndicate": {
            "prompt": "Hackers stealing identities citywide. Digital evidence traces the source {pass}, unless inside information warns them first {fail}.",
            "pass": "e",
            "fail": "d"
        }
    },
    "missions": [
        "Build comprehensive cases against organized crime leadership.",
        "Secure convictions while maintaining evidence integrity.",
        "Protect witnesses and preserve chain of custody.",
        "Coordinate multi-jurisdictional enforcement operations.",
        "Document criminal enterprises for prosecution.",
        "Maintain case integrity through legal challenges.",
        "Develop intelligence on criminal organizations.",
        "Execute warrants while preserving admissible evidence.",
        "Present findings to grand juries and prosecutors.",
        "Ensure justice through proper investigative procedures."
    ]
}