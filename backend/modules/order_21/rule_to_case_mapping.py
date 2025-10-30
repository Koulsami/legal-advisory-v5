"""
Rule-to-Case-Law Mapping for Order 21
Legal Advisory System v5.0

This module provides explicit mappings between Order 21 rules/sub-rules
and relevant case law from the case_law_data.py database.

Based on: Order_21_Enhanced_Analysis.docx
Compiled: October 30, 2025
"""

from typing import Dict, List

# Mapping of logic tree node IDs to case law IDs
# This creates explicit linkages between rules and judicial interpretations
RULE_TO_CASE_MAPPING: Dict[str, List[str]] = {

    # Rule 2(1) - Court's Discretion on Costs
    "ORDER21_RULE_2_1_DISCRETION": [
        "2023_SGCA_40",  # Founder Group - broad discretionary power
        "2025_SGHCR_18_discretion",  # Armira Capital - discretion factors
    ],

    # Rule 2(2) - Factors in Exercising Discretion
    "ORDER21_RULE_2_2_FACTORS": [
        "2025_SGHCR_18_factors",  # Armira Capital - all 8 factors
        "2023_SGCA_45_conduct",  # QBE Insurance - conduct factors
    ],

    # Rule 2(2)(f) - Conduct of Parties
    "ORDER21_RULE_2_2_F_CONDUCT": [
        "2024_SGHC_146_conduct",  # Tjiang Giok Moy - conduct for indemnity costs
        "2023_SGCA_45_conduct",  # QBE Insurance - exceptional circumstances required
    ],

    # Rule 2(2)(g) - Proportionality Principle
    "ORDER21_RULE_2_2_G_PROPORTIONALITY": [
        "2025_SGHCR_18_indemnity",  # Armira Capital - mandatory proportionality
    ],

    # Rule 2(6) - Power to Stay Appeals
    "ORDER21_RULE_2_6_STAY": [
        "2024_SGHCA_33",  # Huttons Asia - express statutory power
        "2024_SGHCA_33_discretion",  # Huttons Asia - discretion in exercise
    ],

    # Rule 3(2) - Costs Follow the Event
    "ORDER21_RULE_3_2_COSTS_FOLLOW_EVENT": [
        "2024_SGHC_146",  # Tjiang Giok Moy - successful party entitlement
    ],

    # Rule 5 - Non-Party Costs Orders
    "ORDER21_RULE_5_NON_PARTY": [
        "2023_SGCA_40",  # Founder Group - directors/shareholders liability
    ],

    # Rule 6 - Personal Costs Orders Against Solicitors
    "ORDER21_RULE_6_SOLICITOR_COSTS": [
        "2025_SGHCR_33",  # Tajudin - AI-generated authorities sanctions
    ],

    # Rule 7 - Costs for Litigants-in-Person
    "ORDER21_RULE_7_LIP_COSTS": [
        "2022_SGHC_232",  # Chan Hui Peng - LIP costs principles
    ],

    # Rule 20 - Bill of Costs Requirements
    "ORDER21_RULE_20_BILL_COSTS": [
        "2025_SGHCR_18_bill",  # Armira Capital - bill of costs assessment
    ],

    # Rule 22(3) - Assessment on Indemnity Basis
    "ORDER21_RULE_22_3_INDEMNITY": [
        "2025_SGHCR_18_indemnity",  # Armira Capital - indemnity assessment
        "2025_SGHCR_18_purpose",  # Armira Capital - purpose and scope
    ],
}

