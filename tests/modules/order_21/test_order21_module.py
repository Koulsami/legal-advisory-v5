"""
Tests for Order21Module
Legal Advisory System v5.0

Comprehensive tests for Order 21 cost calculation module.
"""

import pytest
from backend.modules.order_21 import Order21Module
from backend.interfaces import ModuleStatus


@pytest.fixture
def order21_module():
    """Create Order21Module instance"""
    return Order21Module()


# ============================================
# METADATA TESTS
# ============================================


def test_module_metadata(order21_module):
    """Test module metadata"""
    metadata = order21_module.metadata

    assert metadata.module_id == "ORDER_21"
    assert "Order 21" in metadata.module_name
    assert "Party-and-Party Costs" in metadata.module_name
    assert metadata.version == "1.0.0"
    assert metadata.status == ModuleStatus.ACTIVE
    assert "costs" in metadata.tags
    assert "singapore" in metadata.tags


def test_module_version(order21_module):
    """Test tree version"""
    version = order21_module.get_tree_version()
    assert version == "1.0.0"


# ============================================
# TREE TESTS
# ============================================


def test_tree_nodes_loaded(order21_module):
    """Test that pre-built tree nodes are loaded"""
    nodes = order21_module.get_tree_nodes()

    # Should have 38 nodes (29 rules + 9 scenarios)
    assert len(nodes) == 38

    # All nodes should have module_id ORDER_21
    for node in nodes:
        assert node.module_id == "ORDER_21"


def test_tree_nodes_have_citations(order21_module):
    """Test all nodes have proper citations"""
    nodes = order21_module.get_tree_nodes()

    for node in nodes:
        assert node.citation is not None
        assert len(node.citation) > 0
        assert "Order 21" in node.citation or "Appendix 1" in node.citation


def test_tree_has_rule_nodes(order21_module):
    """Test tree contains Order 21 rule nodes"""
    nodes = order21_module.get_tree_nodes()
    rule_nodes = [n for n in nodes if n.node_id.startswith("ORDER21_RULE_")]

    # Should have 29 rule nodes
    assert len(rule_nodes) == 29


def test_tree_has_scenario_nodes(order21_module):
    """Test tree contains Appendix 1 scenario nodes"""
    nodes = order21_module.get_tree_nodes()
    scenario_nodes = [n for n in nodes if n.node_id.startswith("APPENDIX1_SCENARIO_")]

    # Should have 9 scenario nodes
    assert len(scenario_nodes) == 9


# ============================================
# FIELD REQUIREMENTS TESTS
# ============================================


def test_field_requirements(order21_module):
    """Test field requirements"""
    requirements = order21_module.get_field_requirements()

    # Should have at least 7 fields
    assert len(requirements) >= 7

    # Check required fields
    field_names = [r.field_name for r in requirements]
    assert "court_level" in field_names
    assert "case_type" in field_names
    assert "claim_amount" in field_names


def test_required_fields_marked_correctly(order21_module):
    """Test that required fields are marked as required"""
    requirements = order21_module.get_field_requirements()
    required_fields = [r for r in requirements if r.required]

    # Should have at least 3 required fields
    assert len(required_fields) >= 3

    # Core fields should be required
    required_names = [r.field_name for r in required_fields]
    assert "court_level" in required_names
    assert "case_type" in required_names
    assert "claim_amount" in required_names


def test_field_enum_values(order21_module):
    """Test enum fields have valid values"""
    requirements = order21_module.get_field_requirements()

    # Find court_level field
    court_field = next((r for r in requirements if r.field_name == "court_level"), None)
    assert court_field is not None
    assert court_field.field_type == "enum"
    assert "High Court" in court_field.enum_values
    assert "District Court" in court_field.enum_values
    assert "Magistrates Court" in court_field.enum_values


# ============================================
# QUESTION TEMPLATES TESTS
# ============================================


def test_question_templates(order21_module):
    """Test question templates"""
    questions = order21_module.get_question_templates()

    # Should have templates for main fields
    assert len(questions) >= 7

    # Check priorities are assigned
    for q in questions:
        assert q.priority > 0


def test_question_templates_cover_required_fields(order21_module):
    """Test that questions cover required fields"""
    questions = order21_module.get_question_templates()
    question_fields = [q.field_name for q in questions]

    assert "court_level" in question_fields
    assert "case_type" in question_fields
    assert "claim_amount" in question_fields


# ============================================
# VALIDATION TESTS
# ============================================


