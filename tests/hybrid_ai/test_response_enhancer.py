"""
Tests for Response Enhancer
Legal Advisory System v5.0

Comprehensive tests for ResponseEnhancer implementation.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from backend.hybrid_ai.response_enhancer import (
    ResponseEnhancer,
    ResponseEnhancerError,
    EnhancementResult
)
from backend.interfaces.ai_service import IAIService
from backend.interfaces.data_structures import (
    AIRequest,
    AIResponse,
    AIProvider,
    AIServiceType
)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def mock_ai_service():
    """Create mock AI service"""
    service = AsyncMock(spec=IAIService)
    service.provider = AIProvider.ANTHROPIC_CLAUDE
    service.model_name = "claude-test-model"

    # Default successful response
    service.generate = AsyncMock(return_value=AIResponse(
        content="This is an enhanced explanation of the calculation results.",
        service_type=AIServiceType.ENHANCEMENT,
        tokens_used=100,
        finish_reason="stop",
        metadata={"model": "claude-test"}
    ))

    return service


@pytest.fixture
def enhancer(mock_ai_service):
    """Create ResponseEnhancer with mock AI service"""
    return ResponseEnhancer(mock_ai_service)


@pytest.fixture
def sample_calculation():
    """Create sample calculation result"""
    return {
        "total_costs": 1500.00,
        "filing_fee": 500.00,
        "hearing_fee": 1000.00,
        "breakdown": {
            "base_fee": 400.00,
            "additional_fee": 100.00
        }
    }


# ============================================
# INITIALIZATION TESTS
# ============================================

def test_init_with_valid_service(mock_ai_service):
    """Test initialization with valid AI service"""
    enhancer = ResponseEnhancer(mock_ai_service)

    assert enhancer._ai_service == mock_ai_service
    assert enhancer._enable_enhancement is True
    assert enhancer._max_explanation_length == 2000


def test_init_with_custom_config(mock_ai_service):
    """Test initialization with custom configuration"""
    enhancer = ResponseEnhancer(
        mock_ai_service,
        enable_enhancement=False,
        max_explanation_length=1000
    )

    assert enhancer._enable_enhancement is False
    assert enhancer._max_explanation_length == 1000


def test_init_with_invalid_service():
    """Test initialization with invalid AI service raises TypeError"""
    with pytest.raises(TypeError, match="must implement IAIService"):
        ResponseEnhancer("not_a_service")


# ============================================
# CALCULATION ENHANCEMENT TESTS
# ============================================

@pytest.mark.asyncio
async def test_enhance_calculation_basic(enhancer, sample_calculation):
    """Test basic calculation enhancement"""
    result = await enhancer.enhance_calculation_result(sample_calculation)

    assert isinstance(result, EnhancementResult)
    assert result.original_result == sample_calculation
    assert result.calculation_preserved is True
    assert len(result.enhanced_explanation) > 0
    assert result.enhancement_metadata["enhanced"] is True


@pytest.mark.asyncio
async def test_enhance_calculation_with_context(enhancer, sample_calculation):
    """Test calculation enhancement with context"""
    context = {
        "module_id": "ORDER_21",
        "case_type": "costs_assessment",
        "court_level": "High Court"
    }

    result = await enhancer.enhance_calculation_result(
        sample_calculation,
        context=context
    )

    assert result.calculation_preserved is True
    assert result.enhancement_metadata["enhanced"] is True

    # Verify AI service was called with context
    call_args = enhancer._ai_service.generate.call_args
    assert call_args is not None
    request = call_args[0][0]
    assert request.context == context


@pytest.mark.asyncio
async def test_enhance_calculation_with_recommendations(enhancer, sample_calculation):
    """Test calculation enhancement with recommendations"""
    recommendations = [
        "File within 14 days",
        "Include all supporting documents",
        "Pay filing fee promptly"
    ]

    result = await enhancer.enhance_calculation_result(
        sample_calculation,
        recommendations=recommendations
    )

    assert result.calculation_preserved is True

    # Verify recommendations were included in prompt
    call_args = enhancer._ai_service.generate.call_args
    request = call_args[0][0]
    prompt = request.prompt

    for rec in recommendations:
        assert rec in prompt


@pytest.mark.asyncio
async def test_enhance_calculation_disabled(mock_ai_service, sample_calculation):
    """Test enhancement when disabled"""
    enhancer = ResponseEnhancer(mock_ai_service, enable_enhancement=False)

    result = await enhancer.enhance_calculation_result(sample_calculation)

    assert result.original_result == sample_calculation
    assert result.calculation_preserved is True
    assert result.enhancement_metadata["enhanced"] is False
    assert result.enhancement_metadata["reason"] == "disabled"

    # Verify AI service was NOT called
    mock_ai_service.generate.assert_not_called()


@pytest.mark.asyncio
async def test_enhance_calculation_empty_result(enhancer):
    """Test enhancement with empty calculation result"""
    result = await enhancer.enhance_calculation_result({})

    assert result.calculation_preserved is True
    assert result.enhancement_metadata["enhanced"] is False
    assert "Empty calculation result" in result.enhancement_metadata["reason"]


@pytest.mark.asyncio
async def test_enhance_calculation_ai_failure(enhancer, sample_calculation):
    """Test enhancement falls back gracefully on AI failure"""
    # Make AI service raise error
    enhancer._ai_service.generate = AsyncMock(side_effect=Exception("AI Error"))

    result = await enhancer.enhance_calculation_result(sample_calculation)

    # Should fall back to basic explanation
    assert result.original_result == sample_calculation
    assert result.calculation_preserved is True
    assert result.enhancement_metadata["enhanced"] is False
    assert result.enhancement_metadata["fallback"] is True


@pytest.mark.asyncio
async def test_enhance_calculation_preserves_original(enhancer, sample_calculation):
    """Test that enhancement never modifies original calculation"""
    original_copy = sample_calculation.copy()

    result = await enhancer.enhance_calculation_result(sample_calculation)

    # Original calculation should be unchanged
    assert result.original_result == original_copy
    assert sample_calculation == original_copy


# ============================================
# RECOMMENDATIONS ENHANCEMENT TESTS
# ============================================

@pytest.mark.asyncio
async def test_enhance_recommendations_basic(enhancer):
    """Test basic recommendations enhancement"""
    recommendations = [
        "File within 14 days",
        "Include all receipts"
    ]

    result = await enhancer.enhance_recommendations(recommendations)

    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_enhance_recommendations_with_context(enhancer):
    """Test recommendations enhancement with context"""
    recommendations = ["File promptly"]
    context = {"urgency": "high", "deadline": "2025-11-01"}

    result = await enhancer.enhance_recommendations(
        recommendations,
        context=context
    )

    assert isinstance(result, str)

    # Verify context was passed to AI
    call_args = enhancer._ai_service.generate.call_args
    request = call_args[0][0]
    assert request.context == context


@pytest.mark.asyncio
async def test_enhance_recommendations_disabled(mock_ai_service):
    """Test recommendations enhancement when disabled"""
    enhancer = ResponseEnhancer(mock_ai_service, enable_enhancement=False)
    recommendations = ["Rec 1", "Rec 2"]

    result = await enhancer.enhance_recommendations(recommendations)

    # Should just join recommendations
    assert result == "Rec 1\nRec 2"
    mock_ai_service.generate.assert_not_called()


@pytest.mark.asyncio
async def test_enhance_recommendations_empty(enhancer):
    """Test enhancement with empty recommendations"""
    result = await enhancer.enhance_recommendations([])

    assert result == ""


@pytest.mark.asyncio
async def test_enhance_recommendations_ai_failure(enhancer):
    """Test recommendations falls back on AI failure"""
    enhancer._ai_service.generate = AsyncMock(side_effect=Exception("Error"))
    recommendations = ["Rec 1", "Rec 2"]

    result = await enhancer.enhance_recommendations(recommendations)

    # Should fall back to simple join
    assert result == "Rec 1\nRec 2"


# ============================================
# ERROR MESSAGE ENHANCEMENT TESTS
# ============================================

@pytest.mark.asyncio
async def test_enhance_validation_error_basic(enhancer):
    """Test basic validation error enhancement"""
    error_msg = "Invalid date format"
    field_name = "filing_date"

    result = await enhancer.enhance_validation_error(error_msg, field_name)

    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_enhance_validation_error_with_context(enhancer):
    """Test error enhancement with context"""
    error_msg = "Value out of range"
    field_name = "amount"
    context = {"min": 0, "max": 1000000, "provided": -500}

    result = await enhancer.enhance_validation_error(
        error_msg,
        field_name,
        context=context
    )

    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_enhance_validation_error_disabled(mock_ai_service):
    """Test error enhancement when disabled"""
    enhancer = ResponseEnhancer(mock_ai_service, enable_enhancement=False)

    error_msg = "Test error"
    result = await enhancer.enhance_validation_error(error_msg, "field")

    assert result == error_msg
    mock_ai_service.generate.assert_not_called()


@pytest.mark.asyncio
async def test_enhance_validation_error_ai_failure(enhancer):
    """Test error enhancement falls back on AI failure"""
    enhancer._ai_service.generate = AsyncMock(side_effect=Exception("Error"))

    error_msg = "Original error"
    result = await enhancer.enhance_validation_error(error_msg, "field")

    # Should return original error
    assert result == error_msg


# ============================================
# VALIDATION TESTS
# ============================================

@pytest.mark.asyncio
async def test_validate_enhancement_valid(enhancer, sample_calculation):
    """Test validation passes for valid enhancement"""
    valid_text = "This is a valid enhancement explaining the calculation results in detail."

    is_valid = await enhancer._validate_enhancement(sample_calculation, valid_text)

    assert is_valid is True


@pytest.mark.asyncio
async def test_validate_enhancement_too_short(enhancer, sample_calculation):
    """Test validation fails for too-short enhancement"""
    short_text = "Too short"

    is_valid = await enhancer._validate_enhancement(sample_calculation, short_text)

    assert is_valid is False


@pytest.mark.asyncio
async def test_validate_enhancement_empty(enhancer, sample_calculation):
    """Test validation fails for empty enhancement"""
    is_valid = await enhancer._validate_enhancement(sample_calculation, "")

    assert is_valid is False


@pytest.mark.asyncio
async def test_validate_enhancement_hallucination_patterns(enhancer, sample_calculation):
    """Test validation detects hallucination patterns"""
    hallucination_texts = [
        "I cannot provide this information as an AI",
        "I don't have access to that data",
        "I apologize, but I cannot calculate",
        "There is a [calculation error] in the results"
    ]

    for text in hallucination_texts:
        is_valid = await enhancer._validate_enhancement(sample_calculation, text)
        assert is_valid is False, f"Should reject: {text}"


# ============================================
# PROMPT CONSTRUCTION TESTS
# ============================================

def test_construct_enhancement_prompt(enhancer, sample_calculation):
    """Test enhancement prompt construction"""
    context = {"module": "ORDER_21"}
    recommendations = ["Rec 1", "Rec 2"]

    prompt = enhancer._construct_enhancement_prompt(
        sample_calculation,
        context,
        recommendations
    )

    assert isinstance(prompt, str)
    assert "Calculation Results:" in prompt
    assert "Context:" in prompt
    assert "Recommendations:" in prompt
    assert "total_costs" in prompt
    assert "DO NOT change any numbers" in prompt


def test_construct_recommendations_prompt(enhancer):
    """Test recommendations prompt construction"""
    recommendations = ["File within 14 days"]
    context = {"urgency": "high"}

    prompt = enhancer._construct_recommendations_prompt(recommendations, context)

    assert isinstance(prompt, str)
    assert "File within 14 days" in prompt
    assert "Context:" in prompt


def test_construct_error_enhancement_prompt(enhancer):
    """Test error enhancement prompt construction"""
    error_msg = "Invalid format"
    field_name = "date"
    context = {"expected": "YYYY-MM-DD"}

    prompt = enhancer._construct_error_enhancement_prompt(
        error_msg,
        field_name,
        context
    )

    assert isinstance(prompt, str)
    assert "Invalid format" in prompt
    assert "date" in prompt
    assert "Additional Context:" in prompt


# ============================================
# FALLBACK TESTS
# ============================================

def test_create_fallback_result(enhancer, sample_calculation):
    """Test fallback result creation"""
    result = enhancer._create_fallback_result(
        sample_calculation,
        "Test reason"
    )

    assert isinstance(result, EnhancementResult)
    assert result.original_result == sample_calculation
    assert result.calculation_preserved is True
    assert result.enhancement_metadata["enhanced"] is False
    assert result.enhancement_metadata["fallback"] is True
    assert "Test reason" in result.enhancement_metadata["reason"]


def test_generate_basic_explanation(enhancer, sample_calculation):
    """Test basic explanation generation"""
    explanation = enhancer._generate_basic_explanation(sample_calculation)

    assert isinstance(explanation, str)
    assert "Calculation Results:" in explanation
    assert "Total Costs" in explanation
    assert "1500" in explanation


# ============================================
# STATISTICS TESTS
# ============================================

def test_get_statistics_initial(enhancer):
    """Test initial statistics"""
    stats = enhancer.get_statistics()

    assert stats["enhancement_enabled"] is True
    assert stats["total_enhancements"] == 0
    assert stats["successful_enhancements"] == 0
    assert stats["failed_enhancements"] == 0
    assert stats["success_rate"] == 0.0
    assert stats["ai_service_provider"] == "anthropic_claude"


@pytest.mark.asyncio
async def test_get_statistics_after_enhancements(enhancer, sample_calculation):
    """Test statistics after performing enhancements"""
    # Perform several enhancements
    await enhancer.enhance_calculation_result(sample_calculation)
    await enhancer.enhance_calculation_result(sample_calculation)

    stats = enhancer.get_statistics()

    assert stats["total_enhancements"] == 2
    assert stats["successful_enhancements"] == 2
    assert stats["success_rate"] == 1.0


@pytest.mark.asyncio
async def test_get_statistics_with_failures(enhancer, sample_calculation):
    """Test statistics with some failures"""
    # One success
    await enhancer.enhance_calculation_result(sample_calculation)

    # One failure
    enhancer._ai_service.generate = AsyncMock(side_effect=Exception("Error"))
    await enhancer.enhance_calculation_result(sample_calculation)

    stats = enhancer.get_statistics()

    assert stats["total_enhancements"] == 2
    assert stats["successful_enhancements"] == 1
    assert stats["failed_enhancements"] == 1
    assert stats["success_rate"] == 0.5


def test_reset_statistics(enhancer):
    """Test statistics reset"""
    # Manually set some stats
    enhancer._enhancement_count = 10
    enhancer._enhancement_failures = 2
    enhancer._fallback_count = 1

    enhancer.reset_statistics()

    stats = enhancer.get_statistics()
    assert stats["total_enhancements"] == 0
    assert stats["failed_enhancements"] == 0
    assert stats["fallback_count"] == 0


# ============================================
# ENABLE/DISABLE TESTS
# ============================================

def test_enable_disable_enhancement(enhancer):
    """Test enabling/disabling enhancement"""
    assert enhancer.is_enhancement_enabled() is True

    enhancer.disable_enhancement()
    assert enhancer.is_enhancement_enabled() is False

    enhancer.enable_enhancement()
    assert enhancer.is_enhancement_enabled() is True


@pytest.mark.asyncio
async def test_enhancement_respects_enable_state(enhancer, sample_calculation):
    """Test that enhancement respects enabled state"""
    # Initially enabled
    result1 = await enhancer.enhance_calculation_result(sample_calculation)
    assert result1.enhancement_metadata["enhanced"] is True

    # Disable
    enhancer.disable_enhancement()
    result2 = await enhancer.enhance_calculation_result(sample_calculation)
    assert result2.enhancement_metadata["enhanced"] is False

    # Re-enable
    enhancer.enable_enhancement()
    result3 = await enhancer.enhance_calculation_result(sample_calculation)
    assert result3.enhancement_metadata["enhanced"] is True


# ============================================
# INTEGRATION TESTS
# ============================================

@pytest.mark.asyncio
async def test_full_enhancement_workflow(enhancer):
    """Test complete enhancement workflow"""
    # 1. Check initial state
    assert enhancer.is_enhancement_enabled() is True

    # 2. Enhance calculation
    calculation = {"total": 1000, "fee": 100}
    calc_result = await enhancer.enhance_calculation_result(calculation)
    assert calc_result.calculation_preserved is True

    # 3. Enhance recommendations
    recs = ["Action 1", "Action 2"]
    recs_result = await enhancer.enhance_recommendations(recs)
    assert len(recs_result) > 0

    # 4. Enhance error
    error_result = await enhancer.enhance_validation_error("Error", "field")
    assert len(error_result) > 0

    # 5. Check statistics
    stats = enhancer.get_statistics()
    assert stats["total_enhancements"] >= 1


@pytest.mark.asyncio
async def test_concurrent_enhancements(enhancer, sample_calculation):
    """Test handling concurrent enhancement requests"""
    import asyncio

    # Make 5 concurrent requests
    tasks = [
        enhancer.enhance_calculation_result(sample_calculation)
        for _ in range(5)
    ]

    results = await asyncio.gather(*tasks)

    assert len(results) == 5
    for result in results:
        assert isinstance(result, EnhancementResult)
        assert result.calculation_preserved is True


# ============================================
# EDGE CASE TESTS
# ============================================

@pytest.mark.asyncio
async def test_enhancement_with_complex_nested_calculation(enhancer):
    """Test enhancement with deeply nested calculation"""
    complex_calc = {
        "total": 5000,
        "level1": {
            "subtotal": 3000,
            "level2": {
                "item_a": 1000,
                "item_b": 2000
            }
        },
        "fees": {
            "filing": 500,
            "hearing": 1500
        }
    }

    result = await enhancer.enhance_calculation_result(complex_calc)

    assert result.calculation_preserved is True
    assert result.original_result == complex_calc


@pytest.mark.asyncio
async def test_enhancement_with_special_characters(enhancer):
    """Test enhancement with special characters in calculation"""
    calc = {
        "amount_$": 1000.50,
        "description": "Fee: $100 (10%)",
        "note": "Currency: S$"
    }

    result = await enhancer.enhance_calculation_result(calc)

    assert result.calculation_preserved is True


@pytest.mark.asyncio
async def test_enhancement_metadata_tracking(enhancer, sample_calculation):
    """Test that enhancement metadata is properly tracked"""
    result = await enhancer.enhance_calculation_result(sample_calculation)

    metadata = result.enhancement_metadata

    assert "enhanced" in metadata
    assert "tokens_used" in metadata
    assert "model" in metadata
    assert "provider" in metadata
    assert metadata["model"] == "claude-test-model"
    assert metadata["provider"] == "anthropic_claude"
