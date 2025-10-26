"""
Tests for Deductive Questioning Engine
Legal Advisory System v5.0
"""

import pytest
from backend.conversation import DeductiveQuestioningEngine
from backend.interfaces import (
    ConversationSession,
    ConversationStatus,
    FieldRequirement,
    QuestionTemplate,
)


@pytest.fixture
def questioning_engine():
    """Create questioning engine"""
    return DeductiveQuestioningEngine()


@pytest.fixture
def sample_session():
    """Create sample session"""
    return ConversationSession(
        session_id="test_session",
        user_id="test_user",
        status=ConversationStatus.INFORMATION_GATHERING,
        filled_fields={},
    )


@pytest.fixture
def sample_field_requirements():
    """Create sample field requirements"""
    return [
        FieldRequirement(
            field_name="court_level",
            field_type="enum",
            description="Level of court",
            required=True,
            validation_rules={},
            enum_values=["High Court", "District Court"],
        ),
        FieldRequirement(
            field_name="case_type",
            field_type="enum",
            description="Type of case",
            required=True,
            validation_rules={},
            enum_values=["default_judgment", "summary_judgment"],
        ),
        FieldRequirement(
            field_name="claim_amount",
            field_type="number",
            description="Claim amount in SGD",
            required=True,
            validation_rules={"min_value": 0},
        ),
        FieldRequirement(
            field_name="complexity_level",
            field_type="enum",
            description="Case complexity",
            required=False,
            validation_rules={},
            enum_values=["simple", "complex"],
        ),
    ]


@pytest.fixture
def sample_question_templates():
    """Create sample question templates"""
    return [
        QuestionTemplate(
            field_name="court_level",
            template="In which court is this matter filed?",
            priority=1,
        ),
        QuestionTemplate(
            field_name="case_type",
            template="What type of case is this?",
            priority=2,
        ),
        QuestionTemplate(
            field_name="claim_amount",
            template="What is the claim amount in SGD?",
            priority=3,
        ),
    ]


# ============================================
# GAP ANALYSIS TESTS
# ============================================


def test_analyze_gaps_all_missing(questioning_engine, sample_field_requirements):
    """Test gap analysis when all fields are missing"""
    filled_fields = {}

    gaps = questioning_engine.analyze_gaps(filled_fields, sample_field_requirements)

    assert len(gaps) == 4
    assert all(gap.current_value is None for gap in gaps)


def test_analyze_gaps_some_filled(questioning_engine, sample_field_requirements):
    """Test gap analysis when some fields are filled"""
    filled_fields = {"court_level": "High Court", "case_type": "default_judgment"}

    gaps = questioning_engine.analyze_gaps(filled_fields, sample_field_requirements)

    assert len(gaps) == 2
    gap_names = [gap.field_name for gap in gaps]
    assert "claim_amount" in gap_names
    assert "complexity_level" in gap_names


