"""
Test All Interfaces
"""

import pytest
from backend.interfaces import (
    ILegalModule,
    IAIService,
    IMatchingEngine,
    IValidator,
    ITreeFramework,
    IAnalysisEngine,
    ICalculator,
    LogicTreeNode,
    MatchResult,
    ModuleMetadata,
    ModuleStatus,
    AIProvider,        # ← ADD THIS
    AIServiceType,     # ← ADD THIS
)


def test_imports():
    """Test all interfaces can be imported"""
    assert ILegalModule is not None
    assert IAIService is not None
    assert IMatchingEngine is not None
    assert IValidator is not None
    assert ITreeFramework is not None
    assert IAnalysisEngine is not None
    assert ICalculator is not None


def test_logic_tree_node_creation():
    """Test LogicTreeNode creation"""
    node = LogicTreeNode(
        node_id="test_1",
        citation="Order 21 Rule 1",
        module_id="ORDER_21"
    )
    assert node.node_id == "test_1"
    assert node.citation == "Order 21 Rule 1"
    assert node.confidence == 1.0


def test_logic_tree_node_validation():
    """Test LogicTreeNode validation"""
    with pytest.raises(ValueError):
        LogicTreeNode(
            node_id="",  # Invalid
            citation="Test",
            module_id="TEST"
        )

def test_logic_tree_node_confidence_validation():
    """Test LogicTreeNode confidence must be 0.0-1.0"""
    with pytest.raises(ValueError):
        LogicTreeNode(
            node_id="test",
            citation="Test",
            module_id="TEST",
            confidence=1.5  # Invalid - > 1.0
        )

def test_module_metadata():
    """Test ModuleMetadata creation"""
    metadata = ModuleMetadata(
        module_id="ORDER_21",
        module_name="Order 21",
        version="1.0.0",
        status=ModuleStatus.ACTIVE,
        author="Test",
        description="Test module",
        effective_date="2024-01-01",
        last_updated="2024-10-25"
    )
    assert metadata.module_id == "ORDER_21"
    assert metadata.status == ModuleStatus.ACTIVE


def test_match_result_validation():
    """Test MatchResult validation"""
    node = LogicTreeNode(
        node_id="test_1",
        citation="Test",
        module_id="TEST"
    )
    
    match = MatchResult(
        node_id="test_1",
        node=node,
        match_score=0.85,
        matched_fields={"field1": "value1"},
        missing_fields=["field2"],
        confidence=0.9,
        reasoning="Test match"
    )
    assert match.match_score == 0.85
    assert match.confidence == 0.9

def test_match_result_score_validation():
    """Test MatchResult score must be 0.0-1.0"""
    node = LogicTreeNode(
        node_id="test_1",
        citation="Test",
        module_id="TEST"
    )
    
    with pytest.raises(ValueError):
        MatchResult(
            node_id="test_1",
            node=node,
            match_score=1.5,  # Invalid - > 1.0
            matched_fields={},
            missing_fields=[],
            confidence=0.9,
            reasoning="Test"
        )

def test_interface_cannot_be_instantiated():
    """Test that interfaces cannot be instantiated directly"""
    with pytest.raises(TypeError):
        ILegalModule()
    
    with pytest.raises(TypeError):
        IAIService()

def test_enums():
    """Test enum values"""
    assert ModuleStatus.ACTIVE.value == "active"
    assert AIProvider.ANTHROPIC_CLAUDE.value == "anthropic_claude"
    assert AIServiceType.CONVERSATION.value == "conversation"