# Reverse mapping: case law ID to rules it illustrates
CASE_TO_RULE_MAPPING: Dict[str, List[str]] = {
    "2024_SGHCA_33": ["ORDER21_RULE_2_6_STAY"],
    "2024_SGHCA_33_discretion": ["ORDER21_RULE_2_6_STAY"],
    "2023_SGCA_40": ["ORDER21_RULE_2_1_DISCRETION", "ORDER21_RULE_5_NON_PARTY"],
    "2024_SGHC_146": ["ORDER21_RULE_3_2_COSTS_FOLLOW_EVENT"],
    "2024_SGHC_146_conduct": ["ORDER21_RULE_2_2_F_CONDUCT"],
    "2025_SGHCR_18_discretion": ["ORDER21_RULE_2_1_DISCRETION"],
    "2025_SGHCR_18_factors": ["ORDER21_RULE_2_2_FACTORS"],
    "2025_SGHCR_18_indemnity": ["ORDER21_RULE_2_2_G_PROPORTIONALITY", "ORDER21_RULE_22_3_INDEMNITY"],
    "2025_SGHCR_18_purpose": ["ORDER21_RULE_22_3_INDEMNITY"],
    "2025_SGHCR_18_bill": ["ORDER21_RULE_20_BILL_COSTS"],
    "2023_SGCA_45_conduct": ["ORDER21_RULE_2_2_F_CONDUCT", "ORDER21_RULE_2_2_FACTORS"],
    "2025_SGHCR_33": ["ORDER21_RULE_6_SOLICITOR_COSTS"],
    "2022_SGHC_232": ["ORDER21_RULE_7_LIP_COSTS"],
}

# Provision-level mapping for broader searches
PROVISION_TO_CASE_MAPPING: Dict[str, List[str]] = {
    "Order 21 r 2(1)": ["2023_SGCA_40", "2025_SGHCR_18_discretion"],
    "Order 21 r 2(2)": ["2025_SGHCR_18_factors", "2023_SGCA_45_conduct"],
    "Order 21 r 2(2)(f)": ["2024_SGHC_146_conduct", "2023_SGCA_45_conduct"],
    "Order 21 r 2(2)(g)": ["2025_SGHCR_18_indemnity"],
    "Order 21 r 2(6)": ["2024_SGHCA_33", "2024_SGHCA_33_discretion"],
    "Order 21 r 3(2)": ["2024_SGHC_146"],
    "Order 21 r 5": ["2023_SGCA_40"],
    "Order 21 r 6": ["2025_SGHCR_33"],
    "Order 21 r 7": ["2022_SGHC_232"],
    "Order 21 r 20": ["2025_SGHCR_18_bill"],
    "Order 21 r 22(3)": ["2025_SGHCR_18_indemnity", "2025_SGHCR_18_purpose"],
}


def get_cases_for_node(node_id: str) -> List[str]:
    """
    Get case law IDs relevant to a logic tree node.

    Args:
        node_id: Logic tree node ID

    Returns:
        List of case law IDs
    """
    return RULE_TO_CASE_MAPPING.get(node_id, [])


def get_rules_for_case(case_id: str) -> List[str]:
    """
    Get logic tree node IDs that a case law illustrates.

    Args:
        case_id: Case law ID

    Returns:
        List of logic tree node IDs
    """
    return CASE_TO_RULE_MAPPING.get(case_id, [])


def get_cases_for_provision(provision: str) -> List[str]:
    """
    Get case law IDs for an Order 21 provision.

    Args:
        provision: Provision reference (e.g., "Order 21 r 2(1)")

    Returns:
        List of case law IDs
    """
    return PROVISION_TO_CASE_MAPPING.get(provision, [])


def get_all_mapped_nodes() -> List[str]:
    """Return all logic tree node IDs that have case law mappings"""
    return list(RULE_TO_CASE_MAPPING.keys())


def get_all_mapped_cases() -> List[str]:
    """Return all case law IDs that are mapped to nodes"""
    all_cases = set()
    for cases in RULE_TO_CASE_MAPPING.values():
        all_cases.update(cases)
    return list(all_cases)


def get_mapping_statistics() -> Dict[str, int]:
    """Return statistics about the mappings"""
    return {
        "total_nodes_mapped": len(RULE_TO_CASE_MAPPING),
        "total_cases_used": len(get_all_mapped_cases()),
        "total_provisions_mapped": len(PROVISION_TO_CASE_MAPPING),
        "avg_cases_per_node": sum(len(v) for v in RULE_TO_CASE_MAPPING.values()) / len(RULE_TO_CASE_MAPPING) if RULE_TO_CASE_MAPPING else 0,
    }
