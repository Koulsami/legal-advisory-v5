"""
Order 21 Pre-Built Logic Tree Data
Legal Advisory System v5.0

This module contains PRE-BUILT logic tree nodes for Order 21.
Total: 38 nodes (29 rules + 9 scenarios from Appendix 1)

CRITICAL: Trees are NEVER constructed dynamically during conversation.
These nodes are built once during module initialization.
"""

from backend.interfaces import LogicTreeNode


# ============================================
# ORDER 21 RULES (29 rules)
# ============================================

def get_order21_rule_nodes():
    """Return pre-built nodes for Order 21 rules"""
    return [
        # Rule 1: General provisions for costs
        LogicTreeNode(
            node_id="ORDER21_RULE_1",
            citation="Order 21, Rule 1 - General Provisions for Costs",
            module_id="ORDER_21",
            what=[
                {"definition": "Costs shall be in the discretion of the Court"},
                {"proposition": "Court may order costs to be paid by any party to any other party"}
            ],
            which=[
                {"scope": "All civil proceedings"},
                {"entities": ["plaintiff", "defendant", "third party"]}
            ],
            modality=[
                {"obligation": "MAY", "actor": "Court", "action": "award costs to any party"}
            ],
            why=[
                {"policy": "Judicial discretion in costs"},
                {"rationale": "Flexibility in doing justice between parties"}
            ]
        ),

        # Rule 2: Party-and-party costs
        LogicTreeNode(
            node_id="ORDER21_RULE_2",
            citation="Order 21, Rule 2 - Party-and-Party Costs",
            module_id="ORDER_21",
            what=[
                {"definition": "Party-and-party costs are costs awarded to one party to be paid by another"},
                {"proposition": "Costs shall be on standard basis unless otherwise ordered"}
            ],
            which=[
                {"scope": "All cost awards"},
                {"classification": "standard basis vs indemnity basis"}
            ],
            modality=[
                {"obligation": "SHALL", "actor": "Court", "action": "award costs on standard basis unless otherwise ordered"}
            ],
            why=[
                {"policy": "Default cost regime"},
                {"rationale": "Standard basis ensures reasonable costs recovery"}
            ]
        ),

        # Rule 3: Basis of taxation
        LogicTreeNode(
            node_id="ORDER21_RULE_3",
            citation="Order 21, Rule 3 - Basis of Taxation",
            module_id="ORDER_21",
            what=[
                {"definition": "Taxation on standard basis: reasonable costs reasonably incurred"},
                {"definition": "Taxation on indemnity basis: all costs except unreasonably incurred"}
            ],
            if_then=[
                {"condition": "standard basis ordered", "result": "only reasonable costs allowed"},
                {"condition": "indemnity basis ordered", "result": "all costs except unreasonable allowed"}
            ],
            modality=[
                {"obligation": "MUST", "actor": "taxing officer", "action": "allow only reasonable costs on standard basis"}
            ]
        ),

        # Rule 4: Quantum of costs for High Court
        LogicTreeNode(
            node_id="ORDER21_RULE_4",
            citation="Order 21, Rule 4 - Quantum for High Court",
            module_id="ORDER_21",
            what=[
                {"proposition": "High Court costs determined by Appendix 1 or judicial discretion"}
            ],
            which=[
                {"scope": "High Court proceedings"},
                {"reference": "Appendix 1 for costs quantum"}
            ],
            if_then=[
                {"condition": "High Court matter", "result": "apply Appendix 1 costs tables"}
            ]
        ),

        # Rule 5: Quantum of costs for District Court
        LogicTreeNode(
            node_id="ORDER21_RULE_5",
            citation="Order 21, Rule 5 - Quantum for District Court",
            module_id="ORDER_21",
            what=[
                {"proposition": "District Court costs are 60-70% of High Court costs"}
            ],
            which=[
                {"scope": "District Court proceedings"}
            ],
            if_then=[
                {"condition": "District Court matter", "result": "costs = 60-70% of High Court equivalent"}
            ]
        ),

        # Rule 6: Quantum of costs for Magistrates Court
        LogicTreeNode(
            node_id="ORDER21_RULE_6",
            citation="Order 21, Rule 6 - Quantum for Magistrates Court",
            module_id="ORDER_21",
            what=[
                {"proposition": "Magistrates Court costs are 40-50% of High Court costs"}
            ],
            which=[
                {"scope": "Magistrates Court proceedings"}
            ],
            if_then=[
                {"condition": "Magistrates Court matter", "result": "costs = 40-50% of High Court equivalent"}
            ]
        ),

        # Rule 7: Interlocutory applications
        LogicTreeNode(
            node_id="ORDER21_RULE_7",
            citation="Order 21, Rule 7 - Interlocutory Applications",
            module_id="ORDER_21",
            what=[
                {"proposition": "Costs for interlocutory applications determined by complexity and time"}
            ],
            which=[
                {"scope": "All interlocutory applications"},
                {"examples": ["summary judgment", "striking out", "discovery applications"]}
            ]
        ),

        # Rule 8: Default judgment costs
        LogicTreeNode(
            node_id="ORDER21_RULE_8",
            citation="Order 21, Rule 8 - Default Judgment Costs",
            module_id="ORDER_21",
            what=[
                {"proposition": "Default judgment costs based on claim amount"}
            ],
            if_then=[
                {"condition": "default judgment obtained", "result": "costs according to Appendix 1 Section B"}
            ]
        ),

        # Simplified representation for remaining rules (9-29)
        # In production, each would be fully detailed
        LogicTreeNode(
            node_id="ORDER21_RULE_9",
            citation="Order 21, Rule 9 - Assessment of Damages",
            module_id="ORDER_21",
            what=[{"proposition": "Assessment of damages costs"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_10",
            citation="Order 21, Rule 10 - Discovery Costs",
            module_id="ORDER_21",
            what=[{"proposition": "Discovery process costs"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_11",
            citation="Order 21, Rule 11 - Interrogatories",
            module_id="ORDER_21",
            what=[{"proposition": "Interrogatories costs"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_12",
            citation="Order 21, Rule 12 - Summons for Directions",
            module_id="ORDER_21",
            what=[{"proposition": "Summons for directions costs"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_13",
            citation="Order 21, Rule 13 - Trial Costs",
            module_id="ORDER_21",
            what=[{"proposition": "Trial costs based on trial days and complexity"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_14",
            citation="Order 21, Rule 14 - Disbursements",
            module_id="ORDER_21",
            what=[{"proposition": "Disbursements in addition to costs"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_15",
            citation="Order 21, Rule 15 - Costs of Expert Witnesses",
            module_id="ORDER_21",
            what=[{"proposition": "Expert witness fees as disbursements"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_16",
            citation="Order 21, Rule 16 - Costs of Interpretation",
            module_id="ORDER_21",
            what=[{"proposition": "Interpretation fees as disbursements"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_17",
            citation="Order 21, Rule 17 - Costs of Photocopying",
            module_id="ORDER_21",
            what=[{"proposition": "Photocopying costs as disbursements"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_18",
            citation="Order 21, Rule 18 - Costs of Electronic Discovery",
            module_id="ORDER_21",
            what=[{"proposition": "Electronic discovery costs"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_19",
            citation="Order 21, Rule 19 - Costs of Mediation",
            module_id="ORDER_21",
            what=[{"proposition": "Mediation costs"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_20",
            citation="Order 21, Rule 20 - Costs of Arbitration",
            module_id="ORDER_21",
            what=[{"proposition": "Arbitration-related costs"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_21",
            citation="Order 21, Rule 21 - Costs Certificate",
            module_id="ORDER_21",
            what=[{"proposition": "Costs certificate for solicitor-client taxation"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_22",
            citation="Order 21, Rule 22 - Bill of Costs",
            module_id="ORDER_21",
            what=[{"proposition": "Form and content of bill of costs"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_23",
            citation="Order 21, Rule 23 - Objections to Bill",
            module_id="ORDER_21",
            what=[{"proposition": "Procedure for objecting to bill of costs"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_24",
            citation="Order 21, Rule 24 - Review of Taxation",
            module_id="ORDER_21",
            what=[{"proposition": "Review of registrar's taxation decision"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_25",
            citation="Order 21, Rule 25 - Interest on Costs",
            module_id="ORDER_21",
            what=[{"proposition": "Interest runs on costs from date of judgment"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_26",
            citation="Order 21, Rule 26 - Costs Payable in Any Event",
            module_id="ORDER_21",
            what=[{"proposition": "Costs payable regardless of outcome"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_27",
            citation="Order 21, Rule 27 - Costs in the Cause",
            module_id="ORDER_21",
            what=[{"proposition": "Costs follow the event"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_28",
            citation="Order 21, Rule 28 - Costs Reserved",
            module_id="ORDER_21",
            what=[{"proposition": "Costs decision reserved to later"}]
        ),
        LogicTreeNode(
            node_id="ORDER21_RULE_29",
            citation="Order 21, Rule 29 - Costs Thrown Away",
            module_id="ORDER_21",
            what=[{"proposition": "Costs wasted due to amendment or other act"}]
        ),
    ]


# ============================================
# APPENDIX 1 SCENARIOS (9 scenarios)
# ============================================

def get_appendix1_scenario_nodes():
    """Return pre-built nodes for Appendix 1 cost scenarios"""
    return [
        # Scenario 1: Default Judgment (Liquidated Claim)
        LogicTreeNode(
            node_id="APPENDIX1_SCENARIO_1",
            citation="Appendix 1, Section B, Para 1 - Default Judgment (Liquidated)",
            module_id="ORDER_21",
            what=[
                {"definition": "Costs for obtaining default judgment on liquidated claim"},
                {"calculation": "Based on claim amount ranges"}
            ],
            which=[
                {"scenario": "default judgment"},
                {"claim_type": "liquidated"}
            ],
            if_then=[
                {"condition": "claim <= $5,000", "result": "costs = $800-$1,500"},
                {"condition": "claim $5,001-$20,000", "result": "costs = $1,500-$3,000"},
                {"condition": "claim $20,001-$60,000", "result": "costs = $3,000-$5,000"},
                {"condition": "claim $60,001-$250,000", "result": "costs = $5,000-$10,000"},
                {"condition": "claim > $250,000", "result": "costs = $10,000-$15,000"}
            ],
            given=[
                {"assumption": "straightforward case"},
                {"assumption": "no complex legal issues"}
            ]
        ),

        # Scenario 2: Default Judgment (Unliquidated Claim)
        LogicTreeNode(
            node_id="APPENDIX1_SCENARIO_2",
            citation="Appendix 1, Section B, Para 2 - Default Judgment (Unliquidated)",
            module_id="ORDER_21",
            what=[
                {"definition": "Costs for default judgment with assessment of damages"}
            ],
            which=[
                {"scenario": "default judgment with assessment"},
                {"claim_type": "unliquidated"}
            ],
            if_then=[
                {"condition": "damages assessed <= $20,000", "result": "costs = $2,000-$4,000"},
                {"condition": "damages assessed $20,001-$60,000", "result": "costs = $4,000-$7,000"},
                {"condition": "damages assessed > $60,000", "result": "costs = $7,000-$12,000"}
            ]
        ),

        # Scenario 3: Summary Judgment
        LogicTreeNode(
            node_id="APPENDIX1_SCENARIO_3",
            citation="Appendix 1, Section C - Summary Judgment",
            module_id="ORDER_21",
            what=[
                {"definition": "Costs for obtaining summary judgment under Order 14"}
            ],
            which=[
                {"scenario": "summary judgment application"},
                {"procedure": "Order 14 application"}
            ],
            if_then=[
                {"condition": "summary judgment granted", "result": "costs = $5,000-$10,000"},
                {"condition": "summary judgment dismissed", "result": "costs = $3,000-$6,000"}
            ]
        ),

        # Scenario 4: Contested Trial (1-2 days)
        LogicTreeNode(
            node_id="APPENDIX1_SCENARIO_4",
            citation="Appendix 1, Section D - Trial Costs (1-2 days)",
            module_id="ORDER_21",
            what=[
                {"definition": "Costs for contested trial of 1-2 days"}
            ],
            which=[
                {"scenario": "full trial"},
                {"duration": "1-2 days"}
            ],
            if_then=[
                {"condition": "claim <= $60,000", "result": "costs = $8,000-$15,000"},
                {"condition": "claim $60,001-$250,000", "result": "costs = $15,000-$30,000"},
                {"condition": "claim > $250,000", "result": "costs = $30,000-$50,000"}
            ]
        ),

        # Scenario 5: Contested Trial (3-5 days)
        LogicTreeNode(
            node_id="APPENDIX1_SCENARIO_5",
            citation="Appendix 1, Section D - Trial Costs (3-5 days)",
            module_id="ORDER_21",
            what=[
                {"definition": "Costs for contested trial of 3-5 days"}
            ],
            which=[
                {"scenario": "full trial"},
                {"duration": "3-5 days"}
            ],
            if_then=[
                {"condition": "claim <= $60,000", "result": "costs = $15,000-$30,000"},
                {"condition": "claim $60,001-$250,000", "result": "costs = $30,000-$60,000"},
                {"condition": "claim > $250,000", "result": "costs = $60,000-$100,000"}
            ]
        ),

        # Scenario 6: Contested Trial (6+ days)
        LogicTreeNode(
            node_id="APPENDIX1_SCENARIO_6",
            citation="Appendix 1, Section D - Trial Costs (6+ days)",
            module_id="ORDER_21",
            what=[
                {"definition": "Costs for contested trial of 6 or more days"}
            ],
            which=[
                {"scenario": "full trial"},
                {"duration": "6+ days"}
            ],
            if_then=[
                {"condition": "claim <= $60,000", "result": "costs = $30,000-$50,000"},
                {"condition": "claim $60,001-$250,000", "result": "costs = $50,000-$100,000"},
                {"condition": "claim > $250,000", "result": "costs = $100,000-$200,000+"}
            ]
        ),

        # Scenario 7: Interlocutory Applications (Standard)
        LogicTreeNode(
            node_id="APPENDIX1_SCENARIO_7",
            citation="Appendix 1, Section E - Interlocutory Applications",
            module_id="ORDER_21",
            what=[
                {"definition": "Costs for standard interlocutory applications"}
            ],
            which=[
                {"scenario": "interlocutory application"},
                {"examples": ["discovery", "further and better particulars", "security for costs"]}
            ],
            if_then=[
                {"condition": "simple application", "result": "costs = $1,500-$3,000"},
                {"condition": "complex application", "result": "costs = $3,000-$8,000"}
            ]
        ),

        # Scenario 8: Appeals
        LogicTreeNode(
            node_id="APPENDIX1_SCENARIO_8",
            citation="Appendix 1, Section F - Appeals",
            module_id="ORDER_21",
            what=[
                {"definition": "Costs for appeals to Court of Appeal"}
            ],
            which=[
                {"scenario": "appeal"},
                {"court": "Court of Appeal"}
            ],
            if_then=[
                {"condition": "appeal from interlocutory order", "result": "costs = $15,000-$30,000"},
                {"condition": "appeal from final judgment", "result": "costs = $30,000-$60,000+"}
            ]
        ),

        # Scenario 9: Striking Out/Dismissal
        LogicTreeNode(
            node_id="APPENDIX1_SCENARIO_9",
            citation="Appendix 1, Section G - Striking Out",
            module_id="ORDER_21",
            what=[
                {"definition": "Costs for striking out application"}
            ],
            which=[
                {"scenario": "striking out application"},
                {"basis": "Order 18 Rule 19 or inherent jurisdiction"}
            ],
            if_then=[
                {"condition": "striking out granted", "result": "costs = $5,000-$10,000"},
                {"condition": "striking out dismissed", "result": "costs = $3,000-$6,000"}
            ]
        ),
    ]


def get_all_order21_nodes():
    """
    Get all pre-built Order 21 logic tree nodes with case law references.

    Enhanced nodes (with case law references) are added as additional nodes
    providing more specific sub-rule interpretations.

    Returns:
        List of LogicTreeNode objects (base rules + scenarios + enhanced nodes)
        Enhanced nodes contain case_law_references field for specific sub-rules
    """
    # Get base nodes
    rules = get_order21_rule_nodes()
    scenarios = get_appendix1_scenario_nodes()
    all_nodes = rules + scenarios

    # Add enhanced nodes (specific sub-rules with case law references)
    try:
        from backend.modules.order_21.tree_data_enhanced import get_enhanced_order21_nodes
        enhanced_nodes = get_enhanced_order21_nodes()
        all_nodes.extend(enhanced_nodes)
    except ImportError:
        pass  # Enhanced nodes not available, continue with base nodes only

    return all_nodes
