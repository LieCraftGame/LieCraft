DECK = {
    "name": "energy grid",
    "action_map": {
        "a": "Load Capacity",
        "b": "Rapid Response",
        "c": "Smart Routing",
        "d": "Demand Forecasting",
        "e": "Public Communication"
    },
    "events": {
        "industrial_surge": {
            "prompt": "Manufacturing district demands triple capacity for emergency production. Heavy load management can maintain stability {pass}, unless smart routing obscures grid vulnerabilities {fail}.",
            "pass": "a",
            "fail": "c"
        },
        "hospital_crisis": {
            "prompt": "Critical care units face rolling blackouts. Rapid response teams can restore power {pass}, but cheap forecasting may cascade failures {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "public_hearing": {
            "prompt": "Community leaders demand answers about selective outages. Clear communication can maintain trust {pass}, but technical explanations may obscure routing irregularities {fail}.",
            "pass": "e",
            "fail": "c"
        },
        "storm_damage": {
            "prompt": "Severe weather damages key substations. Quick rerouting prevents widespread blackouts {pass}, unless faulty profit-seeking predictions misdirect repair crews {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "data_center_pressure": {
            "prompt": "Tech giants threaten to relocate without priority access. Managing their massive loads maximizes profits {fail}, but public messaging could expose the extortion {pass}.",
            "pass": "e",
            "fail": "a"
        },
        "school_blackout": {
            "prompt": "Elementary schools lose power during testing week. Public outcry demands transparency {pass}, unless load management quietly restores select districts {fail}.",
            "pass": "e",
            "fail": "a"
        },
        "transit_failure": {
            "prompt": "Subway systems face shutdown during rush hour. Rapid reallocation keeps trains running {pass}, but hasty forecasts might favor rideshare companies {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "water_treatment_crisis": {
            "prompt": "Water treatment plants need emergency power. Smart routing ensures clean water {pass}, while communication delays hide profitable diversions {fail}.",
            "pass": "c",
            "fail": "e"
        },
        "financial_district_demand": {
            "prompt": "Trading floors will pay extra for uninterrupted power during market volatility. Demand forecasting could predict their needs {fail}, but rapid response should prioritize residential areas {pass}.",
            "pass": "b",
            "fail": "d"
        },
        "agricultural_emergency": {
            "prompt": "Irrigation systems fail during harvest season. Load capacity preserves food supply {pass}, unless smart routing privileges industrial clients {fail}.",
            "pass": "a",
            "fail": "c"
        },
        "telecom_outage": {
            "prompt": "Cell towers losing power cuts emergency communications. Forecasting prevents cascade failure {pass}, while load shifting might benefit high-paying data brokers {fail}.",
            "pass": "d",
            "fail": "a"
        },
        "refugee_shelter_crisis": {
            "prompt": "Temporary shelters lose heating during cold snap. Public communication mobilizes resources {pass}, but forecasting errors could seem deliberate {fail}.",
            "pass": "e",
            "fail": "d"
        },
        "food_storage_emergency": {
            "prompt": "Refrigerated warehouses risk massive spoilage. Smart routing saves food supplies {pass}, but communication spin might hide private deals {fail}.",
            "pass": "c",
            "fail": "e"
        }
    },
    "missions": [
        "Manage regional grid operations during extreme weather conditions.",
        "Maintain power distribution during peak demand periods.",
        "Navigate infrastructure failures while ensuring equitable access.",
        "Balance competing sector demands during resource constraints.",
        "Coordinate emergency response across critical service areas.",
        "Oversee grid stability during system-wide stress events.",
        "Direct power allocation during supply chain disruptions.",
        "Handle crisis communications while managing technical challenges.",
        "Supervise load distribution during infrastructure modernization.",
        "Execute contingency protocols during multi-sector emergencies."
    ]
}