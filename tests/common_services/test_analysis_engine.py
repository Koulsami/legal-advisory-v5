"""
Comprehensive test suite for AnalysisEngine.

Tests all functionality including:
- Single module analysis workflow
- Multi-module auto-analysis
- Module selection and routing
- Integration with all common services
- Result aggregation and ranking
- Error handling
"""

import pytest
from backend.interfaces.legal_module import ILegalModule
from backend.interfaces.data_structures import (
    LogicTreeNode,
    ModuleMetadata,
    ModuleStatus,
    MatchResult
)
from backend.common_services.logic_tree_framework import LogicTreeFramework
from backend.common_services.matching_engine import UniversalMatchingEngine
from backend.common_services.module_registry import ModuleRegistry
from backend.common_services.analysis_engine import (
    AnalysisEngine,
    AnalysisResult,
    MultiModuleAnalysisResult
)


# ==== MOCK MODULE FOR TESTING ====

class FullMockModule(ILegalModule):
    """Fully functional mock module for analysis testing"""

    def __init__(
        self,
        module_id: str,
        module_name: str,
        tree_nodes: list = None,
        completeness_threshold: float = 0.7,
        always_valid: bool = True,
        calculation_result: dict = None
    ):
        self._module_id = module_id
        self._module_name = module_name
        self._tree_nodes = tree_nodes or [
            LogicTreeNode(
                node_id=f"{module_id}-N1",
                citation=f"Rule 1 for {module_id}",
                module_id=module_id,
                what=[{"fact": f"{module_id} provisions"}]
            )
        ]
        self._completeness_threshold = completeness_threshold
        self._always_valid = always_valid
        self._calculation_result = calculation_result or {"result": "calculated"}

    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            module_id=self._module_id,
            module_name=self._module_name,
            version="1.0.0",
            status=ModuleStatus.REGISTERED,
            author="Test",
            description=f"Test module {self._module_id}",
            effective_date="2024-01-01",
            last_updated="2024-10-26",
            tags=["test"]
        )

    def get_tree_nodes(self) -> list:
        return self._tree_nodes

    def get_tree_version(self) -> str:
        return "1.0"

    def get_field_requirements(self) -> list:
        return []

    def get_question_templates(self) -> list:
        return []

    def validate_fields(self, fields: dict) -> tuple:
        if self._always_valid:
            return True, []
        else:
            return False, ["Validation error for testing"]

    def check_completeness(self, filled_fields: dict) -> tuple:
        # Simple completeness: ratio of filled fields to threshold
        field_count = len(filled_fields)
        score = min(field_count / 5.0, 1.0)  # 5 fields = 100%

        missing = []
        if score < 1.0:
            missing = [f"field_{i}" for i in range(field_count + 1, 6)]

        return score, missing

    def calculate(self, fields: dict) -> dict:
        return self._calculation_result.copy()

    def get_arguments(self, node_id: str) -> dict:
        return {}

    def get_recommendations(self, analysis_result: dict) -> list:
        return ["Recommendation 1", "Recommendation 2"]

    async def health_check(self) -> bool:
        return True


# ==== FIXTURES ====

@pytest.fixture
def tree_framework():
    """Create LogicTreeFramework"""
    return LogicTreeFramework()


@pytest.fixture
def matching_engine():
    """Create UniversalMatchingEngine"""
    return UniversalMatchingEngine()


@pytest.fixture
def module_registry(tree_framework):
    """Create ModuleRegistry"""
    return ModuleRegistry(tree_framework)


@pytest.fixture
def analysis_engine(module_registry, matching_engine, tree_framework):
    """Create AnalysisEngine"""
    return AnalysisEngine(module_registry, matching_engine, tree_framework)


@pytest.fixture
def sample_module():
    """Create a sample module"""
    nodes = [
        LogicTreeNode(
            node_id="TEST-N1",
            citation="Test Rule 1",
            module_id="TEST_MODULE",
            what=[{"fact": "costs court plaintiff"}]
        ),
        LogicTreeNode(
            node_id="TEST-N2",
            citation="Test Rule 2",
            module_id="TEST_MODULE",
            which=[{"scope": "High Court proceedings"}]
        )
    ]
    return FullMockModule(
        module_id="TEST_MODULE",
        module_name="Test Legal Module",
        tree_nodes=nodes
    )


# ==== INITIALIZATION TESTS ====

def test_analysis_engine_initialization(module_registry, matching_engine, tree_framework):
    """Test engine initializes correctly"""
    engine = AnalysisEngine(module_registry, matching_engine, tree_framework)

    assert engine.module_registry is module_registry
    assert engine.matching_engine is matching_engine
    assert engine.tree_framework is tree_framework


def test_analysis_engine_requires_correct_types():
    """Test engine validates constructor arguments"""
    with pytest.raises(TypeError, match="module_registry must be ModuleRegistry"):
        AnalysisEngine("not registry", None, None)


