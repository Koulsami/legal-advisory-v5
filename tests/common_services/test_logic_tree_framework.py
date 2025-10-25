"""
Comprehensive test suite for LogicTreeFramework.

Tests all functionality including:
- Tree registration and retrieval
- Tree validation (positive and negative cases)
- Completeness calculation
- Node indexing and lookup
- Tree statistics
- Error handling
"""

import pytest

from backend.interfaces.data_structures import LogicTreeNode
from backend.common_services.logic_tree_framework import LogicTreeFramework


# ==== FIXTURES ====

@pytest.fixture
def framework():
    """Create a fresh LogicTreeFramework instance."""
    return LogicTreeFramework()


@pytest.fixture
def valid_node():
    """Create a single valid test node."""
    return LogicTreeNode(
        node_id="TEST-001",
        citation="Test Rule 1",
        module_id="TEST_MODULE",
        what=[{"proposition": "Court must order costs"}],
        which=[{"entity": "Court"}],
        if_then=[{"condition": "party succeeds", "consequence": "gets costs"}],
        modality=[{"action": "order costs", "type": "MUST"}],
        given=[{"premise": "jurisdiction exists"}],
        why=[{"reasoning": "costs follow event"}]
    )


@pytest.fixture
def valid_tree():
    """Create a valid tree with multiple nodes."""
    node1 = LogicTreeNode(
        node_id="O21-R3-1",
        citation="Order 21 Rule 3(1)",
        module_id="ORDER_21",
        what=[{"proposition": "Default costs rule"}],
        which=[{"entity": "All parties"}],
        if_then=[],
        modality=[],
        given=[],
        why=[]
    )
    
    node2 = LogicTreeNode(
        node_id="O21-R3-2",
        citation="Order 21 Rule 3(2)",
        module_id="ORDER_21",
        what=[{"proposition": "Court must order costs"}],
        which=[{"entity": "Court"}],
        if_then=[{"condition": "party succeeds", "consequence": "gets costs"}],
        modality=[{"action": "order", "type": "MUST"}],
        given=[{"premise": "litigation complete"}],
        why=[{"reasoning": "costs follow event"}],
        parent_nodes=["O21-R3-1"]
    )
    
    node3 = LogicTreeNode(
        node_id="O21-R3-3",
        citation="Order 21 Rule 3(3)",
        module_id="ORDER_21",
        what=[{"proposition": "Exceptions may apply"}],
        which=[{"entity": "Court"}],
        if_then=[{"condition": "special circumstances", "consequence": "different order"}],
        modality=[{"action": "vary", "type": "MAY"}],
        given=[],
        why=[{"reasoning": "judicial discretion"}],
        parent_nodes=["O21-R3-2"]
    )
    
    return [node1, node2, node3]


# ==== REGISTRATION TESTS ====

def test_register_valid_tree(framework, valid_tree):
    """Test registering a valid tree."""
    framework.register_module_tree("ORDER_21", valid_tree)
    
    # Verify registration
    assert "ORDER_21" in framework.get_registered_modules()
    assert len(framework.get_module_tree("ORDER_21")) == 3


def test_register_single_node(framework, valid_node):
    """Test registering a tree with single node."""
    framework.register_module_tree("TEST", [valid_node])
    
    assert "TEST" in framework.get_registered_modules()
    assert len(framework.get_module_tree("TEST")) == 1


def test_register_overwrites_existing(framework, valid_tree, valid_node):
    """Test that re-registering a module overwrites the previous tree."""
    # Register first tree
    framework.register_module_tree("TEST", valid_tree)
    assert len(framework.get_module_tree("TEST")) == 3
    
    # Register second tree (should overwrite)
    framework.register_module_tree("TEST", [valid_node])
    assert len(framework.get_module_tree("TEST")) == 1
    assert framework.get_module_tree("TEST")[0].node_id == "TEST-001"


def test_register_empty_module_id_fails(framework, valid_tree):
    """Test that empty module_id is rejected."""
    with pytest.raises(ValueError, match="module_id must be a non-empty string"):
        framework.register_module_tree("", valid_tree)


