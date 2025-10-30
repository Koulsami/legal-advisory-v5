"""
Enhanced Order 21 Logic Tree Nodes with Case Law References
Legal Advisory System v5.0

This module provides ENHANCED logic tree nodes that include explicit
case law references based on the Enhanced Analysis document.

These nodes supplement the existing tree_data.py with judicial interpretations.
"""

from backend.interfaces import LogicTreeNode
from backend.modules.order_21.rule_to_case_mapping import get_cases_for_node


def get_enhanced_order21_nodes():
    """
    Return enhanced pre-built nodes for key Order 21 rules with case law references.

    These nodes include explicit case_law_references field populated from
    the rule_to_case_mapping.py file.
    """
    return [
        # ====================================================================================
        # Rule 2(1) - Court's Discretion on Costs
        # ====================================================================================
        LogicTreeNode(
            node_id="ORDER21_RULE_2_1_DISCRETION",
            citation="Order 21, Rule 2(1) - Court's Discretion on Costs",
            module_id="ORDER_21",
            what=[
                {"definition": "Costs are in the discretion of the Court"},
                {"proposition": "Court has power to determine all issues relating to costs"},
                {"interpretation": "Wide discretionary power not constrained by specific provisions"}
            ],
            which=[
                {"scope": "All proceedings in Supreme Court or State Courts"},
                {"entities": ["parties", "non-parties", "solicitors"]},
                {"classification": "Subject to any written law"}
            ],
            modality=[
                {"obligation": "MAY", "actor": "Court", "action": "determine all cost issues at any stage"}
            ],
            why=[
                {"policy": "Preserve broad judicial discretion over costs"},
                {"rationale": "Flexibility to do justice in diverse circumstances"},
                {"principle": "Power extends beyond statutory enumeration"}
            ],
            case_law_references=[
                "2023_SGCA_40",  # Founder Group - discretion not constrained by r 5
                "2025_SGHCR_18_discretion",  # Armira Capital - discretion factors
            ]
        ),

        # ====================================================================================
        # Rule 2(2) - Factors in Exercising Discretion
        # ====================================================================================
        LogicTreeNode(
            node_id="ORDER21_RULE_2_2_FACTORS",
            citation="Order 21, Rule 2(2) - Factors in Exercising Discretion",
            module_id="ORDER_21",
            what=[
                {"definition": "Court MUST have regard to all relevant circumstances"},
                {"proposition": "Eight non-exhaustive factors listed in sub-rules (a)-(h)"}
            ],
            which=[
                {"factors": [
                    "(a) efforts at amicable resolution",
                    "(b) complexity and difficulty",
                    "(c) skill, knowledge, specialised knowledge, responsibility, time",
                    "(d) urgency and importance",
                    "(e) number of solicitors reasonably required",
                    "(f) conduct of parties",
                    "(g) principle of proportionality",
                    "(h) stage of proceedings"
                ]},
                {"scope": "All cost determinations"}
            ],
            modality=[
                {"obligation": "MUST", "actor": "Court", "action": "have regard to all relevant circumstances"}
            ],
            why=[
                {"policy": "Comprehensive assessment framework"},
                {"rationale": "Balance competing interests fairly"},
                {"principle": "Context-sensitive cost determination"}
            ],
            case_law_references=[
                "2025_SGHCR_18_factors",  # Armira Capital - comprehensive application of all 8 factors
                "2023_SGCA_45_conduct",  # QBE Insurance - conduct factors
            ]
        ),

        # ====================================================================================
        # Rule 2(2)(f) - Conduct of Parties
        # ====================================================================================
        LogicTreeNode(
            node_id="ORDER21_RULE_2_2_F_CONDUCT",
            citation="Order 21, Rule 2(2)(f) - Conduct of Parties",
            module_id="ORDER_21",
            what=[
                {"definition": "Conduct of parties affecting costs award"},
                {"proposition": "Exceptional conduct may warrant indemnity costs"},
                {"interpretation": "Touchstone is unreasonable conduct, not moral condemnation"}
            ],
            which=[
                {"categories": [
                    "Bad faith or oppression",
                    "Speculative/hypothetical/without basis",
                    "Dishonest, abusive or improper conduct",
                    "Wasteful or duplicative litigation"
                ]},
                {"threshold": "Conduct must take case out of the norm"}
            ],
            if_then=[
                {"condition": "completely unmeritorious action brought to intimidate", "result": "indemnity costs may be awarded"},
                {"condition": "withdrawal shortly before hearing without more", "result": "standard costs appropriate"}
            ],
            modality=[
                {"obligation": "MAY", "actor": "Court", "action": "award indemnity costs for exceptional conduct"}
            ],
            why=[
                {"policy": "Deter abusive litigation"},
                {"rationale": "Compensate innocent parties for unreasonable conduct"},
                {"principle": "Indemnity costs remain exceptional"}
            ],
            case_law_references=[
                "2024_SGHC_146_conduct",  # Tjiang Giok Moy - conduct threshold for indemnity
                "2023_SGCA_45_conduct",  # QBE Insurance - exceptional circumstances required
            ]
        ),

        # ====================================================================================
        # Rule 2(2)(g) - Proportionality Principle
        # ====================================================================================
        LogicTreeNode(
            node_id="ORDER21_RULE_2_2_G_PROPORTIONALITY",
            citation="Order 21, Rule 2(2)(g) - Principle of Proportionality",
            module_id="ORDER_21",
            what=[
                {"definition": "Costs must be proportionate to matters in issue"},
                {"proposition": "Proportionality is MANDATORY consideration"},
                {"interpretation": "Applies even to indemnity costs"}
            ],
            which=[
                {"scope": "ALL cost assessments including indemnity basis"},
                {"application": "Foreign lawyers' fees also subject to Singapore proportionality"}
            ],
            modality=[
                {"obligation": "MUST", "actor": "Court", "action": "have regard to proportionality principle"}
            ],
            why=[
                {"policy": "Access to justice - prevent excessive costs"},
                {"rationale": "Costs should not exceed matters at stake"},
                {"principle": "Cannot be contracted out or overridden by foreign rules"}
            ],
            case_law_references=[
                "2025_SGHCR_18_indemnity",  # Armira Capital - mandatory proportionality
            ]
        ),

        # ====================================================================================
        # Rule 2(6) - Power to Stay Appeals for Non-Payment
        # ====================================================================================
        LogicTreeNode(
            node_id="ORDER21_RULE_2_6_STAY",
            citation="Order 21, Rule 2(6) - Power to Stay Appeals for Non-Payment of Costs",
            module_id="ORDER_21",
            what=[
                {"definition": "Express statutory power to stay/dismiss for non-payment"},
                {"proposition": "Court may stay any application, action or appeal if party refuses/neglects to pay costs"},
                {"interpretation": "New provision - more robust than old inherent powers regime"}
            ],
            which=[
                {"scope": "Any application, action or appeal"},
                {"trigger": "Refusal or neglect to pay costs ordered within specified time"},
                {"application": "Costs in present or related proceedings"}
            ],
            if_then=[
                {"condition": "party refuses or neglects to pay costs ordered", "result": "Court may stay or dismiss proceedings"},
                {"condition": "constructive refusal (e.g., refusing service for enforcement)", "result": "may constitute refusal"}
            ],
            modality=[
                {"obligation": "MAY", "actor": "Court", "action": "stay or dismiss or make any other order"},
                {"note": "Discretionary but no longer requires 'special or exceptional circumstances'"}
            ],
            why=[
                {"policy": "Enforce costs orders and prevent abuse of appeals"},
                {"rationale": "Appellants should not evade payment while pursuing appeals"},
                {"principle": "Lower threshold than old inherent powers regime"}
            ],
            case_law_references=[
                "2024_SGHCA_33",  # Huttons Asia - express statutory power
                "2024_SGHCA_33_discretion",  # Huttons Asia - judicious exercise of discretion
            ]
        ),

        # ====================================================================================
        # Rule 3(2) - Costs Follow the Event
        # ====================================================================================
        LogicTreeNode(
            node_id="ORDER21_RULE_3_2_COSTS_FOLLOW_EVENT",
            citation="Order 21, Rule 3(2) - Costs Follow the Event",
            module_id="ORDER_21",
            what=[
                {"definition": "Successful party normally entitled to costs"},
                {"proposition": "Court MUST order costs in favour of successful party except when circumstances warrant otherwise"},
                {"interpretation": "Fundamental principle of costs law"}
            ],
            which=[
                {"scope": "Any proceedings where there is a successful party"},
                {"entities": ["successful party"]},
                {"exceptions": "When it appears circumstances warrant different order"}
            ],
            if_then=[
                {"condition": "party is successful", "result": "costs must be awarded unless circumstances warrant otherwise"},
                {"condition": "party has locus standi and objections succeed", "result": "entitled to costs as successful party"}
            ],
            modality=[
                {"obligation": "MUST", "actor": "Court", "action": "order costs in favour of successful party"},
                {"qualifier": "Except when circumstances warrant different order"}
            ],
            why=[
                {"policy": "Winner should not be out of pocket"},
                {"rationale": "Incentivize reasonable litigation conduct"},
                {"principle": "Natural justice - parties with standing entitled to be heard and recover costs"}
            ],
            case_law_references=[
                "2024_SGHC_146",  # Tjiang Giok Moy - successful party entitlement
            ]
        ),

        # ====================================================================================
        # Rule 5 - Non-Party Costs Orders
        # ====================================================================================
        LogicTreeNode(
            node_id="ORDER21_RULE_5_NON_PARTY",
            citation="Order 21, Rule 5 - Adverse Costs Orders Against Non-Parties",
            module_id="ORDER_21",
            what=[
                {"definition": "Court may order costs against non-parties"},
                {"proposition": "Specific grounds in r 5(1) do not exhaust Court's power under r 2(1)"},
                {"interpretation": "R 5 not an exhaustive code - broad residual power remains"}
            ],
            which=[
                {"categories": [
                    "r 5(1)(a) - Vexatious/frivolous/abuse conduct",
                    "r 5(1)(b) - Improper interference with administration of justice",
                    "r 5(1)(c) - Failure to comply without reasonable excuse"
                ]},
                {"non-parties": ["directors", "shareholders", "funders", "controllers"]}
            ],
            if_then=[
                {"condition": "close connection + causation + insolvency", "result": "may order costs against directors even without impropriety"},
                {"condition": "non-party funds/controls litigation intending to benefit", "result": "may be ordered to pay costs"}
            ],
            modality=[
                {"obligation": "MAY", "actor": "Court", "action": "order costs against non-parties where just to do so"}
            ],
            why=[
                {"policy": "Prevent abuse of corporate veil"},
                {"rationale": "Protect litigants from impecunious companies controlled by solvent directors"},
                {"principle": "Corporate separate liability not absolute"}
            ],
            case_law_references=[
                "2023_SGCA_40",  # Founder Group - directors/shareholders liability framework
            ]
        ),

        # ====================================================================================
        # Rule 6 - Personal Costs Orders Against Solicitors
        # ====================================================================================
        LogicTreeNode(
            node_id="ORDER21_RULE_6_SOLICITOR_COSTS",
            citation="Order 21, Rule 6 - Personal Costs Orders Against Solicitors",
            module_id="ORDER_21",
            what=[
                {"definition": "Court may make personal costs orders against advocates and solicitors"},
                {"proposition": "Codifies inherent power to supervise officers of court"},
                {"interpretation": "Applies to citing AI-generated fictitious authorities"}
            ],
            which=[
                {"scope": "Advocates and solicitors as officers of court"},
                {"conduct": ["Unjustifiable conduct", "Conduct tending to defeat justice", "Citing fictitious AI authorities"]}
            ],
            if_then=[
                {"condition": "solicitor cites fictitious AI authority", "result": "may attract personal costs order"},
                {"condition": "counterparty incurs costs addressing fictitious authority", "result": "solicitor may compensate"}
            ],
            modality=[
                {"obligation": "MAY", "actor": "Court", "action": "order solicitor to pay costs personally"}
            ],
            why=[
                {"policy": "Maintain integrity of justice system"},
                {"rationale": "Solicitors must verify AI-generated content"},
                {"principle": "Compensatory, not merely punitive"}
            ],
            case_law_references=[
                "2025_SGHCR_33",  # Tajudin - AI-generated authorities framework
            ]
        ),

        # ====================================================================================
        # Rule 7 - Costs for Litigants-in-Person
        # ====================================================================================
        LogicTreeNode(
            node_id="ORDER21_RULE_7_LIP_COSTS",
            citation="Order 21, Rule 7 - Costs for Litigants-in-Person",
            module_id="ORDER_21",
            what=[
                {"definition": "Court may award costs to successful litigant-in-person"},
                {"proposition": "Reasonable compensation for time and work required and expenses incurred"},
                {"interpretation": "Not automatic - discretionary and only for successful parties"}
            ],
            which=[
                {"scope": "Litigants-in-person (not represented by solicitors)"},
                {"compensation": "Time and work REQUIRED for proceedings + reasonable expenses"}
            ],
            if_then=[
                {"condition": "litigant-in-person is successful", "result": "Court may award reasonable compensation"},
                {"condition": "litigant-in-person is unsuccessful", "result": "No costs entitlement"}
            ],
            modality=[
                {"obligation": "MAY", "actor": "Court", "action": "award costs to successful LIP"},
                {"note": "Permissive, not mandatory"}
            ],
            why=[
                {"policy": "Access to justice for self-represented litigants"},
                {"rationale": "Work income not proper measure (protects homemakers/retirees)"},
                {"principle": "Costs follow event applies equally to LIPs"}
            ],
            case_law_references=[
                "2022_SGHC_232",  # Chan Hui Peng - LIP costs principles
            ]
        ),

        # ====================================================================================
        # Rule 22(3) - Assessment on Indemnity Basis
        # ====================================================================================
        LogicTreeNode(
            node_id="ORDER21_RULE_22_3_INDEMNITY",
            citation="Order 21, Rule 22(3) - Assessment on Indemnity Basis",
            module_id="ORDER_21",
            what=[
                {"definition": "All costs allowed except unreasonable amount or unreasonably incurred"},
                {"proposition": "Doubts resolved in favour of receiving party"},
                {"interpretation": "Not automatic acceptance - reasonableness still required"}
            ],
            which=[
                {"scope": "Costs assessed on indemnity basis"},
                {"standard": "All costs EXCEPT unreasonable (inverse of standard basis)"}
            ],
            if_then=[
                {"condition": "costs on indemnity basis", "result": "all costs allowed unless unreasonable"},
                {"condition": "doubt about reasonableness", "result": "resolved in favour of receiving party"},
                {"condition": "contractual indemnity", "result": "does not fetter court's discretion"}
            ],
            modality=[
                {"obligation": "SHALL", "actor": "Registrar", "action": "allow all costs except unreasonable"},
                {"note": "Contractual clauses cannot override court discretion"}
            ],
            why=[
                {"policy": "More generous recovery than standard basis"},
                {"rationale": "Still subject to reasonableness and proportionality"},
                {"principle": "Lin Jian Wei framework continues to apply"}
            ],
            case_law_references=[
                "2025_SGHCR_18_indemnity",  # Armira Capital - indemnity assessment principles
                "2025_SGHCR_18_purpose",  # Armira Capital - purpose and scope
            ]
        ),
    ]


# Convenience function to get a specific enhanced node
def get_enhanced_node_by_id(node_id: str) -> LogicTreeNode:
    """
    Get a specific enhanced node by its ID.

    Args:
        node_id: Node identifier

    Returns:
        LogicTreeNode or None if not found
    """
    nodes = get_enhanced_order21_nodes()
    for node in nodes:
        if node.node_id == node_id:
            return node
    return None
