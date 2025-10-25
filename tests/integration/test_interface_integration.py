"""
Test Interface Integration
"""

import pytest
from tests.mocks.mock_legal_module import MockLegalModule
from backend.interfaces import LogicTreeNode


@pytest.mark.asyncio
async def test_mock_module_full_flow():
    """Test complete flow with mock module"""
    module = MockLegalModule()
    
    # Get metadata
    metadata = module.metadata
    assert metadata.module_id == "MOCK_MODULE"
    
    # Get tree
    tree = module.get_tree_nodes()
    assert len(tree) == 2
    assert all(isinstance(n, LogicTreeNode) for n in tree)
    
    # Get requirements
    requirements = module.get_field_requirements()
    assert len(requirements) > 0
    
    # Validate fields
    is_valid, errors = module.validate_fields({"test_field": "value"})
    assert is_valid
    assert len(errors) == 0
    
    # Check completeness
    completeness = module.check_completeness({"test_field": "value"})
    assert completeness == 1.0
    
    # Calculate
    result = await module.calculate([], {"test_field": "value"})
    assert result["result"] == "mock_calculation"
    
    # Get arguments
    arguments = await module.get_arguments(result, {})
    assert "arguments" in arguments
    
    # Get recommendations
    recommendations = await module.get_recommendations(result, {})
    assert len(recommendations) > 0


def test_tree_node_relationships():
    """Test tree node parent/child relationships"""
    parent = LogicTreeNode(
        node_id="parent",
        citation="Parent Rule",
        module_id="TEST",
        child_nodes=["child1", "child2"]
    )
    
    child = LogicTreeNode(
        node_id="child1",
        citation="Child Rule",
        module_id="TEST",
        parent_nodes=["parent"]
    )
    
    assert "child1" in parent.child_nodes
    assert "parent" in child.parent_nodes