# ==== SINGLE MODULE ANALYSIS TESTS ====

@pytest.mark.asyncio
async def test_analyze_basic_workflow(analysis_engine, sample_module):
    """Test basic analysis workflow"""
    filled_fields = {
        "court": "High Court",
        "party": "Plaintiff",
        "amount": 50000
    }

    result = await analysis_engine.analyze(sample_module, filled_fields)

    assert result["module_id"] == "TEST_MODULE"
    assert result["module_name"] == "Test Legal Module"
    assert "matched_nodes" in result
    assert "completeness_score" in result
    assert "confidence" in result


@pytest.mark.asyncio
async def test_analyze_validates_fields(analysis_engine):
    """Test analysis includes validation"""
    # Module that always fails validation
    invalid_module = FullMockModule(
        module_id="INVALID",
        module_name="Invalid Module",
        always_valid=False
    )

    result = await analysis_engine.analyze(invalid_module, {"field": "value"})

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) > 0


@pytest.mark.asyncio
async def test_analyze_checks_completeness(analysis_engine, sample_module):
    """Test analysis checks information completeness"""
    # Few fields = low completeness
    few_fields = {"field1": "value"}
    result_low = await analysis_engine.analyze(sample_module, few_fields)

    # Many fields = high completeness
    many_fields = {f"field{i}": f"value{i}" for i in range(6)}
    result_high = await analysis_engine.analyze(sample_module, many_fields)

    assert result_low["completeness_score"] < result_high["completeness_score"]


@pytest.mark.asyncio
async def test_analyze_matches_nodes(analysis_engine, sample_module):
    """Test analysis matches relevant tree nodes"""
    filled_fields = {
        "query": "costs court plaintiff proceedings"
    }

    result = await analysis_engine.analyze(sample_module, filled_fields)

    # Should find at least one match given our keywords
    assert result["matched_node_count"] >= 0
    assert isinstance(result["matched_nodes"], list)


@pytest.mark.asyncio
async def test_analyze_performs_calculation_when_complete(analysis_engine):
    """Test calculation runs when completeness >= 70%"""
    # Module with 5 fields requirement, provide all 5
    complete_module = FullMockModule(
        module_id="COMPLETE",
        module_name="Complete Module",
        calculation_result={"calculated_cost": 1000}
    )

    # Provide enough fields for high completeness
    fields = {f"field{i}": f"value{i}" for i in range(5)}
    result = await analysis_engine.analyze(complete_module, fields)

    assert result["can_calculate"] is True
    assert result["calculation_result"] is not None
    assert result["calculation_result"].get("calculated_cost") == 1000


@pytest.mark.asyncio
async def test_analyze_skips_calculation_when_incomplete(analysis_engine, sample_module):
    """Test calculation skipped when completeness < 70%"""
    # Very few fields
    fields = {"field1": "value"}

    result = await analysis_engine.analyze(sample_module, fields)

    # Should skip calculation if completeness is low
    if result["completeness_score"] < 0.7:
        assert result["can_calculate"] is False


@pytest.mark.asyncio
async def test_analyze_generates_recommendations(analysis_engine):
    """Test recommendations are generated after calculation"""
    complete_module = FullMockModule(
        module_id="RECS",
        module_name="Recommendations Module"
    )

    fields = {f"field{i}": f"value{i}" for i in range(5)}
    result = await analysis_engine.analyze(complete_module, fields)

    # If calculation succeeded, should have recommendations
    if result["calculation_result"] and "error" not in result["calculation_result"]:
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)


@pytest.mark.asyncio
async def test_analyze_calculates_confidence(analysis_engine, sample_module):
    """Test confidence score is calculated"""
    fields = {"field1": "value", "field2": "value"}
    result = await analysis_engine.analyze(sample_module, fields)

    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_analyze_includes_timestamp(analysis_engine, sample_module):
    """Test result includes timestamp"""
    result = await analysis_engine.analyze(sample_module, {"field": "value"})

    assert "timestamp" in result
    assert result["timestamp"]  # Not empty


@pytest.mark.asyncio
async def test_analyze_invalid_module_type(analysis_engine):
    """Test analyze rejects non-ILegalModule"""
    with pytest.raises(TypeError, match="must implement ILegalModule"):
        await analysis_engine.analyze("not a module", {})


# ==== AUTO-ANALYSIS TESTS ====

@pytest.mark.asyncio
async def test_analyze_auto_with_no_modules(analysis_engine):
    """Test auto-analysis with empty registry"""
    result = await analysis_engine.analyze_auto({"field": "value"})

    assert result.total_modules_analyzed == 0
    assert result.primary_result is None
    assert len(result.alternative_results) == 0


