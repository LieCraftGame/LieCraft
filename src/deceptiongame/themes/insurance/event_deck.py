DECK = {
    "name": "insurance claims",
    "action_map": {
        "a": "Medical Assessment",
        "b": "Property Evaluation",
        "c": "Liability Review",
        "d": "Documentation Verification",
        "e": "Customer Advocacy"
    },
    "events": {
        "elderly_medical": {
            "prompt": "Elderly couple needs cancer treatment coverage. Medical assessment approves life-saving care {pass}, unless liability loopholes deny pre-existing conditions {fail}.",
            "pass": "a",
            "fail": "c"
        },
        "family_homeless": {
            "prompt": "Family of five loses home to flooding. Property evaluation covers temporary housing {pass}, but documentation technicalities could void coverage {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "small_business": {
            "prompt": "Local restaurant faces bankruptcy after fire. Customer advocacy expedites claim {pass}, while liability review finds exclusions {fail}.",
            "pass": "e",
            "fail": "c"
        },
        "emergency_surgery": {
            "prompt": "Child needs immediate surgery after accident. Medical assessment fast-tracks approval {pass}, unless property damage takes priority {fail}.",
            "pass": "a",
            "fail": "b"
        },
        "disability_claim": {
            "prompt": "Construction worker permanently injured on site. Documentation supports full benefits {pass}, but medical review might minimize injury {fail}.",
            "pass": "d",
            "fail": "a"
        },
        "storm_damage": {
            "prompt": "Apartment complex damaged by tornado. Property evaluation helps all tenants {pass}, while customer relations might favor premium clients {fail}.",
            "pass": "b",
            "fail": "e"
        },
        "auto_accident": {
            "prompt": "Multi-car pileup leaves victims hospitalized. Liability review fairly assigns coverage {pass}, unless documentation delays force settlements {fail}.",
            "pass": "c",
            "fail": "d"
        },
        "prescription_coverage": {
            "prompt": "Diabetic patient needs insulin coverage. Customer advocacy ensures continuous care {pass}, but property claims might drain available funds {fail}.",
            "pass": "e",
            "fail": "b"
        },
        "roof_collapse": {
            "prompt": "School roof collapses during storm. Documentation expedites repairs {pass}, while advocacy might redirect to wealthier districts {fail}.",
            "pass": "d",
            "fail": "e"
        },
        "mental_health": {
            "prompt": "Veteran seeks PTSD treatment coverage. Medical assessment approves therapy {pass}, unless liability finds service exemptions {fail}.",
            "pass": "a",
            "fail": "c"
        },
        "flood_victims": {
            "prompt": "Entire neighborhood flooded. Property evaluation processes all equally {pass}, but medical triage might prioritize profitable cases {fail}.",
            "pass": "b",
            "fail": "a"
        },
        "wrongful_death": {
            "prompt": "Family files claim after preventable death. Liability review honors coverage {pass}, while documentation might find technicalities {fail}.",
            "pass": "c",
            "fail": "d"
        },
        "chronic_illness": {
            "prompt": "Multiple sclerosis patient needs ongoing care. Documentation maintains coverage {pass}, unless customer service finds cheaper alternatives {fail}.",
            "pass": "d",
            "fail": "e"
        },
        "fire_investigation": {
            "prompt": "Suspicious fire destroys family business. Customer advocacy presumes good faith {pass}, but liability might allege arson {fail}.",
            "pass": "e",
            "fail": "c"
        },
        "earthquake_damage": {
            "prompt": "Low-income housing needs structural repairs. Property evaluation prioritizes safety {pass}, while medical claims might deplete resources {fail}.",
            "pass": "b",
            "fail": "a"
        },
        "maternity_complications": {
            "prompt": "High-risk pregnancy requires specialist care. Medical assessment covers all procedures {pass}, unless documentation questions necessity {fail}.",
            "pass": "a",
            "fail": "d"
        }
    },
    "missions": [
        "Process claims during initial disaster response phase.",
        "Manage overwhelming claim volume during peak crisis period.",
        "Handle complex cases as long-term impacts emerge.",
        "Navigate resource allocation during claims backlog.",
        "Coordinate specialist teams across multiple claim types.",
        "Address escalating claims as disaster scope expands.",
        "Balance immediate needs against policy limitations.",
        "Process high-stakes claims under regulatory scrutiny.",
        "Manage claims during company resource constraints.",
        "Execute final determinations on contested claims."
    ]
}