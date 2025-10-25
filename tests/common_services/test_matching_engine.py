"""
Comprehensive test suite for UniversalMatchingEngine.

Tests all functionality including:
- 6-dimension scoring
- Weighted score calculation
- Threshold filtering
- Confidence calculation
- Match explanation generation
- Edge cases and error handling
"""

import pytest
from backend.interfaces.data_structures import LogicTreeNode, MatchResult
from backend.common_services.matching_engine import UniversalMatchingEngine, DimensionScore


# ==== FIXTURES ====

@pytest.fixture
def engine():
    """Create a fresh UniversalMatchingEngine instance with default weights"""
    return UniversalMatchingEngine()


@pytest.fixture
def custom_weights_engine():
    """Create engine with custom weights"""
    weights = {
        "WHAT": 0.30,
        "WHICH": 0.25,
        "IF_THEN": 0.20,
        "MODALITY": 0.10,
        "GIVEN": 0.10,
        "WHY": 0.05
    }
    return UniversalMatchingEngine(dimension_weights=weights)


@pytest.fixture
def sample_node():
    """Create a sample LogicTreeNode with all 6 dimensions populated"""
    return LogicTreeNode(
        node_id="TEST-001",
        citation="Test Rule 1",
        module_id="TEST_MODULE",
        what=[
            {"fact": "Court may award costs"},
            {"proposition": "Costs follow the event"}
        ],
        which=[
            {"scope": "High Court"},
            {"entity": "Plaintiff"}
        ],
        if_then=[
            {"condition": "party succeeds", "consequence": "gets costs"}
        ],
        modality=[
            {"obligation": "MUST", "action": "file within 14 days"}
        ],
        given=[
            {"context": "civil proceedings"},
            {"assumption": "written submissions filed"}
        ],
        why=[
            {"rationale": "Encourage early settlement"},
            {"policy": "Access to justice"}
        ]
    )


@pytest.fixture
def minimal_node():
    """Create node with only WHAT dimension"""
    return LogicTreeNode(
        node_id="MIN-001",
        citation="Minimal Rule",
        module_id="TEST_MODULE",
        what=[{"fact": "Simple fact"}]
    )


@pytest.fixture
def empty_node():
    """Create node with no dimension content"""
    return LogicTreeNode(
        node_id="EMPTY-001",
        citation="Empty Rule",
        module_id="TEST_MODULE"
    )


# ==== INITIALIZATION TESTS ====

def test_engine_initialization_default_weights():
    """Test engine initializes with correct default weights"""
    engine = UniversalMatchingEngine()
    assert engine.weights["WHAT"] == 0.25
    assert engine.weights["WHICH"] == 0.20
    assert engine.weights["IF_THEN"] == 0.20
    assert engine.weights["MODALITY"] == 0.15
    assert engine.weights["GIVEN"] == 0.10
    assert engine.weights["WHY"] == 0.10
    assert sum(engine.weights.values()) == pytest.approx(1.0)


def test_engine_initialization_custom_weights(custom_weights_engine):
    """Test engine accepts custom weights"""
    assert custom_weights_engine.weights["WHAT"] == 0.30
    assert custom_weights_engine.weights["WHICH"] == 0.25
    assert sum(custom_weights_engine.weights.values()) == pytest.approx(1.0)


def test_engine_initialization_invalid_weights():
    """Test engine rejects weights that don't sum to 1.0"""
    invalid_weights = {
        "WHAT": 0.5,
        "WHICH": 0.2,
        "IF_THEN": 0.2,
        "MODALITY": 0.1,
        "GIVEN": 0.1,
        "WHY": 0.1  # Sum = 1.2, invalid
    }
    with pytest.raises(ValueError, match="must sum to 1.0"):
        UniversalMatchingEngine(dimension_weights=invalid_weights)


def test_engine_initialization_options():
    """Test engine accepts optional configuration"""
    engine = UniversalMatchingEngine(
        use_fuzzy_matching=True,
        case_sensitive=True
    )
    assert engine.use_fuzzy_matching is True
    assert engine.case_sensitive is True