def test_validate_fields_success(order21_module):
    """Test successful field validation"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 50000,
    }

    is_valid, errors = order21_module.validate_fields(filled_fields)

    assert is_valid is True
    assert len(errors) == 0


def test_validate_fields_missing_required(order21_module):
    """Test validation with missing required fields"""
    filled_fields = {
        "court_level": "High Court",
        # Missing case_type and claim_amount
    }

    is_valid, errors = order21_module.validate_fields(filled_fields)

    assert is_valid is False
    assert len(errors) >= 2
    assert any("case_type" in e for e in errors)
    assert any("claim_amount" in e for e in errors)


def test_validate_fields_invalid_court(order21_module):
    """Test validation with invalid court level"""
    filled_fields = {
        "court_level": "Supreme Court",  # Invalid
        "case_type": "default_judgment_liquidated",
        "claim_amount": 50000,
    }

    is_valid, errors = order21_module.validate_fields(filled_fields)

    assert is_valid is False
    assert any("court_level" in e for e in errors)


def test_validate_fields_invalid_case_type(order21_module):
    """Test validation with invalid case type"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "invalid_type",
        "claim_amount": 50000,
    }

    is_valid, errors = order21_module.validate_fields(filled_fields)

    assert is_valid is False
    assert any("case_type" in e for e in errors)


def test_validate_fields_negative_claim(order21_module):
    """Test validation with negative claim amount"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": -1000,
    }

    is_valid, errors = order21_module.validate_fields(filled_fields)

    assert is_valid is False
    assert any("claim_amount" in e for e in errors)


def test_validate_fields_contested_trial_requires_days(order21_module):
    """Test that contested trial requires trial_days"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "contested_trial",
        "claim_amount": 100000,
        # Missing trial_days
    }

    is_valid, errors = order21_module.validate_fields(filled_fields)

    assert is_valid is False
    assert any("trial_days" in e for e in errors)


# ============================================
# COMPLETENESS TESTS
# ============================================


def test_check_completeness_full(order21_module):
    """Test completeness with all fields"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 50000,
        "complexity_level": "moderate",
        "basis_of_taxation": "standard",
        "party_type": "plaintiff",
    }

    score, missing = order21_module.check_completeness(filled_fields)

    assert score == 1.0
    assert len(missing) == 0


def test_check_completeness_required_only(order21_module):
    """Test completeness with only required fields"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 50000,
    }

    score, missing = order21_module.check_completeness(filled_fields)

    # Should be 70% (all required, no recommended)
    assert score == 0.7
    assert len(missing) > 0


def test_check_completeness_empty(order21_module):
    """Test completeness with no fields"""
    filled_fields = {}

    score, missing = order21_module.check_completeness(filled_fields)

    assert score == 0.0
    assert len(missing) >= 3


def test_check_completeness_contested_trial(order21_module):
    """Test completeness for contested trial (requires trial_days)"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "contested_trial",
        "claim_amount": 100000,
        "trial_days": 3,
    }

    score, missing = order21_module.check_completeness(filled_fields)

    # Should have good score since all required fields present
    assert score >= 0.7


# ============================================
# CALCULATION TESTS - Default Judgment Liquidated
# ============================================


def test_calculate_default_judgment_liquidated_low(order21_module):
    """Test calculation for default judgment with low claim amount"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 3000,
    }

    result = order21_module.calculate(filled_fields)

    assert result["total_costs"] > 0
    assert result["cost_range_min"] == 800.0
    assert result["cost_range_max"] == 1500.0
    assert result["claim_amount"] == 3000
    assert "Appendix 1" in result["calculation_basis"]


def test_calculate_default_judgment_liquidated_mid(order21_module):
    """Test calculation for default judgment with mid claim amount"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 50000,
    }

    result = order21_module.calculate(filled_fields)

    assert result["total_costs"] > 0
    assert result["cost_range_min"] == 3000.0
    assert result["cost_range_max"] == 5000.0


def test_calculate_default_judgment_liquidated_high(order21_module):
    """Test calculation for default judgment with high claim amount"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 300000,
    }

    result = order21_module.calculate(filled_fields)

    assert result["total_costs"] > 0
    assert result["cost_range_min"] == 10000.0
    assert result["cost_range_max"] == 15000.0


# ============================================
# CALCULATION TESTS - Court Level Adjustments
# ============================================


def test_calculate_district_court_adjustment(order21_module):
    """Test District Court costs are 65% of High Court"""
    filled_fields_high = {
        "court_level": "High Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 50000,
    }

    filled_fields_district = {
        "court_level": "District Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 50000,
    }

    result_high = order21_module.calculate(filled_fields_high)
    result_district = order21_module.calculate(filled_fields_district)

    # District should be approximately 65% of High Court
    expected_district = result_high["total_costs"] * 0.65
    assert abs(result_district["total_costs"] - expected_district) < 1.0