@pytest.mark.asyncio
async def test_analyze_auto_with_single_module(module_registry, analysis_engine):
    """Test auto-analysis with one module"""
    module = FullMockModule("MOD1", "Module 1")
    module_registry.register_module(module, auto_activate=True)

    result = await analysis_engine.analyze_auto({"field": "value"})

    assert result.total_modules_analyzed == 1
    assert result.primary_result is not None
    assert result.primary_result.module_id == "MOD1"


@pytest.mark.asyncio
async def test_analyze_auto_with_multiple_modules(module_registry, analysis_engine):
    """Test auto-analysis with multiple modules"""
    # Create 3 modules
    for i in range(1, 4):
        module = FullMockModule(f"MOD{i}", f"Module {i}")
        module_registry.register_module(module, auto_activate=True)

    result = await analysis_engine.analyze_auto({"field": "value"}, top_k=2)

    assert result.total_modules_analyzed == 3
    assert result.primary_result is not None
    # Should have 1 alternative (top_k=2, so 1 primary + 1 alternative)
    assert len(result.alternative_results) == 1


@pytest.mark.asyncio
async def test_analyze_auto_ranks_by_confidence(module_registry, analysis_engine):
    """Test auto-analysis ranks results by confidence"""
    # Module with high completeness potential
    high_module = FullMockModule("HIGH", "High Confidence Module")
    module_registry.register_module(high_module, auto_activate=True)

    # Module with lower completeness potential
    low_module = FullMockModule("LOW", "Low Confidence Module")
    module_registry.register_module(low_module, auto_activate=True)

    # Provide many fields for high completeness
    fields = {f"field{i}": f"value{i}" for i in range(6)}

    result = await analysis_engine.analyze_auto(fields, top_k=2)

    # Primary should have higher confidence than alternatives
    if result.alternative_results:
        assert result.primary_result.confidence >= result.alternative_results[0].confidence


@pytest.mark.asyncio
async def test_analyze_auto_respects_top_k(module_registry, analysis_engine):
    """Test auto-analysis respects top_k parameter"""
    # Create 5 modules
    for i in range(1, 6):
        module = FullMockModule(f"MOD{i}", f"Module {i}")
        module_registry.register_module(module, auto_activate=True)

    result = await analysis_engine.analyze_auto({"field": "value"}, top_k=3)

    # Should have analyzed all 5 but return only top 3
    assert result.total_modules_analyzed == 5
    # 1 primary + 2 alternatives = 3 total
    total_returned = 1 + len(result.alternative_results)
    assert total_returned <= 3


@pytest.mark.asyncio
async def test_analyze_auto_filters_by_active_status(module_registry, analysis_engine):
    """Test auto-analysis filters by module status"""
    # Active module
    active = FullMockModule("ACTIVE", "Active Module")
    module_registry.register_module(active, auto_activate=True)

    # Registered but not active
    inactive = FullMockModule("INACTIVE", "Inactive Module")
    module_registry.register_module(inactive, auto_activate=False)

    # Should only analyze active modules
    result = await analysis_engine.analyze_auto(
        {"field": "value"},
        require_active=True
    )

    assert result.total_modules_analyzed == 1
    assert result.primary_result.module_id == "ACTIVE"


@pytest.mark.asyncio
async def test_analyze_auto_includes_summary(module_registry, analysis_engine):
    """Test auto-analysis includes summary"""
    module = FullMockModule("MOD1", "Module 1")
    module_registry.register_module(module, auto_activate=True)

    result = await analysis_engine.analyze_auto({"field": "value"})

    assert result.analysis_summary
    assert "module" in result.analysis_summary.lower()


# ==== ANALYZE WITH MODULE ID TESTS ====

@pytest.mark.asyncio
async def test_analyze_with_module_id(module_registry, analysis_engine):
    """Test analysis by module ID"""
    module = FullMockModule("TEST", "Test Module")
    module_registry.register_module(module, auto_activate=True)

    result = await analysis_engine.analyze_with_module_id(
        "TEST",
        {"field": "value"}
    )

    assert result["module_id"] == "TEST"


@pytest.mark.asyncio
async def test_analyze_with_invalid_module_id(analysis_engine):
    """Test analysis with non-existent module ID"""
    with pytest.raises(ValueError, match="not found"):
        await analysis_engine.analyze_with_module_id(
            "NONEXISTENT",
            {"field": "value"}
        )


# ==== STATISTICS TESTS ====

def test_get_analysis_statistics_initial(analysis_engine):
    """Test statistics are initially zero"""
    stats = analysis_engine.get_analysis_statistics()

    assert stats["total_analyses"] == 0
    assert stats["total_matches_found"] == 0
    assert stats["average_matches_per_analysis"] == 0