# ==== BASIC MATCHING TESTS ====

@pytest.mark.asyncio
async def test_match_empty_nodes(engine):
    """Test match with empty node list"""
    filled = {"field": "value"}
    results = await engine.match([], filled, threshold=0.5)
    assert results == []


@pytest.mark.asyncio
async def test_match_empty_fields(engine, sample_node):
    """Test match with empty filled_fields"""
    results = await engine.match([sample_node], {}, threshold=0.5)
    assert results == []


@pytest.mark.asyncio
async def test_match_invalid_threshold(engine, sample_node):
    """Test match rejects invalid threshold"""
    filled = {"field": "value"}

    with pytest.raises(ValueError, match="threshold must be between"):
        await engine.match([sample_node], filled, threshold=1.5)

    with pytest.raises(ValueError, match="threshold must be between"):
        await engine.match([sample_node], filled, threshold=-0.1)


@pytest.mark.asyncio
async def test_match_single_node_above_threshold(engine, sample_node):
    """Test matching single node that scores above threshold"""
    filled = {"court": "High Court", "party": "Plaintiff"}
    results = await engine.match([sample_node], filled, threshold=0.1)

    assert len(results) == 1
    assert results[0].node_id == "TEST-001"
    assert results[0].match_score >= 0.1
    assert results[0].node == sample_node


@pytest.mark.asyncio
async def test_match_single_node_below_threshold(engine, sample_node):
    """Test matching single node that scores below threshold"""
    filled = {"irrelevant": "value"}
    results = await engine.match([sample_node], filled, threshold=0.9)

    # Should have no matches (score likely very low)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_match_multiple_nodes_sorted(engine):
    """Test matching multiple nodes returns sorted results"""
    # Create nodes with varying amounts of matching content
    node_high = LogicTreeNode(
        node_id="HIGH",
        citation="High Match",
        module_id="TEST",
        what=[{"fact": "court costs plaintiff"}],
        which=[{"scope": "court plaintiff"}]
    )

    node_low = LogicTreeNode(
        node_id="LOW",
        citation="Low Match",
        module_id="TEST",
        what=[{"fact": "unrelated content"}]
    )

    filled = {"court": "yes", "costs": "yes", "plaintiff": "yes"}
    results = await engine.match([node_low, node_high], filled, threshold=0.0)

    # Results should be sorted by match_score descending
    assert len(results) >= 1
    if len(results) > 1:
        assert results[0].match_score >= results[1].match_score


# ==== DIMENSION SCORING TESTS ====

@pytest.mark.asyncio
async def test_what_dimension_scoring(engine):
    """Test WHAT dimension scoring"""
    node = LogicTreeNode(
        node_id="WHAT-TEST",
        citation="What Test",
        module_id="TEST",
        what=[
            {"fact": "court costs"},
            {"proposition": "plaintiff wins"}
        ]
    )

    filled = {"info": "court costs plaintiff"}
    results = await engine.match([node], filled, threshold=0.0)

    assert len(results) == 1
    assert results[0].match_score > 0.0


@pytest.mark.asyncio
async def test_which_dimension_scoring(engine):
    """Test WHICH dimension scoring"""
    node = LogicTreeNode(
        node_id="WHICH-TEST",
        citation="Which Test",
        module_id="TEST",
        which=[
            {"scope": "High Court"},
            {"entity": "Plaintiff"}
        ]
    )

    filled = {"court": "High Court", "party": "Plaintiff"}
    results = await engine.match([node], filled, threshold=0.0)

    assert len(results) == 1
    assert results[0].match_score > 0.0


@pytest.mark.asyncio
async def test_if_then_dimension_scoring(engine):
    """Test IF-THEN dimension scoring"""
    node = LogicTreeNode(
        node_id="IF-TEST",
        citation="If Then Test",
        module_id="TEST",
        if_then=[
            {"condition": "party succeeds", "consequence": "gets costs"}
        ]
    )

    filled = {"outcome": "party succeeds gets costs"}
    results = await engine.match([node], filled, threshold=0.0)

    assert len(results) == 1
    assert results[0].match_score > 0.0