def test_calculate_magistrates_court_adjustment(order21_module):
    """Test Magistrates Court costs are 45% of High Court"""
    filled_fields_high = {
        "court_level": "High Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 50000,
    }

    filled_fields_magistrates = {
        "court_level": "Magistrates Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 50000,
    }

    result_high = order21_module.calculate(filled_fields_high)
    result_magistrates = order21_module.calculate(filled_fields_magistrates)

    # Magistrates should be approximately 45% of High Court
    expected_magistrates = result_high["total_costs"] * 0.45
    assert abs(result_magistrates["total_costs"] - expected_magistrates) < 1.0


# ============================================
# CALCULATION TESTS - Other Case Types
# ============================================


def test_calculate_summary_judgment(order21_module):
    """Test calculation for summary judgment"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "summary_judgment",
        "claim_amount": 100000,
    }

    result = order21_module.calculate(filled_fields)

    assert result["total_costs"] > 0
    assert result["cost_range_min"] == 5000.0
    assert result["cost_range_max"] == 10000.0


def test_calculate_contested_trial_1_2_days(order21_module):
    """Test calculation for 1-2 day contested trial"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "contested_trial",
        "claim_amount": 100000,
        "trial_days": 2,
        "complexity_level": "moderate",
    }

    result = order21_module.calculate(filled_fields)

    assert result["total_costs"] > 0
    assert result["total_costs"] >= 15000  # Should be in mid-range


def test_calculate_contested_trial_3_5_days(order21_module):
    """Test calculation for 3-5 day contested trial"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "contested_trial",
        "claim_amount": 300000,
        "trial_days": 4,
        "complexity_level": "moderate",
    }

    result = order21_module.calculate(filled_fields)

    assert result["total_costs"] > 0
    assert result["total_costs"] >= 60000  # Should be in high range


def test_calculate_contested_trial_6_plus_days(order21_module):
    """Test calculation for 6+ day contested trial"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "contested_trial",
        "claim_amount": 500000,
        "trial_days": 10,
        "complexity_level": "moderate",
    }

    result = order21_module.calculate(filled_fields)

    assert result["total_costs"] > 0
    assert result["total_costs"] >= 100000  # Should be in very high range


def test_calculate_trial_complexity_adjustment(order21_module):
    """Test complexity adjustments for contested trials"""
    filled_fields_simple = {
        "court_level": "High Court",
        "case_type": "contested_trial",
        "claim_amount": 100000,
        "trial_days": 2,
        "complexity_level": "simple",
    }

    filled_fields_complex = {
        "court_level": "High Court",
        "case_type": "contested_trial",
        "claim_amount": 100000,
        "trial_days": 2,
        "complexity_level": "very_complex",
    }

    result_simple = order21_module.calculate(filled_fields_simple)
    result_complex = order21_module.calculate(filled_fields_complex)

    # Complex should cost more than simple
    assert result_complex["total_costs"] > result_simple["total_costs"]


def test_calculate_interlocutory_simple(order21_module):
    """Test calculation for simple interlocutory application"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "interlocutory_application",
        "claim_amount": 50000,
        "complexity_level": "simple",
    }

    result = order21_module.calculate(filled_fields)

    assert result["total_costs"] > 0
    assert result["cost_range_min"] == 1500.0
    assert result["cost_range_max"] == 3000.0


def test_calculate_interlocutory_complex(order21_module):
    """Test calculation for complex interlocutory application"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "interlocutory_application",
        "claim_amount": 50000,
        "complexity_level": "complex",
    }

    result = order21_module.calculate(filled_fields)

    assert result["total_costs"] > 0
    assert result["cost_range_min"] == 3000.0
    assert result["cost_range_max"] == 8000.0


