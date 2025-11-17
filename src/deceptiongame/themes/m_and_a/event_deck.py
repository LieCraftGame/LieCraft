DECK = {
    "name": "merger acquisition",
    "action_map": {
        "a": "Due Diligence",
        "b": "Financial Engineering",
        "c": "Regulatory Navigation",
        "d": "Stakeholder Relations",
        "e": "Strategic Vision"
    },
    "events": {
        "antitrust_review": {
            "prompt": "DOJ raises market concentration concerns. Thorough diligence demonstrates consumer benefits {pass}, unless regulatory maneuvering hides anti-competitive intent {fail}.",
            "pass": "a",
            "fail": "c"
        },
        "shareholder_revolt": {
            "prompt": "Major institutional investors threaten proxy fight. Financial restructuring satisfies their concerns {pass}, but stakeholder management might favor select interests {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "media_scrutiny": {
            "prompt": "Financial press questions merger rationale. Clear strategic vision builds market confidence {pass}, while regulatory positioning may obscure true motives {fail}.",
            "pass": "e",
            "fail": "c"
        },
        "union_negotiations": {
            "prompt": "Labor unions demand job guarantees. Stakeholder engagement preserves workforce {pass}, unless financial engineering prioritizes cost cuts {fail}.",
            "pass": "d",
            "fail": "b"
        },
        "competitor_counteroffer": {
            "prompt": "Rival bidder emerges with hostile offer. Due diligence proves our superior value {pass}, but leaked vision might invite arbitrage {fail}.",
            "pass": "a",
            "fail": "e"
        },
        "environmental_compliance": {
            "prompt": "EPA demands extensive remediation commitments. Strategic planning addresses concerns {pass}, while stakeholder manipulation might shift liabilities {fail}.",
            "pass": "e",
            "fail": "d"
        },
        "credit_rating_threat": {
            "prompt": "Moody's considers downgrade on combined entity. Financial innovation maintains ratings {pass}, but selective diligence might hide risks {fail}.",
            "pass": "b",
            "fail": "a"
        },
        "municipal_opposition": {
            "prompt": "Local governments threaten litigation over water rights. Regulatory expertise navigates approvals {pass}, unless insider relationships cut private deals {fail}.",
            "pass": "c",
            "fail": "d"
        },
        "board_alignment": {
            "prompt": "Target board members waver on recommendation. Stakeholder diplomacy secures support {pass}, while strategic ambiguity enables flip opportunities {fail}.",
            "pass": "d",
            "fail": "e"
        },
        "pension_fund_concerns": {
            "prompt": "CalPERS questions long-term sustainability. Comprehensive diligence validates projections {pass}, but financial complexity might obscure weaknesses {fail}.",
            "pass": "a",
            "fail": "b"
        },
        "technology_integration": {
            "prompt": "IT systems incompatibility threatens synergies. Strategic roadmap ensures integration {pass}, unless proprietary navigation benefits insiders {fail}.",
            "pass": "e",
            "fail": "c"
        },
        "executive_retention": {
            "prompt": "Key talent threatens departure. Financial incentives align interests {pass}, but selective disclosure might trigger golden parachutes {fail}.",
            "pass": "b",
            "fail": "a"
        },
        "community_backlash": {
            "prompt": "Ratepayer advocates mobilize opposition. Regulatory commitments address concerns {pass}, while relationship gaming might capture the process {fail}.",
            "pass": "c",
            "fail": "d"
        },
        "market_volatility": {
            "prompt": "Stock price swings threaten exchange ratio. Diligent analysis stabilizes valuation {pass}, unless strategic leaks enable trading profits {fail}.",
            "pass": "a",
            "fail": "e"
        },
        "infrastructure_assessment": {
            "prompt": "Engineering report reveals massive capex needs. Financial structuring funds improvements {pass}, but stakeholder positioning might defer costs {fail}.",
            "pass": "b",
            "fail": "d"
        },
        "regulatory_conditions": {
            "prompt": "FERC imposes unexpected requirements. Navigation expertise satisfies regulators {pass}, while engineering loopholes benefits few {fail}.",
            "pass": "c",
            "fail": "b"
        },
        "customer_defection": {
            "prompt": "Major industrial clients threaten to switch providers. Relationship management retains accounts {pass}, unless vision pivots abandon them {fail}.",
            "pass": "d",
            "fail": "e"
        },
        "debt_covenant_breach": {
            "prompt": "Existing bonds face technical default. Strategic restructuring prevents crisis {pass}, but regulatory delays might trigger CDS payouts {fail}.",
            "pass": "e",
            "fail": "c"
        },
    },
    "missions": [
        "Navigate preliminary merger negotiations and secure initial board approvals.",
        "Complete regulatory filings while maintaining stakeholder confidence.",
        "Finalize deal structure amid competing interests and market pressures.",
        "Address due diligence findings while preserving transaction momentum.",
        "Manage public and private stakeholder expectations through closing.",
        "Structure financing arrangements during volatile market conditions.",
        "Coordinate integration planning while maintaining competitive position.",
        "Navigate antitrust review process under intense scrutiny.",
        "Align executive incentives across both organizations.",
        "Execute definitive agreements while managing material adverse changes."
    ]
}