def test_register_whitespace_module_id_fails(framework, valid_tree):
    """Test that whitespace-only module_id is rejected."""
    with pytest.raises(ValueError, match="module_id must be a non-empty string"):
        framework.register_module_tree("   ", valid_tree)


def test_register_non_list_nodes_fails(framework):
    """Test that non-list nodes parameter is rejected."""
    with pytest.raises(TypeError, match="nodes must be a list"):
        framework.register_module_tree("TEST", "not a list")


def test_register_empty_tree_fails(framework):
    """Test that empty node list is rejected."""
    with pytest.raises(ValueError, match="Cannot register empty tree"):
        framework.register_module_tree("TEST", [])


def test_register_invalid_node_type_fails(framework):
    """Test that non-LogicTreeNode objects are rejected."""
    with pytest.raises(TypeError, match="not a LogicTreeNode object"):
        framework.register_module_tree("TEST", [{"not": "a node"}, "also not"])


# ==== RETRIEVAL TESTS ====

def test_get_registered_tree(framework, valid_tree):
    """Test retrieving a registered tree."""
    framework.register_module_tree("ORDER_21", valid_tree)
    retrieved = framework.get_module_tree("ORDER_21")
    
    assert len(retrieved) == 3
    assert retrieved[0].node_id == "O21-R3-1"
    assert retrieved[1].node_id == "O21-R3-2"
    assert retrieved[2].node_id == "O21-R3-3"


def test_get_unregistered_tree_fails(framework):
    """Test that retrieving unregistered module raises KeyError."""
    with pytest.raises(KeyError, match="not registered"):
        framework.get_module_tree("NONEXISTENT")


def test_get_registered_modules_empty(framework):
    """Test getting modules when none registered."""
    assert framework.get_registered_modules() == []


def test_get_registered_modules_multiple(framework, valid_tree, valid_node):
    """Test getting multiple registered modules."""
    framework.register_module_tree("ORDER_21", valid_tree)
    framework.register_module_tree("ORDER_5", [valid_node])
    
    modules = framework.get_registered_modules()
    assert "ORDER_21" in modules
    assert "ORDER_5" in modules
    assert len(modules) == 2


# ==== NODE LOOKUP TESTS ====

def test_get_node_success(framework, valid_tree):
    """Test successful node lookup."""
    framework.register_module_tree("ORDER_21", valid_tree)
    
    node = framework.get_node("ORDER_21", "O21-R3-2")
    assert node is not None
    assert node.node_id == "O21-R3-2"
    assert node.citation == "Order 21 Rule 3(2)"


def test_get_node_unregistered_module(framework):
    """Test node lookup for unregistered module returns None."""
    node = framework.get_node("NONEXISTENT", "ANY-NODE")
    assert node is None


def test_get_node_nonexistent_node_id(framework, valid_tree):
    """Test node lookup for nonexistent node_id returns None."""
    framework.register_module_tree("ORDER_21", valid_tree)
    node = framework.get_node("ORDER_21", "NONEXISTENT")
    assert node is None


# ==== VALIDATION TESTS - POSITIVE CASES ====

def test_validate_valid_tree(framework, valid_tree):
    """Test validation of a valid tree."""
    is_valid, errors = framework.validate_tree(valid_tree)
    assert is_valid
    assert len(errors) == 0


def test_validate_single_node(framework, valid_node):
    """Test validation of a single node."""
    is_valid, errors = framework.validate_tree([valid_node])
    assert is_valid
    assert len(errors) == 0


# ==== VALIDATION TESTS - NEGATIVE CASES ====

def test_validate_empty_list_fails(framework):
    """Test validation of empty list."""
    is_valid, errors = framework.validate_tree([])
    assert not is_valid
    assert "empty node list" in errors[0]


def test_validate_wrong_type_fails(framework):
    """Test validation of wrong node types."""
    is_valid, errors = framework.validate_tree([{"not": "a node"}])
    assert not is_valid
    assert "not a LogicTreeNode object" in errors[0]


def test_validate_duplicate_ids_fails(framework):
    """Test validation detects duplicate node IDs."""
    node1 = LogicTreeNode(
        node_id="DUPLICATE",
        citation="Rule 1",
        module_id="TEST"
    )
    node2 = LogicTreeNode(
        node_id="DUPLICATE",  # Same ID!
        citation="Rule 2",
        module_id="TEST"
    )
    
    is_valid, errors = framework.validate_tree([node1, node2])
    assert not is_valid
    assert any("Duplicate node IDs" in e for e in errors)