def test_calculate_appeal(order21_module):
    """Test calculation for appeal"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "appeal",
        "claim_amount": 200000,
    }

    result = order21_module.calculate(filled_fields)

    assert result["total_costs"] > 0
    assert result["cost_range_min"] == 30000.0
    assert result["cost_range_max"] == 60000.0


def test_calculate_striking_out(order21_module):
    """Test calculation for striking out"""
    filled_fields = {
        "court_level": "High Court",
        "case_type": "striking_out",
        "claim_amount": 100000,
    }

    result = order21_module.calculate(filled_fields)

    assert result["total_costs"] > 0
    assert result["cost_range_min"] == 5000.0
    assert result["cost_range_max"] == 10000.0


# ============================================
# ARGUMENTS TESTS
# ============================================


def test_get_arguments(order21_module):
    """Test argument generation"""
    calculation = {
        "total_costs": 5000.0,
        "court_level": "High Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 50000.0,
        "calculation_basis": "Appendix 1, Section B",
        "base_costs": 5000.0,
        "cost_range_min": 3000.0,
        "cost_range_max": 7000.0,
    }

    filled_fields = {
        "court_level": "High Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 50000,
    }

    arguments = order21_module.get_arguments(calculation, filled_fields)

    assert "main_argument" in arguments
    assert "supporting_points" in arguments
    assert "legal_citations" in arguments
    assert "$5,000" in arguments["main_argument"]
    assert "High Court" in arguments["main_argument"]


def test_arguments_have_citations(order21_module):
    """Test that arguments include legal citations"""
    calculation = {
        "total_costs": 5000.0,
        "court_level": "High Court",
        "case_type": "summary_judgment",
        "claim_amount": 100000.0,
        "calculation_basis": "Appendix 1, Section C",
        "base_costs": 5000.0,
        "cost_range_min": 4000.0,
        "cost_range_max": 6000.0,
    }

    filled_fields = {}

    arguments = order21_module.get_arguments(calculation, filled_fields)

    citations = arguments["legal_citations"]
    assert len(citations) > 0
    assert any("Order 21" in c for c in citations)


# ============================================
# RECOMMENDATIONS TESTS
# ============================================


def test_get_recommendations(order21_module):
    """Test recommendation generation"""
    calculation = {
        "total_costs": 5000.0,
        "case_type": "default_judgment_liquidated",
        "claim_amount": 50000.0,
    }

    recommendations = order21_module.get_recommendations(calculation)

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0


def test_recommendations_for_high_costs(order21_module):
    """Test that high cost cases get security recommendation"""
    calculation = {
        "total_costs": 100000.0,
        "case_type": "contested_trial",
        "claim_amount": 500000.0,
    }

    recommendations = order21_module.get_recommendations(calculation)

    # Should recommend security for costs
    assert any("security for costs" in r.lower() for r in recommendations)


def test_recommendations_case_specific(order21_module):
    """Test case-specific recommendations"""
    # Default judgment
    calc_default = {
        "total_costs": 3000.0,
        "case_type": "default_judgment_liquidated",
        "claim_amount": 20000.0,
    }

    recs_default = order21_module.get_recommendations(calc_default)
    assert any("default judgment" in r.lower() for r in recs_default)

    # Contested trial
    calc_trial = {
        "total_costs": 50000.0,
        "case_type": "contested_trial",
        "claim_amount": 200000.0,
    }

    recs_trial = order21_module.get_recommendations(calc_trial)
    assert any("settlement" in r.lower() or "trial" in r.lower() for r in recs_trial)


# ============================================
# INTEGRATION TESTS
# ============================================


def test_end_to_end_workflow(order21_module):
    """Test complete workflow from validation to calculation to arguments"""
    # Step 1: Validate
    filled_fields = {
        "court_level": "High Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 75000,
        "complexity_level": "moderate",
    }

    is_valid, errors = order21_module.validate_fields(filled_fields)
    assert is_valid is True

    # Step 2: Check completeness
    score, missing = order21_module.check_completeness(filled_fields)
    assert score >= 0.7

    # Step 3: Calculate
    result = order21_module.calculate(filled_fields)
    assert result["total_costs"] > 0

    # Step 4: Generate arguments
    arguments = order21_module.get_arguments(result, filled_fields)
    assert "main_argument" in arguments

    # Step 5: Generate recommendations
    recommendations = order21_module.get_recommendations(result)
    assert len(recommendations) > 0


def test_module_can_be_registered(order21_module):
    """Test that module can provide all required interface methods"""
    # Test all ILegalModule methods exist and work
    assert order21_module.metadata is not None
    assert len(order21_module.get_tree_nodes()) > 0
    assert order21_module.get_tree_version() is not None
    assert len(order21_module.get_field_requirements()) > 0
    assert len(order21_module.get_question_templates()) > 0

    # Test validation methods
    valid, errors = order21_module.validate_fields({})
    assert isinstance(valid, bool)
    assert isinstance(errors, list)

    score, missing = order21_module.check_completeness({})
    assert isinstance(score, float)
    assert isinstance(missing, list)

    # Test calculation methods
    calc = order21_module.calculate(
        {"court_level": "High Court", "case_type": "summary_judgment", "claim_amount": 10000}
    )
    assert isinstance(calc, dict)

    args = order21_module.get_arguments(calc, {})
    assert isinstance(args, dict)

    recs = order21_module.get_recommendations(calc)
    assert isinstance(recs, list)