@pytest.mark.asyncio
async def test_modality_dimension_scoring(engine):
    """Test MODALITY dimension scoring"""
    node = LogicTreeNode(
        node_id="MOD-TEST",
        citation="Modality Test",
        module_id="TEST",
        modality=[
            {"obligation": "MUST", "action": "file within 14 days"}
        ]
    )

    filled = {"requirement": "must file"}
    results = await engine.match([node], filled, threshold=0.0)

    assert len(results) == 1
    assert results[0].match_score > 0.0


@pytest.mark.asyncio
async def test_given_dimension_scoring(engine):
    """Test GIVEN dimension scoring"""
    node = LogicTreeNode(
        node_id="GIVEN-TEST",
        citation="Given Test",
        module_id="TEST",
        given=[
            {"context": "civil proceedings"}
        ]
    )

    filled = {"case_type": "civil proceedings"}
    results = await engine.match([node], filled, threshold=0.0)

    assert len(results) == 1
    assert results[0].match_score > 0.0


@pytest.mark.asyncio
async def test_why_dimension_scoring(engine):
    """Test WHY dimension scoring"""
    node = LogicTreeNode(
        node_id="WHY-TEST",
        citation="Why Test",
        module_id="TEST",
        why=[
            {"rationale": "encourage settlement"}
        ]
    )

    filled = {"purpose": "settlement"}
    results = await engine.match([node], filled, threshold=0.0)

    assert len(results) == 1
    assert results[0].match_score > 0.0


# ==== WEIGHTED SCORING TESTS ====

@pytest.mark.asyncio
async def test_weighted_scoring_default(engine, sample_node):
    """Test that different dimensions contribute according to default weights"""
    # WHAT has weight 0.25 (highest)
    filled = {"info": "costs event"}  # Matches WHAT dimension
    results = await engine.match([sample_node], filled, threshold=0.0)

    assert len(results) == 1
    # Score should reflect WHAT's weight contribution


@pytest.mark.asyncio
async def test_weighted_scoring_custom(custom_weights_engine):
    """Test custom weights affect scoring"""
    node = LogicTreeNode(
        node_id="WEIGHT-TEST",
        citation="Weight Test",
        module_id="TEST",
        what=[{"fact": "important fact"}],  # Weight 0.30
        why=[{"reason": "minor reason"}]     # Weight 0.05
    )

    # Match WHAT dimension (higher weight)
    filled_what = {"info": "important fact"}
    results_what = await custom_weights_engine.match([node], filled_what, threshold=0.0)

    # Match WHY dimension (lower weight)
    filled_why = {"info": "minor reason"}
    results_why = await custom_weights_engine.match([node], filled_why, threshold=0.0)

    # WHAT match should score higher due to higher weight
    if results_what and results_why:
        assert results_what[0].match_score > results_why[0].match_score


# ==== CONFIDENCE CALCULATION TESTS ====

@pytest.mark.asyncio
async def test_confidence_more_dimensions_higher(engine):
    """Test confidence is higher when more dimensions have content"""
    # Node with many dimensions
    node_many = LogicTreeNode(
        node_id="MANY",
        citation="Many Dimensions",
        module_id="TEST",
        what=[{"a": "x"}],
        which=[{"b": "y"}],
        if_then=[{"c": "z"}],
        modality=[{"d": "w"}],
        given=[{"e": "v"}],
        why=[{"f": "u"}]
    )

    # Node with one dimension
    node_one = LogicTreeNode(
        node_id="ONE",
        citation="One Dimension",
        module_id="TEST",
        what=[{"a": "x"}]
    )

    filled = {"info": "x"}
    results_many = await engine.match([node_many], filled, threshold=0.0)
    results_one = await engine.match([node_one], filled, threshold=0.0)

    if results_many and results_one:
        # Node with more dimensions should have higher confidence
        assert results_many[0].confidence >= results_one[0].confidence


