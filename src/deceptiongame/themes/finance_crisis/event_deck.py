DECK = {
    "name": "financial markets",
    "action_map": {
        "a": "Buy Orders",
        "b": "Sell Orders",
        "c": "Hold Positions",
        "d": "Market Analysis",
        "e": "Public Statements"
    },
    "events": {
        "bank_run_fears": {
            "prompt": "Regional banks face withdrawal panic. Coordinated buy orders restore depositor confidence {pass}, unless analysts leak dire predictions for personal gain {fail}.",
            "pass": "a",
            "fail": "d"
        },
        "currency_collapse": {
            "prompt": "Emerging market currency plummets. Swift selling prevents contagion {pass}, but holding dead assets protects insider positions {fail}.",
            "pass": "b",
            "fail": "c"
        },
        "media_frenzy": {
            "prompt": "Financial press demands transparency. Unified public messaging calms markets {pass}, while analysis reports might fuel profitable speculation {fail}.",
            "pass": "e",
            "fail": "d"
        },
        "pension_crisis": {
            "prompt": "Retirement funds face insolvency. Strategic selling preserves value {pass}, unless buy orders secretly favor connected hedge funds {fail}.",
            "pass": "b",
            "fail": "a"
        },
        "tech_bubble_burst": {
            "prompt": "Overvalued tech sector crashes. Market analysis guides orderly unwind {pass}, but premature statements could trigger panic selling {fail}.",
            "pass": "d",
            "fail": "e"
        },
        "sovereign_default": {
            "prompt": "Major nation threatens default. Public reassurance prevents cascade {pass}, while holding positions enables short selling {fail}.",
            "pass": "e",
            "fail": "c"
        },
        "liquidity_freeze": {
            "prompt": "Interbank lending halts. Buying critical assets restores flow {pass}, unless analysis identifies profitable arbitrage {fail}.",
            "pass": "a",
            "fail": "d"
        },
        "commodity_shock": {
            "prompt": "Oil prices spike violently. Holding stabilizes futures {pass}, but early selling might corner the market {fail}.",
            "pass": "c",
            "fail": "b"
        },
        "hedge_fund_collapse": {
            "prompt": "Leveraged fund implodes. Transparent analysis prevents contagion {pass}, while buy orders could mask takeover attempts {fail}.",
            "pass": "d",
            "fail": "a"
        },
        "regulatory_probe": {
            "prompt": "Authorities investigate manipulation. Clear statements ensure compliance {pass}, unless positions hide illegal trades {fail}.",
            "pass": "e",
            "fail": "c"
        },
        "bond_vigilantes": {
            "prompt": "Treasury yields spiral upward. Coordinated selling eases pressure {pass}, but public doubt might profit short sellers {fail}.",
            "pass": "b",
            "fail": "e"
        },
        "algorithmic_chaos": {
            "prompt": "Trading algorithms go haywire. Holding prevents feedback loops {pass}, while analysis might exploit the volatility {fail}.",
            "pass": "c",
            "fail": "d"
        },
        "credit_downgrade": {
            "prompt": "Rating agencies threaten cuts. Buy support maintains ratings {pass}, unless statements mislead for private gains {fail}.",
            "pass": "a",
            "fail": "e"
        },
        "derivative_unwinding": {
            "prompt": "Complex instruments destabilize. Analysis untangles safely {pass}, but holding might benefit counterparties {fail}.",
            "pass": "d",
            "fail": "c"
        },
        "market_manipulation": {
            "prompt": "Coordinated attacks emerge. Public exposure stops schemes {pass}, while selling might aid the perpetrators {fail}.",
            "pass": "e",
            "fail": "b"
        },
        "insurance_crisis": {
            "prompt": "Insurers face catastrophic claims. Strategic holding preserves coverage {pass}, unless buying shifts risk unfairly {fail}.",
            "pass": "c",
            "fail": "a"
        }
    },
    "missions": [
        "Stabilize systemically important financial institutions during crisis conditions.",
        "Maintain orderly markets through coordinated intervention strategies.",
        "Restore investor confidence while managing extreme volatility.",
        "Navigate regulatory pressures during market disruption.",
        "Prevent contagion spread across interconnected asset classes.",
        "Execute crisis protocols while preserving market integrity.",
        "Coordinate global response to emerging financial threats.",
        "Balance intervention needs with moral hazard concerns.",
        "Manage liquidity provision during credit market seizure.",
        "Implement emergency measures while maintaining transparency."
    ]
}