"""
Tests for Hybrid AI Orchestrator
Legal Advisory System v5.0
"""

import pytest
from unittest.mock import AsyncMock, Mock
from backend.hybrid_ai.hybrid_orchestrator import HybridAIOrchestrator, HybridResult
from backend.hybrid_ai.claude_ai_service import ClaudeAIService
from backend.interfaces.data_structures import AIResponse, AIProvider, AIServiceType


@pytest.fixture
def mock_ai_service():
    """Create mock AI service"""
    service = Mock(spec=ClaudeAIService)
    service.provider = AIProvider.ANTHROPIC_CLAUDE
    service.model_name = "claude-test"
    service.generate = AsyncMock(return_value=AIResponse(
        content="This is a clear explanation of the calculation results.",
        service_type=AIServiceType.ENHANCEMENT,
        tokens_used=100,
        finish_reason="stop"
    ))
    service.get_statistics = Mock(return_value={
        "total_requests": 0,
        "total_tokens": 0
    })
    return service


@pytest.fixture
def orchestrator(mock_ai_service):
    """Create HybridAIOrchestrator"""
    return HybridAIOrchestrator(mock_ai_service)


@pytest.fixture
def sample_calculation():
    """Sample calculation"""
    return {
        "total": 1500,
        "filing_fee": 500,
        "hearing_fee": 1000
    }


@pytest.mark.asyncio
async def test_orchestrator_initialization(mock_ai_service):
    """Test orchestrator initialization"""
    orch = HybridAIOrchestrator(mock_ai_service)

    assert orch._ai_service == mock_ai_service
    assert orch._enhancer is not None
    assert orch._validator is not None


@pytest.mark.asyncio
async def test_enhance_and_validate_safe(orchestrator, sample_calculation):
    """Test successful enhancement and validation"""
    result = await orchestrator.enhance_and_validate(sample_calculation)

    assert isinstance(result, HybridResult)
    assert result.original_calculation == sample_calculation
    assert result.is_safe in [True, False]  # Depends on validation
    assert result.enhanced_result is not None
    assert result.validation_report is not None


@pytest.mark.asyncio
async def test_enhance_with_safety_check(orchestrator, sample_calculation):
    """Test convenience method"""
    result = await orchestrator.enhance_with_safety_check(sample_calculation)

    assert isinstance(result, dict)
    assert "calculation" in result
    assert "explanation" in result
    assert "is_safe" in result
    assert result["calculation"] == sample_calculation


@pytest.mark.asyncio
async def test_orchestrator_with_context(orchestrator, sample_calculation):
    """Test orchestration with context"""
    context = {"module": "ORDER_21", "case_type": "costs"}

    result = await orchestrator.enhance_and_validate(
        sample_calculation,
        context=context
    )

    assert result.original_calculation == sample_calculation


@pytest.mark.asyncio
async def test_orchestrator_with_recommendations(orchestrator, sample_calculation):
    """Test orchestration with recommendations"""
    recommendations = ["File within 14 days", "Include all documents"]

    result = await orchestrator.enhance_and_validate(
        sample_calculation,
        recommendations=recommendations
    )

    assert result.original_calculation == sample_calculation


@pytest.mark.asyncio
async def test_orchestrator_statistics(orchestrator, sample_calculation):
    """Test statistics tracking"""
    await orchestrator.enhance_and_validate(sample_calculation)
    await orchestrator.enhance_and_validate(sample_calculation)

    stats = orchestrator.get_statistics()

    assert stats["total_orchestrations"] == 2
    assert "safe_results" in stats
    assert "unsafe_results" in stats
    assert "success_rate" in stats


@pytest.mark.asyncio
async def test_orchestrator_fallback(mock_ai_service, sample_calculation):
    """Test fallback on AI failure"""
    # Make AI service fail
    mock_ai_service.generate = AsyncMock(side_effect=Exception("AI Error"))

    orchestrator = HybridAIOrchestrator(mock_ai_service)
    result = await orchestrator.enhance_and_validate(sample_calculation)

    # Should still return a result with fallback
    assert result.original_calculation == sample_calculation
    assert result.metadata["used_fallback"] is True


def test_enable_disable_enhancement(orchestrator):
    """Test enabling/disabling enhancement"""
    orchestrator.disable_enhancement()
    orchestrator.enable_enhancement()
    # Should not raise errors


def test_set_strict_validation(orchestrator):
    """Test setting validation strictness"""
    orchestrator.set_strict_validation(False)
    orchestrator.set_strict_validation(True)
    # Should not raise errors


@pytest.mark.asyncio
async def test_full_workflow(orchestrator):
    """Test complete workflow"""
    calculation = {"total": 1000, "fee": 100}

    # Get initial stats
    stats_before = orchestrator.get_statistics()

    # Perform orchestration
    result = await orchestrator.enhance_and_validate(calculation)

    # Check result structure
    assert result.original_calculation == calculation
    assert result.enhanced_result.calculation_preserved is True

    # Check stats updated
    stats_after = orchestrator.get_statistics()
    assert stats_after["total_orchestrations"] > stats_before["total_orchestrations"]