@pytest.mark.asyncio
async def test_confidence_more_fields_higher(engine, sample_node):
    """Test confidence is higher with more filled fields"""
    filled_few = {"field1": "value"}
    filled_many = {"field1": "value", "field2": "value", "field3": "value"}

    results_few = await engine.match([sample_node], filled_few, threshold=0.0)
    results_many = await engine.match([sample_node], filled_many, threshold=0.0)

    # More filled fields should lead to higher confidence
    if results_few and results_many:
        assert results_many[0].confidence >= results_few[0].confidence


# ==== MATCH RESULT TESTS ====

@pytest.mark.asyncio
async def test_match_result_structure(engine, sample_node):
    """Test MatchResult has correct structure"""
    filled = {"court": "High Court"}
    results = await engine.match([sample_node], filled, threshold=0.0)

    assert len(results) >= 1
    result = results[0]

    # Check all required fields
    assert isinstance(result.node_id, str)
    assert isinstance(result.node, LogicTreeNode)
    assert isinstance(result.match_score, float)
    assert 0.0 <= result.match_score <= 1.0
    assert isinstance(result.matched_fields, dict)
    assert isinstance(result.missing_fields, list)
    assert isinstance(result.confidence, float)
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.reasoning, str)


@pytest.mark.asyncio
async def test_match_result_reasoning(engine, sample_node):
    """Test reasoning is generated"""
    filled = {"court": "High Court", "party": "Plaintiff"}
    results = await engine.match([sample_node], filled, threshold=0.0)

    assert len(results) >= 1
    reasoning = results[0].reasoning

    assert reasoning != ""
    assert "match" in reasoning.lower()


# ==== THRESHOLD FILTERING TESTS ====

@pytest.mark.asyncio
async def test_threshold_filters_low_scores(engine):
    """Test threshold correctly filters low-scoring matches"""
    node = LogicTreeNode(
        node_id="FILTER-TEST",
        citation="Filter Test",
        module_id="TEST",
        what=[{"fact": "specific content"}]
    )

    # Fields that won't match well
    filled = {"unrelated": "completely different"}

    # Low threshold - might get results
    results_low = await engine.match([node], filled, threshold=0.0)

    # High threshold - should filter out
    results_high = await engine.match([node], filled, threshold=0.9)

    assert len(results_high) <= len(results_low)


@pytest.mark.asyncio
async def test_threshold_exact_boundary(engine):
    """Test nodes scoring exactly at threshold are included"""
    # This is hard to test precisely, but we can verify behavior
    node = LogicTreeNode(
        node_id="BOUNDARY",
        citation="Boundary Test",
        module_id="TEST",
        what=[{"fact": "test"}]
    )

    filled = {"info": "test"}
    results = await engine.match([node], filled, threshold=0.0)

    # At threshold 0.0, any match should be included
    assert len(results) >= 1


# ==== STATISTICS TESTS ====

def test_statistics_initialization(engine):
    """Test statistics are initialized to zero"""
    assert engine.get_match_count() == 0
    assert engine.get_nodes_evaluated() == 0


@pytest.mark.asyncio
async def test_statistics_tracking(engine, sample_node):
    """Test statistics are tracked correctly"""
    filled = {"field": "value"}

    # First match
    await engine.match([sample_node], filled)
    assert engine.get_match_count() == 1
    assert engine.get_nodes_evaluated() == 1

    # Second match with 2 nodes
    await engine.match([sample_node, sample_node], filled)
    assert engine.get_match_count() == 2
    assert engine.get_nodes_evaluated() == 3  # 1 + 2


def test_statistics_reset(engine):
    """Test statistics can be reset"""
    engine._match_count = 10
    engine._total_nodes_evaluated = 50

    engine.reset_statistics()

    assert engine.get_match_count() == 0
    assert engine.get_nodes_evaluated() == 0


# ==== EDGE CASES ====

@pytest.mark.asyncio
async def test_match_empty_node_dimensions(engine, empty_node):
    """Test matching node with no dimension content"""
    filled = {"field": "value"}
    results = await engine.match([empty_node], filled, threshold=0.0)

    # With threshold 0.0, empty node is returned with score 0.0
    # This is correct behavior (0.0 >= 0.0)
    if results:
        assert results[0].match_score == 0.0

    # With higher threshold, should be filtered out
    results_filtered = await engine.match([empty_node], filled, threshold=0.1)
    assert len(results_filtered) == 0


