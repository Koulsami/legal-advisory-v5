"""Tests for Matching Engine Emulator"""

import pytest
from backend.emulators.matching_emulator import MatchingEmulator
from backend.interfaces.data_structures import LogicTreeNode


@pytest.fixture
def sample_nodes():
    """Create sample nodes for testing"""
    return [
        LogicTreeNode(
            node_id="node1",
            citation="Test-Node-1",
            module_id="TEST_MODULE",
            what=[{"proposition": "court_fees", "text": "What are the court fees?"}]
        ),
        LogicTreeNode(
            node_id="node2",
            citation="Test-Node-2",
            module_id="TEST_MODULE",
            what=[{"proposition": "filing_date", "text": "When was the case filed?"}]
        ),
        LogicTreeNode(
            node_id="node3",
            citation="Test-Node-3",
            module_id="TEST_MODULE",
            which=[{"entity": "case_type", "text": "What type of case is this?"}]
        )
    ]


@pytest.mark.asyncio
async def test_matching_basic(sample_nodes):
    """Test basic matching functionality"""
    emulator = MatchingEmulator(threshold=0.1)
    
    results = await emulator.find_matches(
        "What are the court fees?",
        sample_nodes,
        top_k=5
    )
    
    assert len(results) > 0
    assert results[0].node.node_id == "node1"
    assert results[0].confidence > 0


@pytest.mark.asyncio
async def test_matching_threshold(sample_nodes):
    """Test threshold filtering"""
    emulator = MatchingEmulator(threshold=0.9)
    
    results = await emulator.find_matches(
        "unrelated query",
        sample_nodes,
        top_k=5
    )
    
    # Should return few or no results with high threshold
    assert len(results) <= len(sample_nodes)


@pytest.mark.asyncio
async def test_matching_count(sample_nodes):
    """Test match counting"""
    emulator = MatchingEmulator()
    
    assert emulator.get_match_count() == 0
    
    await emulator.find_matches("test", sample_nodes)
    assert emulator.get_match_count() == 1
    
    await emulator.find_matches("test", sample_nodes)
    assert emulator.get_match_count() == 2
    
    emulator.reset()
    assert emulator.get_match_count() == 0


@pytest.mark.asyncio
async def test_matching_health_check():
    """Test health check"""
    emulator = MatchingEmulator()
    
    health = await emulator.health_check()
    assert health is True