def test_validate_missing_parent_reference_fails(framework):
    """Test validation detects missing parent references."""
    node = LogicTreeNode(
        node_id="TEST-001",
        citation="Test",
        module_id="TEST",
        parent_nodes=["NONEXISTENT-PARENT"]
    )
    
    is_valid, errors = framework.validate_tree([node])
    assert not is_valid
    assert any("non-existent parent" in e for e in errors)


def test_validate_missing_child_reference_fails(framework):
    """Test validation detects missing child references."""
    node = LogicTreeNode(
        node_id="TEST-001",
        citation="Test",
        module_id="TEST",
        child_nodes=["NONEXISTENT-CHILD"]
    )
    
    is_valid, errors = framework.validate_tree([node])
    assert not is_valid
    assert any("non-existent child" in e for e in errors)


def test_validate_missing_related_reference_fails(framework):
    """Test validation detects missing related node references."""
    node = LogicTreeNode(
        node_id="TEST-001",
        citation="Test",
        module_id="TEST",
        related_nodes=["NONEXISTENT-RELATED"]
    )
    
    is_valid, errors = framework.validate_tree([node])
    assert not is_valid
    assert any("non-existent related node" in e for e in errors)


def test_validate_circular_reference_fails(framework):
    """Test validation detects circular references."""
    node1 = LogicTreeNode(
        node_id="A",
        citation="Node A",
        module_id="TEST",
        parent_nodes=["B"]
    )
    node2 = LogicTreeNode(
        node_id="B",
        citation="Node B",
        module_id="TEST",
        parent_nodes=["A"]  # Circular!
    )
    
    is_valid, errors = framework.validate_tree([node1, node2])
    assert not is_valid
    assert any("Circular relationship" in e for e in errors)


# ==== COMPLETENESS CALCULATION TESTS ====

def test_completeness_all_filled(framework):
    """Test completeness when all fields are filled."""
    filled = {"a": "value", "b": "value", "c": "value"}
    required = ["a", "b", "c"]
    
    completeness = framework.calculate_completeness(filled, required)
    assert completeness == 1.0


def test_completeness_none_filled(framework):
    """Test completeness when no fields are filled."""
    filled = {}
    required = ["a", "b", "c"]
    
    completeness = framework.calculate_completeness(filled, required)
    assert completeness == 0.0


def test_completeness_partial_filled(framework):
    """Test completeness with partially filled fields."""
    filled = {"a": "value", "b": "value"}
    required = ["a", "b", "c"]
    
    completeness = framework.calculate_completeness(filled, required)
    assert completeness == 2/3


def test_completeness_no_required_fields(framework):
    """Test completeness when no fields are required."""
    filled = {"a": "value"}
    required = []
    
    completeness = framework.calculate_completeness(filled, required)
    assert completeness == 1.0


def test_completeness_empty_string_not_counted(framework):
    """Test that empty strings are not counted as filled."""
    filled = {"a": "", "b": "value"}
    required = ["a", "b", "c"]
    
    completeness = framework.calculate_completeness(filled, required)
    assert completeness == 1/3  # Only "b" counts


def test_completeness_whitespace_string_not_counted(framework):
    """Test that whitespace-only strings are not counted as filled."""
    filled = {"a": "   ", "b": "value"}
    required = ["a", "b", "c"]
    
    completeness = framework.calculate_completeness(filled, required)
    assert completeness == 1/3  # Only "b" counts


def test_completeness_none_value_not_counted(framework):
    """Test that None values are not counted as filled."""
    filled = {"a": None, "b": "value"}
    required = ["a", "b", "c"]
    
    completeness = framework.calculate_completeness(filled, required)
    assert completeness == 1/3  # Only "b" counts


def test_completeness_empty_list_not_counted(framework):
    """Test that empty lists are not counted as filled."""
    filled = {"a": [], "b": ["item"]}
    required = ["a", "b", "c"]
    
    completeness = framework.calculate_completeness(filled, required)
    assert completeness == 1/3  # Only "b" counts


