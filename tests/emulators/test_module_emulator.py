"""Tests for Legal Module Emulator"""

import pytest
from backend.emulators.module_emulator import ModuleEmulator


@pytest.mark.asyncio
async def test_module_metadata():
    """Test module metadata"""
    emulator = ModuleEmulator("TestModule")
    
    metadata = emulator.metadata
    
    assert metadata.module_name == "TestModule"
    assert metadata.version == "1.0.0-emulator"
    assert metadata.module_id == "TEST_MODULE"


@pytest.mark.asyncio
async def test_get_tree_nodes():
    """Test logic tree retrieval"""
    emulator = ModuleEmulator()
    
    nodes = emulator.get_tree_nodes()
    
    assert nodes is not None
    assert isinstance(nodes, list)
    assert len(nodes) == 3  # Minimal tree has 3 nodes
    assert nodes[0].node_id == "node_1"
    assert nodes[0].citation == "TEST-1"


@pytest.mark.asyncio
async def test_get_tree_version():
    """Test tree version retrieval"""
    emulator = ModuleEmulator()
    
    version = emulator.get_tree_version()
    assert version == "1.0.0"


@pytest.mark.asyncio
async def test_get_field_requirements():
    """Test getting field requirements"""
    emulator = ModuleEmulator()
    
    requirements = emulator.get_field_requirements()
    assert len(requirements) == 3
    assert requirements[0].field_name == "case_type"
    assert requirements[0].required is True
    assert requirements[1].field_name == "amount"


@pytest.mark.asyncio
async def test_validate_fields():
    """Test field validation"""
    emulator = ModuleEmulator()
    
    # Valid data
    is_valid, errors = emulator.validate_fields({
        "case_type": "civil",
        "amount": 1000,
        "party_count": 2
    })
    assert is_valid is True
    assert len(errors) == 0
    
    # Missing required field
    is_valid, errors = emulator.validate_fields({"amount": 1000})
    assert is_valid is False
    assert len(errors) > 0
    assert "case_type" in errors[0].lower()
    
    # Invalid amount
    is_valid, errors = emulator.validate_fields({
        "case_type": "civil",
        "amount": -100
    })
    assert is_valid is False
    assert len(errors) > 0
    assert "positive" in errors[0].lower()
    
    # Invalid party count
    is_valid, errors = emulator.validate_fields({
        "case_type": "civil",
        "amount": 1000,
        "party_count": 0
    })
    assert is_valid is False
    assert len(errors) > 0


@pytest.mark.asyncio
async def test_calculate():
    """Test calculation"""
    emulator = ModuleEmulator()
    
    filled_fields = {
        "case_type": "civil",
        "amount": 1000,
        "party_count": 3
    }
    
    # Empty matched_nodes list for emulator test
    result = await emulator.calculate([], filled_fields)
    
    assert result["base_amount"] == 1000
    assert result["party_count"] == 3
    assert result["case_type"] == "civil"
    assert "total_cost" in result
    assert result["calculation_method"] == "emulator_mock"


@pytest.mark.asyncio
async def test_query_count():
    """Test query counting"""
    emulator = ModuleEmulator()
    
    assert emulator.get_query_count() == 0
    
    # calculate increments query count
    await emulator.calculate([], {"case_type": "civil", "amount": 1000})
    assert emulator.get_query_count() == 1
    
    await emulator.calculate([], {"case_type": "criminal", "amount": 2000})
    assert emulator.get_query_count() == 2
    
    emulator.reset()
    assert emulator.get_query_count() == 0


@pytest.mark.asyncio
async def test_health_check():
    """Test health check"""
    emulator = ModuleEmulator()
    
    health = await emulator.health_check()
    assert health is True