def test_analyze_gaps_all_filled(questioning_engine, sample_field_requirements):
    """Test gap analysis when all fields are filled"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "default_judgment",
        "claim_amount": 50000,
        "complexity_level": "simple",
    }

    gaps = questioning_engine.analyze_gaps(filled_fields, sample_field_requirements)

    assert len(gaps) == 0


def test_gap_has_correct_properties(questioning_engine, sample_field_requirements):
    """Test that gaps have correct properties"""
    filled_fields = {}

    gaps = questioning_engine.analyze_gaps(filled_fields, sample_field_requirements)

    court_gap = next((g for g in gaps if g.field_name == "court_level"), None)
    assert court_gap is not None
    assert court_gap.field_type == "enum"
    assert court_gap.required is True
    assert court_gap.priority == 1


# ============================================
# QUESTION GENERATION TESTS
# ============================================


def test_generate_question_with_template(
    questioning_engine, sample_session, sample_field_requirements, sample_question_templates
):
    """Test question generation using templates"""
    question = questioning_engine.generate_question(
        sample_session, sample_field_requirements, sample_question_templates
    )

    assert question is not None
    assert len(question) > 0
    # Should match one of the templates
    assert question in [qt.template for qt in sample_question_templates]


def test_generate_question_no_gaps(
    questioning_engine, sample_session, sample_field_requirements, sample_question_templates
):
    """Test question generation when no gaps exist"""
    # Fill all fields
    sample_session.filled_fields = {
        "court_level": "High Court",
        "case_type": "default_judgment",
        "claim_amount": 50000,
        "complexity_level": "simple",
    }

    question = questioning_engine.generate_question(
        sample_session, sample_field_requirements, sample_question_templates
    )

    assert question is None


def test_generate_question_fallback(
    questioning_engine, sample_session, sample_field_requirements
):
    """Test fallback question generation without templates"""
    question = questioning_engine.generate_question(
        sample_session, sample_field_requirements, []  # No templates
    )

    assert question is not None
    assert len(question) > 0


def test_generate_multiple_questions(
    questioning_engine, sample_session, sample_field_requirements, sample_question_templates
):
    """Test generating multiple questions at once"""
    questions = questioning_engine.generate_multiple_questions(
        sample_session,
        sample_field_requirements,
        sample_question_templates,
        max_questions=3,
    )

    assert len(questions) <= 3
    assert all(isinstance(q, str) for q in questions)
    assert all(len(q) > 0 for q in questions)


def test_generate_multiple_questions_respects_max(
    questioning_engine, sample_session, sample_field_requirements, sample_question_templates
):
    """Test that max_questions is respected"""
    questions = questioning_engine.generate_multiple_questions(
        sample_session,
        sample_field_requirements,
        sample_question_templates,
        max_questions=2,
    )

    assert len(questions) <= 2


# ============================================
# STRATEGY TESTS
# ============================================


def test_high_impact_strategy(
    questioning_engine, sample_session, sample_field_requirements, sample_question_templates
):
    """Test high impact strategy prioritizes required fields"""
    # Partially fill fields
    sample_session.filled_fields = {"court_level": "High Court"}

    question = questioning_engine.generate_question(
        sample_session,
        sample_field_requirements,
        sample_question_templates,
        strategy_name="high_impact",
    )

    assert question is not None
    # Should ask about required field (case_type or claim_amount)
    assert question in ["What type of case is this?", "What is the claim amount in SGD?"]


def test_user_friendly_strategy(
    questioning_engine, sample_session, sample_field_requirements, sample_question_templates
):
    """Test user friendly strategy asks simple questions first"""
    question = questioning_engine.generate_question(
        sample_session,
        sample_field_requirements,
        sample_question_templates,
        strategy_name="user_friendly",
    )

    assert question is not None


def test_rapid_completion_strategy(
    questioning_engine, sample_session, sample_field_requirements, sample_question_templates
):
    """Test rapid completion strategy"""
    question = questioning_engine.generate_question(
        sample_session,
        sample_field_requirements,
        sample_question_templates,
        strategy_name="rapid",
    )

    assert question is not None


def test_invalid_strategy_uses_default(
    questioning_engine, sample_session, sample_field_requirements, sample_question_templates
):
    """Test that invalid strategy falls back to default"""
    question = questioning_engine.generate_question(
        sample_session,
        sample_field_requirements,
        sample_question_templates,
        strategy_name="invalid_strategy",
    )

    assert question is not None  # Should still work with default


# ============================================
# STRATEGY CONFIGURATION TESTS
# ============================================


def test_set_default_strategy(questioning_engine):
    """Test setting default strategy"""
    result = questioning_engine.set_default_strategy("high_impact")

    assert result is True
    assert questioning_engine.default_strategy == "high_impact"


def test_set_invalid_default_strategy(questioning_engine):
    """Test setting invalid default strategy"""
    original_default = questioning_engine.default_strategy

    result = questioning_engine.set_default_strategy("invalid_strategy")

    assert result is False
    assert questioning_engine.default_strategy == original_default


# ============================================
# FALLBACK QUESTION GENERATION TESTS
# ============================================


def test_fallback_question_enum_type(questioning_engine):
    """Test fallback question for enum type"""
    from backend.interfaces import InfoGap

    gap = InfoGap(
        field_name="test_enum",
        field_type="enum",
        description="Test enum field",
        priority=1,
        required=True,
    )

    question = questioning_engine._generate_fallback_question(gap)

    assert "test enum" in question.lower()


def test_fallback_question_number_type(questioning_engine):
    """Test fallback question for number type"""
    from backend.interfaces import InfoGap

    gap = InfoGap(
        field_name="test_number",
        field_type="number",
        description="Test number field",
        priority=1,
        required=True,
    )

    question = questioning_engine._generate_fallback_question(gap)

    assert "test number" in question.lower()


def test_fallback_question_string_type(questioning_engine):
    """Test fallback question for string type"""
    from backend.interfaces import InfoGap

    gap = InfoGap(
        field_name="test_string",
        field_type="string",
        description="Test string field",
        priority=1,
        required=True,
    )

    question = questioning_engine._generate_fallback_question(gap)

    assert "test string" in question.lower()


# ============================================
# STATISTICS TESTS
# ============================================


def test_statistics_tracking(
    questioning_engine, sample_session, sample_field_requirements, sample_question_templates
):
    """Test statistics tracking"""
    initial_stats = questioning_engine.get_statistics()

    # Generate some questions
    questioning_engine.generate_question(
        sample_session, sample_field_requirements, sample_question_templates
    )
    questioning_engine.generate_question(
        sample_session,
        sample_field_requirements,
        sample_question_templates,
        strategy_name="high_impact",
    )

    stats = questioning_engine.get_statistics()

    assert stats["total_questions_generated"] > initial_stats["total_questions_generated"]
    assert "available_strategies" in stats
    assert "default_strategy" in stats


def test_strategy_usage_tracking(
    questioning_engine, sample_session, sample_field_requirements, sample_question_templates
):
    """Test that strategy usage is tracked"""
    # Generate questions with different strategies
    questioning_engine.generate_question(
        sample_session,
        sample_field_requirements,
        sample_question_templates,
        strategy_name="high_impact",
    )
    questioning_engine.generate_question(
        sample_session,
        sample_field_requirements,
        sample_question_templates,
        strategy_name="rapid",
    )

    stats = questioning_engine.get_statistics()

    assert stats["strategy_usage"]["high_impact"] >= 1
    assert stats["strategy_usage"]["rapid"] >= 1


# ============================================
# INTEGRATION TESTS
# ============================================


def test_end_to_end_questioning_flow(
    questioning_engine, sample_session, sample_field_requirements, sample_question_templates
):
    """Test complete questioning flow"""
    # Start with no fields
    assert len(sample_session.filled_fields) == 0

    # Generate first question
    q1 = questioning_engine.generate_question(
        sample_session, sample_field_requirements, sample_question_templates
    )
    assert q1 is not None

    # Simulate answering first question
    sample_session.filled_fields["court_level"] = "High Court"

    # Generate second question
    q2 = questioning_engine.generate_question(
        sample_session, sample_field_requirements, sample_question_templates
    )
    assert q2 is not None
    assert q2 != q1  # Should be different question

    # Fill all required fields
    sample_session.filled_fields.update(
        {"case_type": "default_judgment", "claim_amount": 50000}
    )

    # Should now ask about optional field or return None
    q3 = questioning_engine.generate_question(
        sample_session, sample_field_requirements, sample_question_templates
    )
    # q3 could be None (if only asking required) or ask about complexity_level


def test_questioning_engine_initialization():
    """Test questioning engine initialization"""
    engine = DeductiveQuestioningEngine()

    assert engine.default_strategy == "user_friendly"
    assert len(engine.strategies) == 3
    assert "high_impact" in engine.strategies
    assert "user_friendly" in engine.strategies
    assert "rapid" in engine.strategies