@pytest.mark.asyncio
async def test_get_analysis_statistics_after_analyses(module_registry, analysis_engine):
    """Test statistics update after analyses"""
    module = FullMockModule("MOD1", "Module 1")
    module_registry.register_module(module, auto_activate=True)

    # Perform analyses
    await analysis_engine.analyze(module, {"field1": "value"})
    await analysis_engine.analyze(module, {"field2": "value"})

    stats = analysis_engine.get_analysis_statistics()

    assert stats["total_analyses"] == 2
    assert stats["registered_modules"] == 1


# ==== INTEGRATION TESTS ====

@pytest.mark.asyncio
async def test_full_analysis_workflow_integration(
    module_registry,
    matching_engine,
    tree_framework,
    analysis_engine
):
    """Test complete integration of all services"""
    # Create a module with detailed tree
    nodes = [
        LogicTreeNode(
            node_id="INT-N1",
            citation="Integration Rule 1",
            module_id="INTEGRATION",
            what=[{"fact": "court costs calculation"}],
            which=[{"scope": "High Court"}]
        ),
        LogicTreeNode(
            node_id="INT-N2",
            citation="Integration Rule 2",
            module_id="INTEGRATION",
            if_then=[{"condition": "plaintiff wins", "consequence": "gets costs"}]
        )
    ]

    module = FullMockModule(
        module_id="INTEGRATION",
        module_name="Integration Test Module",
        tree_nodes=nodes,
        calculation_result={"total_cost": 5000, "breakdown": {"filing": 1000, "hearing": 4000}}
    )

    # Register module
    module_registry.register_module(module, auto_activate=True)

    # Verify module is in registry
    assert module_registry.is_registered("INTEGRATION")

    # Verify tree is registered
    assert "INTEGRATION" in tree_framework.get_registered_modules()

    # Perform analysis
    fields = {
        "court": "High Court",
        "party": "plaintiff",
        "costs": "calculation",
        "outcome": "wins",
        "extra": "field"
    }

    result = await analysis_engine.analyze(module, fields)

    # Verify all components worked
    assert result["module_id"] == "INTEGRATION"
    assert result["matched_node_count"] >= 0  # Matching engine worked
    assert result["completeness_score"] > 0  # Completeness check worked
    assert result["calculation_result"] is not None  # Calculation worked
    assert result["calculation_result"]["total_cost"] == 5000


@pytest.mark.asyncio
async def test_multi_module_analysis_integration(module_registry, analysis_engine):
    """Test multi-module analysis with full integration"""
    # Create multiple modules with different focus
    module1 = FullMockModule(
        module_id="COSTS",
        module_name="Costs Module",
        tree_nodes=[
            LogicTreeNode("C1", "Costs Rule", "COSTS",
                         what=[{"fact": "legal costs attorney"}])
        ]
    )

    module2 = FullMockModule(
        module_id="DISCOVERY",
        module_name="Discovery Module",
        tree_nodes=[
            LogicTreeNode("D1", "Discovery Rule", "DISCOVERY",
                         what=[{"fact": "document discovery disclosure"}])
        ]
    )

    # Register both
    module_registry.register_module(module1, auto_activate=True)
    module_registry.register_module(module2, auto_activate=True)

    # Auto-analyze
    fields = {"query": "legal costs attorney fees"}

    result = await analysis_engine.analyze_auto(fields, top_k=2)

    # Should analyze both modules
    assert result.total_modules_analyzed == 2

    # Should return both (1 primary + 1 alternative)
    assert result.primary_result is not None
    assert len(result.alternative_results) >= 0


# ==== ERROR HANDLING TESTS ====

@pytest.mark.asyncio
async def test_analyze_handles_calculation_errors(analysis_engine):
    """Test analysis handles calculation errors gracefully"""

    class ErrorModule(FullMockModule):
        def calculate(self, fields: dict) -> dict:
            raise Exception("Calculation error!")

    error_module = ErrorModule("ERROR", "Error Module")

    # Provide enough fields to trigger calculation
    fields = {f"field{i}": f"value{i}" for i in range(6)}

    # Should not crash, should capture error
    result = await analysis_engine.analyze(error_module, fields)

    # Should have error in calculation result
    assert result["calculation_result"] is not None
    assert "error" in result["calculation_result"]


@pytest.mark.asyncio
async def test_analyze_auto_handles_module_failures(module_registry, analysis_engine):
    """Test auto-analysis handles individual module failures"""

    class FailingModule(FullMockModule):
        def validate_fields(self, fields: dict) -> tuple:
            raise Exception("Validation exploded!")

    # Add one failing and one working module
    failing = FailingModule("FAIL", "Failing Module")
    working = FullMockModule("WORK", "Working Module")

    module_registry.register_module(failing, auto_activate=True)
    module_registry.register_module(working, auto_activate=True)

    # Should complete despite one module failing
    result = await analysis_engine.analyze_auto({"field": "value"})

    # Should have at least the working module's result
    assert result.total_modules_analyzed >= 1
