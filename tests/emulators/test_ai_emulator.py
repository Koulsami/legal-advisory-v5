"""Tests for AI Emulator"""

import pytest
from backend.emulators.ai_emulator import AIEmulator, AIEmulatorConfig
from backend.interfaces.data_structures import AIRequest, AIServiceType


@pytest.mark.asyncio
async def test_ai_emulator_basic():
    """Test basic AI emulator functionality"""
    emulator = AIEmulator()
    
    request = AIRequest(
        prompt="What is the legal analysis?",
        service_type=AIServiceType.ANALYSIS,
        max_tokens=100,
        temperature=0.7
    )
    
    response = await emulator.generate(request)
    
    assert response is not None
    assert response.content is not None
    assert response.service_type == AIServiceType.ANALYSIS
    assert "legal" in response.content.lower()


@pytest.mark.asyncio
async def test_ai_emulator_deterministic():
    """Test that emulator gives deterministic responses"""
    emulator = AIEmulator(AIEmulatorConfig(deterministic=True))
    
    request = AIRequest(
        prompt="What is the legal analysis?",
        service_type=AIServiceType.ANALYSIS,
        max_tokens=100
    )
    
    response1 = await emulator.generate(request)
    response2 = await emulator.generate(request)
    
    assert response1.content == response2.content


@pytest.mark.asyncio
async def test_ai_emulator_call_count():
    """Test call counting"""
    emulator = AIEmulator()
    
    assert emulator.get_call_count() == 0
    
    request = AIRequest(
        prompt="Test",
        service_type=AIServiceType.CONVERSATION,
        max_tokens=100
    )
    await emulator.generate(request)
    
    assert emulator.get_call_count() == 1
    
    await emulator.generate(request)
    assert emulator.get_call_count() == 2
    
    emulator.reset()
    assert emulator.get_call_count() == 0


@pytest.mark.asyncio
async def test_ai_emulator_health_check():
    """Test health check"""
    emulator = AIEmulator()
    
    health = await emulator.health_check()
    assert health is True
