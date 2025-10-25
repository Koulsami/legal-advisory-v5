"""
Tests for Order 21 Logic Tree Data
Legal Advisory System v5.0

Tests for pre-built logic tree nodes.
"""

import pytest
from backend.modules.order_21.tree_data import (
    get_order21_rule_nodes,
    get_appendix1_scenario_nodes,
    get_all_order21_nodes,
)
from backend.interfaces import LogicTreeNode


def test_get_order21_rule_nodes():
    """Test that rule nodes are returned correctly"""
    nodes = get_order21_rule_nodes()

    # Should have 29 rule nodes
    assert len(nodes) == 29

    # All should be LogicTreeNode instances
    for node in nodes:
        assert isinstance(node, LogicTreeNode)

    # All should have ORDER_21 module_id
    for node in nodes:
        assert node.module_id == "ORDER_21"


def test_get_appendix1_scenario_nodes():
    """Test that scenario nodes are returned correctly"""
    nodes = get_appendix1_scenario_nodes()

    # Should have 9 scenario nodes
    assert len(nodes) == 9

    # All should be LogicTreeNode instances
    for node in nodes:
        assert isinstance(node, LogicTreeNode)

    # All should have ORDER_21 module_id
    for node in nodes:
        assert node.module_id == "ORDER_21"


def test_get_all_order21_nodes():
    """Test that all nodes are returned correctly"""
    nodes = get_all_order21_nodes()

    # Should have 38 total nodes (29 + 9)
    assert len(nodes) == 38

    # Check mix of rules and scenarios
    rule_nodes = [n for n in nodes if n.node_id.startswith("ORDER21_RULE_")]
    scenario_nodes = [n for n in nodes if n.node_id.startswith("APPENDIX1_SCENARIO_")]

    assert len(rule_nodes) == 29
    assert len(scenario_nodes) == 9


def test_rule_node_structure():
    """Test that rule nodes have proper structure"""
    nodes = get_order21_rule_nodes()

    # Check first few detailed nodes
    for node in nodes[:8]:
        # Should have citation
        assert node.citation is not None
        assert "Order 21" in node.citation

        # Should have node_id
        assert node.node_id.startswith("ORDER21_RULE_")

        # Should have at least one dimension populated
        assert (
            len(node.what) > 0
            or len(node.which) > 0
            or len(node.if_then) > 0
            or len(node.modality) > 0
            or len(node.given) > 0
            or len(node.why) > 0
        )


def test_scenario_node_structure():
    """Test that scenario nodes have proper structure"""
    nodes = get_appendix1_scenario_nodes()

    for node in nodes:
        # Should have citation
        assert node.citation is not None
        assert "Appendix 1" in node.citation

        # Should have node_id
        assert node.node_id.startswith("APPENDIX1_SCENARIO_")

        # Should have WHAT dimension (definition/calculation)
        assert len(node.what) > 0

        # Should have IF-THEN dimension (cost ranges)
        assert len(node.if_then) > 0


def test_node_ids_are_unique():
    """Test that all node IDs are unique"""
    nodes = get_all_order21_nodes()
    node_ids = [n.node_id for n in nodes]

    # No duplicates
    assert len(node_ids) == len(set(node_ids))


def test_citations_are_present():
    """Test that all nodes have citations"""
    nodes = get_all_order21_nodes()

    for node in nodes:
        assert node.citation is not None
        assert len(node.citation) > 0


def test_scenario_1_default_judgment_liquidated():
    """Test Scenario 1 node has correct if-then conditions"""
    scenarios = get_appendix1_scenario_nodes()
    scenario_1 = next(n for n in scenarios if n.node_id == "APPENDIX1_SCENARIO_1")

    # Should have multiple if-then conditions for different claim amounts
    assert len(scenario_1.if_then) >= 5

    # Check cost ranges are present
    conditions = [c["condition"] for c in scenario_1.if_then]
    assert any("5,000" in c or "5000" in c for c in conditions)
    assert any("20,000" in c or "20000" in c for c in conditions)


def test_scenario_4_contested_trial():
    """Test Scenario 4 (contested trial) node"""
    scenarios = get_appendix1_scenario_nodes()
    scenario_4 = next(n for n in scenarios if n.node_id == "APPENDIX1_SCENARIO_4")

    assert "1-2 days" in scenario_4.citation
    assert len(scenario_4.if_then) >= 3


def test_rule_1_general_provisions():
    """Test Rule 1 (general provisions) node"""
    rules = get_order21_rule_nodes()
    rule_1 = next(n for n in rules if n.node_id == "ORDER21_RULE_1")

    # Should have WHAT dimension
    assert len(rule_1.what) > 0

    # Should have MODALITY dimension (MAY award costs)
    assert len(rule_1.modality) > 0

    # Should have WHY dimension (policy)
    assert len(rule_1.why) > 0


def test_rule_2_party_and_party():
    """Test Rule 2 (party-and-party costs) node"""
    rules = get_order21_rule_nodes()
    rule_2 = next(n for n in rules if n.node_id == "ORDER21_RULE_2")

    # Should define party-and-party costs
    assert len(rule_2.what) > 0

    # Should have standard vs indemnity basis
    assert len(rule_2.which) > 0

    # Should have SHALL modality
    assert len(rule_2.modality) > 0


def test_rule_3_basis_of_taxation():
    """Test Rule 3 (basis of taxation) node"""
    rules = get_order21_rule_nodes()
    rule_3 = next(n for n in rules if n.node_id == "ORDER21_RULE_3")

    # Should have definitions for standard and indemnity
    assert len(rule_3.what) >= 2

    # Should have if-then conditions
    assert len(rule_3.if_then) >= 2


def test_rules_4_5_6_court_levels():
    """Test Rules 4, 5, 6 (court level quantum) nodes"""
    rules = get_order21_rule_nodes()

    rule_4 = next(n for n in rules if n.node_id == "ORDER21_RULE_4")
    rule_5 = next(n for n in rules if n.node_id == "ORDER21_RULE_5")
    rule_6 = next(n for n in rules if n.node_id == "ORDER21_RULE_6")

    # Rule 4: High Court
    assert "High Court" in rule_4.citation

    # Rule 5: District Court (60-70%)
    assert "District Court" in rule_5.citation
    assert any("60" in str(c) or "70" in str(c) for c in rule_5.what)

    # Rule 6: Magistrates Court (40-50%)
    assert "Magistrates" in rule_6.citation
    assert any("40" in str(c) or "50" in str(c) for c in rule_6.what)


def test_all_nodes_have_module_id():
    """Test that all nodes have correct module_id"""
    nodes = get_all_order21_nodes()

    for node in nodes:
        assert node.module_id == "ORDER_21"


def test_nodes_are_immutable_references():
    """Test that getting nodes multiple times returns consistent data"""
    nodes_1 = get_all_order21_nodes()
    nodes_2 = get_all_order21_nodes()

    # Should have same count
    assert len(nodes_1) == len(nodes_2)

    # Should have same node IDs
    ids_1 = [n.node_id for n in nodes_1]
    ids_2 = [n.node_id for n in nodes_2]
    assert ids_1 == ids_2
