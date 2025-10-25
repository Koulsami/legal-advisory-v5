"""
Interface Compliance Tests - Correct Version
Verify that all mock implementations properly implement their actual interfaces
"""

import pytest

from backend.emulators import (
    MockAIService,
    MockAnalysisEngine,
    MockCalculator,
    MockLegalModule,
    MockMatchingEngine,
    MockTreeFramework,
    MockValidator,
)
from backend.interfaces.ai_service import IAIService
from backend.interfaces.analysis import IAnalysisEngine
from backend.interfaces.calculator import ICalculator
from backend.interfaces.legal_module import ILegalModule
from backend.interfaces.matching import IMatchingEngine
from backend.interfaces.tree import ITreeFramework
from backend.interfaces.validation import IValidator


def test_mock_legal_module_implements_interface():
    """Test MockLegalModule implements ILegalModule"""
    mock = MockLegalModule()
    assert isinstance(mock, ILegalModule)

    # Property
    assert hasattr(mock, "metadata")
    # Methods from actual interface
    assert hasattr(mock, "get_tree_nodes")
    assert hasattr(mock, "get_tree_version")
    assert hasattr(mock, "get_field_requirements")
    assert hasattr(mock, "get_question_templates")
    assert hasattr(mock, "validate_fields")
    assert hasattr(mock, "check_completeness")
    assert hasattr(mock, "calculate")
    assert hasattr(mock, "get_arguments")
    assert hasattr(mock, "get_recommendations")
    assert hasattr(mock, "health_check")


def test_mock_ai_service_implements_interface():
    """Test MockAIService implements IAIService"""
    mock = MockAIService()
    assert isinstance(mock, IAIService)

    # Properties
    assert hasattr(mock, "provider")
    assert hasattr(mock, "model_name")
    # Methods from actual interface
    assert hasattr(mock, "generate")
    assert hasattr(mock, "validate_response")
    assert hasattr(mock, "health_check")


def test_mock_matching_engine_implements_interface():
    """Test MockMatchingEngine implements IMatchingEngine"""
    mock = MockMatchingEngine()
    assert isinstance(mock, IMatchingEngine)

    # Methods from actual interface
    assert hasattr(mock, "match")
    assert hasattr(mock, "health_check")


def test_mock_validator_implements_interface():
    """Test MockValidator implements IValidator"""
    mock = MockValidator()
    assert isinstance(mock, IValidator)

    # Methods from actual interface
    assert hasattr(mock, "validate")
    assert hasattr(mock, "validate_protected_fields")
    assert hasattr(mock, "validate_citations")
    assert hasattr(mock, "validate_legal_terminology")
    assert hasattr(mock, "health_check")


def test_mock_tree_framework_implements_interface():
    """Test MockTreeFramework implements ITreeFramework"""
    mock = MockTreeFramework()
    assert isinstance(mock, ITreeFramework)

    # Methods from actual interface
    assert hasattr(mock, "build_tree")
    assert hasattr(mock, "query_tree")
    assert hasattr(mock, "health_check")


def test_mock_analysis_engine_implements_interface():
    """Test MockAnalysisEngine implements IAnalysisEngine"""
    mock = MockAnalysisEngine()
    assert isinstance(mock, IAnalysisEngine)

    # Methods from actual interface
    assert hasattr(mock, "analyze")
    assert hasattr(mock, "health_check")


def test_mock_calculator_implements_interface():
    """Test MockCalculator implements ICalculator"""
    mock = MockCalculator()
    assert isinstance(mock, ICalculator)

    # Methods from actual interface
    assert hasattr(mock, "calculate")
    assert hasattr(mock, "health_check")


@pytest.mark.asyncio
async def test_all_mocks_have_working_health_check():
    """Test all mocks have functional health_check"""
    mocks = [
        MockLegalModule(),
        MockAIService(),
        MockMatchingEngine(),
        MockValidator(),
        MockTreeFramework(),
        MockAnalysisEngine(),
        MockCalculator(),
    ]

    for mock in mocks:
        health = await mock.health_check()
        assert isinstance(health, bool)
        assert health is True


def test_interfaces_are_abstract():
    """Test that interfaces cannot be instantiated"""
    with pytest.raises(TypeError):
        ILegalModule()
    with pytest.raises(TypeError):
        IAIService()
    with pytest.raises(TypeError):
        IMatchingEngine()
    with pytest.raises(TypeError):
        IValidator()
    with pytest.raises(TypeError):
        ITreeFramework()
    with pytest.raises(TypeError):
        IAnalysisEngine()
    with pytest.raises(TypeError):
        ICalculator()


@pytest.mark.asyncio
async def test_mocks_can_be_used_polymorphically():
    """Test mocks can be used through interface references"""
    # This tests that mocks properly implement the interface contract
    legal_module: ILegalModule = MockLegalModule()
    ai_service: IAIService = MockAIService()
    matching_engine: IMatchingEngine = MockMatchingEngine()
    validator: IValidator = MockValidator()
    tree_framework: ITreeFramework = MockTreeFramework()
    analysis_engine: IAnalysisEngine = MockAnalysisEngine()
    calculator: ICalculator = MockCalculator()

    # Verify they work
    assert legal_module.metadata.module_id == "MOCK_MODULE"
    assert len(legal_module.get_tree_nodes()) > 0
    assert await legal_module.health_check()

    assert ai_service.provider.name == "ANTHROPIC_CLAUDE"
    assert await ai_service.health_check()

    assert await matching_engine.health_check()
    assert await validator.health_check()
    assert await tree_framework.health_check()
    assert await analysis_engine.health_check()
    assert await calculator.health_check()


print("✅ All interface compliance tests defined correctly")