def test_completeness_empty_dict_not_counted(framework):
    """Test that empty dicts are not counted as filled."""
    filled = {"a": {}, "b": {"key": "value"}}
    required = ["a", "b", "c"]
    
    completeness = framework.calculate_completeness(filled, required)
    assert completeness == 1/3  # Only "b" counts


def test_completeness_bool_false_counted(framework):
    """Test that boolean False is counted as filled."""
    filled = {"a": False, "b": True}
    required = ["a", "b", "c"]
    
    completeness = framework.calculate_completeness(filled, required)
    assert completeness == 2/3  # Both "a" and "b" count


def test_completeness_zero_counted(framework):
    """Test that integer 0 is counted as filled."""
    filled = {"a": 0, "b": 10}
    required = ["a", "b", "c"]
    
    completeness = framework.calculate_completeness(filled, required)
    assert completeness == 2/3  # Both "a" and "b" count


# ==== TREE STATS TESTS ====

def test_get_tree_stats(framework, valid_tree):
    """Test getting tree statistics."""
    framework.register_module_tree("ORDER_21", valid_tree)
    stats = framework.get_tree_stats("ORDER_21")
    
    assert stats['node_count'] == 3
    assert 'avg_children' in stats
    assert 'max_depth' in stats
    assert 'dimension_usage' in stats


def test_get_tree_stats_dimension_usage(framework, valid_tree):
    """Test dimension usage statistics."""
    framework.register_module_tree("ORDER_21", valid_tree)
    stats = framework.get_tree_stats("ORDER_21")
    
    usage = stats['dimension_usage']
    assert usage['what'] == 3  # All 3 nodes have what
    assert usage['which'] == 3  # All 3 nodes have which
    assert usage['if_then'] == 2  # 2 nodes have if_then
    assert usage['modality'] == 2  # 2 nodes have modality
    assert usage['given'] == 1  # 1 node has given
    assert usage['why'] == 2  # 2 nodes have why


def test_get_tree_stats_unregistered_fails(framework):
    """Test getting stats for unregistered module fails."""
    with pytest.raises(KeyError, match="not registered"):
        framework.get_tree_stats("NONEXISTENT")


# ==== INTEGRATION TESTS ====

def test_full_workflow(framework, valid_tree):
    """Test complete workflow: register, validate, retrieve, lookup, stats."""
    # 1. Register tree
    framework.register_module_tree("ORDER_21", valid_tree)
    
    # 2. Verify registration
    assert "ORDER_21" in framework.get_registered_modules()
    
    # 3. Retrieve tree
    retrieved = framework.get_module_tree("ORDER_21")
    assert len(retrieved) == 3
    
    # 4. Lookup specific node
    node = framework.get_node("ORDER_21", "O21-R3-2")
    assert node is not None
    assert node.citation == "Order 21 Rule 3(2)"
    
    # 5. Calculate completeness
    filled = {"party": "plaintiff", "outcome": "success"}
    required = ["party", "outcome", "amount"]
    completeness = framework.calculate_completeness(filled, required)
    assert completeness == 2/3
    
    # 6. Get stats
    stats = framework.get_tree_stats("ORDER_21")
    assert stats['node_count'] == 3


def test_multiple_modules_independent(framework, valid_tree, valid_node):
    """Test that multiple modules are independently managed."""
    # Register two different modules
    framework.register_module_tree("ORDER_21", valid_tree)
    framework.register_module_tree("ORDER_5", [valid_node])
    
    # Verify independence
    tree21 = framework.get_module_tree("ORDER_21")
    tree5 = framework.get_module_tree("ORDER_5")
    
    assert len(tree21) == 3
    assert len(tree5) == 1
    assert tree21[0].module_id == "ORDER_21"
    assert tree5[0].module_id == "TEST_MODULE"
    
    # Verify node lookup is module-specific
    node21 = framework.get_node("ORDER_21", "O21-R3-1")
    node5 = framework.get_node("ORDER_5", "TEST-001")
    
    assert node21 is not None
    assert node5 is not None
    assert framework.get_node("ORDER_21", "TEST-001") is None
    assert framework.get_node("ORDER_5", "O21-R3-1") is None