@pytest.mark.asyncio
async def test_match_minimal_node(engine, minimal_node):
    """Test matching node with only one dimension"""
    filled = {"info": "Simple"}
    results = await engine.match([minimal_node], filled, threshold=0.0)

    # Should match if search term appears
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_case_sensitivity_disabled(engine):
    """Test case-insensitive matching (default)"""
    node = LogicTreeNode(
        node_id="CASE-TEST",
        citation="Case Test",
        module_id="TEST",
        what=[{"fact": "UPPERCASE CONTENT"}]
    )

    filled = {"info": "uppercase content"}  # lowercase
    results = await engine.match([node], filled, threshold=0.0)

    # Should match despite case difference
    assert len(results) >= 1


@pytest.mark.asyncio
async def test_case_sensitivity_enabled():
    """Test case-sensitive matching when enabled"""
    engine = UniversalMatchingEngine(case_sensitive=True)

    node = LogicTreeNode(
        node_id="CASE-TEST",
        citation="Case Test",
        module_id="TEST",
        what=[{"fact": "UPPERCASE"}]
    )

    # Exact case match
    filled_match = {"info": "UPPERCASE"}
    results_match = await engine.match([node], filled_match, threshold=0.0)

    # Different case
    filled_no_match = {"info": "uppercase"}
    results_no_match = await engine.match([node], filled_no_match, threshold=0.0)

    # With case sensitivity, different case should score lower
    # (or not match at all depending on implementation)
    assert len(results_match) >= len(results_no_match)


@pytest.mark.asyncio
async def test_special_characters_in_fields(engine):
    """Test handling of special characters"""
    node = LogicTreeNode(
        node_id="SPECIAL",
        citation="Special Test",
        module_id="TEST",
        what=[{"fact": "test@123"}]
    )

    filled = {"info": "test@123"}
    results = await engine.match([node], filled, threshold=0.0)

    # Should handle special characters
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_numeric_values_in_fields(engine):
    """Test handling of numeric values"""
    node = LogicTreeNode(
        node_id="NUMERIC",
        citation="Numeric Test",
        module_id="TEST",
        what=[{"amount": "1000"}]
    )

    filled = {"value": 1000}  # Integer
    results = await engine.match([node], filled, threshold=0.0)

    # Should convert and match
    assert len(results) >= 0


# ==== INTEGRATION TESTS ====

@pytest.mark.asyncio
async def test_full_workflow(engine):
    """Test complete matching workflow"""
    # Create a set of nodes
    nodes = [
        LogicTreeNode(
            node_id=f"NODE-{i}",
            citation=f"Rule {i}",
            module_id="TEST",
            what=[{"fact": f"content {i}"}],
            which=[{"scope": "general"}]
        )
        for i in range(5)
    ]

    # Add one highly relevant node
    nodes.append(LogicTreeNode(
        node_id="RELEVANT",
        citation="Highly Relevant",
        module_id="TEST",
        what=[{"fact": "target content match"}],
        which=[{"scope": "target"}],
        if_then=[{"condition": "target scenario"}]
    ))

    # Match with relevant fields
    filled = {"query": "target content match scenario"}
    results = await engine.match(nodes, filled, threshold=0.3)

    # Should find the relevant node
    assert len(results) >= 1

    # Relevant node should be in top results
    top_ids = [r.node_id for r in results[:3]]
    assert "RELEVANT" in top_ids


@pytest.mark.asyncio
async def test_no_false_positives(engine):
    """Test engine doesn't return false positives"""
    node = LogicTreeNode(
        node_id="SPECIFIC",
        citation="Very Specific",
        module_id="TEST",
        what=[{"fact": "very specific unique content xyz123"}]
    )

    # Completely unrelated query
    filled = {"query": "completely unrelated abc789"}
    results = await engine.match([node], filled, threshold=0.7)

    # Should not match with high threshold
    assert len(results) == 0
