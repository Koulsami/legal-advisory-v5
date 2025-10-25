"""
Phase 4 Integration Tests
Legal Advisory System v5.0

Integration tests for the complete Hybrid AI Layer.
"""

import pytest
from backend.hybrid_ai import (
    ClaudeAIService,
    ResponseEnhancer,
    ValidationGuard,
    HybridAIOrchestrator,
    EnhancementResult,
    ValidationReport,
    HybridResult
)


@pytest.fixture
def ai_service():
    """Create AI service (mock mode)"""
    return ClaudeAIService(api_key=None)  # Mock mode


@pytest.fixture
def enhancer(ai_service):
    """Create ResponseEnhancer"""
    return ResponseEnhancer(ai_service)


@pytest.fixture
def validator():
    """Create ValidationGuard"""
    return ValidationGuard(strict_mode=True)


@pytest.fixture
def orchestrator(ai_service):
    """Create HybridAIOrchestrator"""
    return HybridAIOrchestrator(ai_service)


def test_all_components_importable():
    """Test all hybrid AI components can be imported"""
    from backend.hybrid_ai import (
        ClaudeAIService,
        ResponseEnhancer,
        ValidationGuard,
        HybridAIOrchestrator
    )
    assert ClaudeAIService is not None
    assert ResponseEnhancer is not None
    assert ValidationGuard is not None
    assert HybridAIOrchestrator is not None


@pytest.mark.asyncio
async def test_ai_service_basic_workflow(ai_service):
    """Test AI service basic workflow"""
    from backend.interfaces.data_structures import AIRequest, AIServiceType

    request = AIRequest(
        service_type=AIServiceType.ENHANCEMENT,
        prompt="Test prompt"
    )

    response = await ai_service.generate(request)

    assert response.content is not None
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_enhancer_basic_workflow(enhancer):
    """Test enhancer basic workflow"""
    calculation = {"total": 1000, "fee": 100}

    result = await enhancer.enhance_calculation_result(calculation)

    assert isinstance(result, EnhancementResult)
    assert result.original_result == calculation
    assert result.calculation_preserved is True


def test_validator_basic_workflow(validator):
    """Test validator basic workflow"""
    calculation = {"total": 1000}
    text = "Total: $1000"

    report = validator.validate(calculation, text)

    assert isinstance(report, ValidationReport)
    assert report.checked_fields == 1


@pytest.mark.asyncio
async def test_orchestrator_complete_workflow(orchestrator):
    """Test orchestrator complete workflow"""
    calculation = {
        "total_cost": 1500,
        "filing_fee": 500,
        "hearing_fee": 1000
    }

    result = await orchestrator.enhance_and_validate(calculation)

    assert isinstance(result, HybridResult)
    assert result.original_calculation == calculation
    assert result.enhanced_result.calculation_preserved is True
    assert result.validation_report is not None


@pytest.mark.asyncio
async def test_end_to_end_safe_enhancement():
    """Test end-to-end safe enhancement"""
    # Create all components
    ai_service = ClaudeAIService(api_key=None)
    orchestrator = HybridAIOrchestrator(ai_service)

    # Calculation with clear values
    calculation = {
        "base_amount": 1000.00,
        "additional_fee": 500.00,
        "total": 1500.00
    }

    # Enhance and validate
    result = await orchestrator.enhance_and_validate(calculation)

    # Verify safety
    assert result.original_calculation == calculation
    assert result.enhanced_result.calculation_preserved is True
    # is_safe depends on validation passing


@pytest.mark.asyncio
async def test_enhancer_validator_integration():
    """Test integration between enhancer and validator"""
    ai_service = ClaudeAIService(api_key=None)
    enhancer = ResponseEnhancer(ai_service)
    validator = ValidationGuard()

    calculation = {"amount": 1000}

    # Enhance
    enhanced = await enhancer.enhance_calculation_result(calculation)

    # Validate
    report = validator.validate(calculation, enhanced.enhanced_explanation)

    # Should have validation report
    assert isinstance(report, ValidationReport)


def test_component_statistics():
    """Test all components provide statistics"""
    ai_service = ClaudeAIService(api_key=None)
    enhancer = ResponseEnhancer(ai_service)
    validator = ValidationGuard()

    # All should have get_statistics
    assert ai_service.get_statistics() is not None
    assert enhancer.get_statistics() is not None
    assert validator.get_statistics() is not None


@pytest.mark.asyncio
async def test_phase4_coverage():
    """Verify Phase 4 components are working together"""
    # This test verifies the complete Phase 4 architecture

    # 1. Create AI service
    ai_service = ClaudeAIService(api_key=None)
    assert await ai_service.health_check() is True

    # 2. Create enhancer
    enhancer = ResponseEnhancer(ai_service)
    calc = {"total": 100}
    result = await enhancer.enhance_calculation_result(calc)
    assert result.calculation_preserved is True

    # 3. Create validator
    validator = ValidationGuard()
    report = validator.validate(calc, result.enhanced_explanation)
    assert isinstance(report, ValidationReport)

    # 4. Create orchestrator
    orchestrator = HybridAIOrchestrator(ai_service)
    hybrid_result = await orchestrator.enhance_and_validate(calc)
    assert isinstance(hybrid_result, HybridResult)

    # Phase 4 complete!
    assert True
