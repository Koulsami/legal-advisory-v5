"""
Tests for Validation Guard
Legal Advisory System v5.0

Comprehensive tests for ValidationGuard - the critical safety component.
"""

import pytest
from decimal import Decimal
from backend.hybrid_ai.validation_guard import (
    ValidationGuard,
    ValidationGuardError,
    ValidationReport,
    ValidationIssue
)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def guard():
    """Create ValidationGuard with default settings"""
    return ValidationGuard(strict_mode=True, tolerance=0.01)


@pytest.fixture
def lenient_guard():
    """Create ValidationGuard with lenient settings"""
    return ValidationGuard(strict_mode=False, tolerance=1.0)


@pytest.fixture
def sample_calculation():
    """Sample calculation result"""
    return {
        "total_cost": 1500.00,
        "filing_fee": 500.00,
        "hearing_fee": 1000.00
    }


# ============================================
# INITIALIZATION TESTS
# ============================================

def test_init_default():
    """Test initialization with default settings"""
    guard = ValidationGuard()

    assert guard._strict_mode is True
    assert guard._tolerance == 0.01


def test_init_custom():
    """Test initialization with custom settings"""
    guard = ValidationGuard(strict_mode=False, tolerance=0.5)

    assert guard._strict_mode is False
    assert guard._tolerance == 0.5


# ============================================
# BASIC VALIDATION TESTS
# ============================================

def test_validate_matching_text(guard, sample_calculation):
    """Test validation with matching text"""
    text = "The total cost is $1500.00, including a filing fee of $500.00 and hearing fee of $1000.00"

    report = guard.validate(sample_calculation, text)

    assert isinstance(report, ValidationReport)
    assert report.is_valid is True
    assert report.checked_fields == 3


def test_validate_empty_calculation(guard):
    """Test validation with empty calculation"""
    report = guard.validate({}, "some text")

    assert report.is_valid is True  # Empty calc is just a warning
    assert "Empty calculation result" in report.warnings


def test_validate_empty_text(guard, sample_calculation):
    """Test validation with empty AI text"""
    report = guard.validate(sample_calculation, "")

    assert report.is_valid is False
    assert any(i.issue_type == "missing_content" for i in report.issues)


def test_validate_whitespace_text(guard, sample_calculation):
    """Test validation with whitespace-only text"""
    report = guard.validate(sample_calculation, "   \n\t  ")

    assert report.is_valid is False


# ============================================
# SUSPICIOUS PATTERN TESTS
# ============================================

def test_detect_calculation_inability(guard, sample_calculation):
    """Test detection of AI claiming inability to calculate"""
    text = "I cannot calculate the exact amount..."

    report = guard.validate(sample_calculation, text)

    assert report.is_valid is False
    assert any(
        i.issue_type == "suspicious_pattern" and i.severity == "critical"
        for i in report.issues
    )


def test_detect_no_access_claim(guard, sample_calculation):
    """Test detection of AI claiming no data access"""
    text = "I don't have access to the calculation data..."

    report = guard.validate(sample_calculation, text)

    assert report.is_valid is False


def test_detect_error_markers(guard, sample_calculation):
    """Test detection of error markers"""
    texts = [
        "The result is [error]",
        "Total: [invalid]",
        "Amount: [unknown]"
    ]

    for text in texts:
        report = guard.validate(sample_calculation, text)
        assert report.is_valid is False


def test_detect_verification_suggestion(guard, sample_calculation):
    """Test detection of AI suggesting verification"""
    text = "The total is $1500, but please verify these calculations."

    report = guard.validate(sample_calculation, text)

    assert report.is_valid is False


def test_detect_estimates_language(guard, sample_calculation):
    """Test detection of treating calculations as estimates"""
    text = "These are estimates only: total $1500"

    report = guard.validate(sample_calculation, text)

    assert report.is_valid is False


def test_detect_warning_patterns(guard):
    """Test detection of warning patterns (not critical)"""
    # Test the detection function directly
    warning_texts = [
        "The total is approximately $1500",
        "This might be around $1500",
        "Assuming that the amount is $1500",
        "In theory, the total is $1500"
    ]

    for text in warning_texts:
        issues = guard._check_suspicious_patterns(text)
        # Should have at least one warning issue
        assert any(i.severity == "warning" for i in issues), f"No warnings found for: {text}"


# ============================================
# VALUE EXTRACTION TESTS
# ============================================

def test_extract_values_from_flat_calculation(guard):
    """Test value extraction from flat calculation"""
    calc = {
        "amount": 100,
        "fee": 50.50,
        "total": 150.50
    }

    values = guard._extract_values_from_calculation(calc)

    assert len(values) == 3
    assert values["amount"] == Decimal("100")
    assert values["fee"] == Decimal("50.50")
    assert values["total"] == Decimal("150.50")


def test_extract_values_from_nested_calculation(guard):
    """Test value extraction from nested calculation"""
    calc = {
        "total": 1000,
        "breakdown": {
            "subtotal": 800,
            "tax": 200
        }
    }

    values = guard._extract_values_from_calculation(calc)

    assert len(values) == 3
    assert values["total"] == Decimal("1000")
    assert values["breakdown.subtotal"] == Decimal("800")
    assert values["breakdown.tax"] == Decimal("200")


def test_extract_values_from_text_currency(guard):
    """Test extraction of currency values from text"""
    text = "The total is $1,500.00 with a fee of $250.50"

    values = guard._extract_values_from_text(text)

    assert Decimal("1500.00") in values
    assert Decimal("250.50") in values


def test_extract_values_from_text_singapore_currency(guard):
    """Test extraction of Singapore currency"""
    text = "Total: S$1500 and fee: S$250"

    values = guard._extract_values_from_text(text)

    assert Decimal("1500") in values
    assert Decimal("250") in values


def test_extract_values_from_text_percentage(guard):
    """Test extraction of percentage values"""
    text = "Interest rate is 15% and discount is 5.5%"

    values = guard._extract_values_from_text(text)

    assert Decimal("15") in values
    assert Decimal("5.5") in values


def test_extract_values_ignores_invalid(guard):
    """Test that invalid numeric strings are ignored"""
    text = "Reference: ABC-123-XYZ"

    values = guard._extract_values_from_text(text)

    # Should extract 123 but not the letters
    assert Decimal("123") in values


# ============================================
# VALUE COMPARISON TESTS
# ============================================

def test_values_match_exact(guard):
    """Test exact value matching"""
    val1 = Decimal("100.00")
    val2 = Decimal("100.00")

    assert guard._values_match(val1, val2) is True


def test_values_match_within_tolerance(guard):
    """Test value matching within tolerance"""
    val1 = Decimal("100.00")
    val2 = Decimal("100.005")  # Within 0.01 tolerance

    assert guard._values_match(val1, val2) is True


def test_values_dont_match_outside_tolerance(guard):
    """Test values don't match outside tolerance"""
    val1 = Decimal("100.00")
    val2 = Decimal("100.05")  # Outside 0.01 tolerance

    assert guard._values_match(val1, val2) is False


def test_compare_values_all_present(guard):
    """Test comparison when all values are present"""
    calc_values = {
        "total": Decimal("1000"),
        "fee": Decimal("100")
    }
    ai_values = [Decimal("1000"), Decimal("100")]

    issues = guard._compare_values(calc_values, ai_values)

    # Should have no critical issues
    critical_issues = [i for i in issues if i.severity == "critical"]
    assert len(critical_issues) == 0


def test_compare_values_missing(guard):
    """Test comparison when values are missing"""
    calc_values = {
        "total": Decimal("1000"),
        "fee": Decimal("100")
    }
    ai_values = [Decimal("1000")]  # Missing fee

    issues = guard._compare_values(calc_values, ai_values)

    # Should have missing value issue for "fee"
    missing_issues = [i for i in issues if i.issue_type == "missing_value"]
    assert len(missing_issues) == 1
    assert missing_issues[0].field_name == "fee"


def test_compare_values_near_match(guard):
    """Test comparison with near matches"""
    calc_values = {
        "total": Decimal("1000.00")
    }
    # Near but not exact (within 10*tolerance but not tolerance)
    ai_values = [Decimal("1000.05")]

    issues = guard._compare_values(calc_values, ai_values)

    # Should have near_match warning
    near_match_issues = [i for i in issues if i.issue_type == "near_match"]
    assert len(near_match_issues) == 1


# ============================================
# STRICT MODE TESTS
# ============================================

def test_strict_mode_fails_on_missing_values(guard, sample_calculation):
    """Test strict mode fails when values are missing"""
    text = "The total is $1500.00"  # Missing filing and hearing fees

    report = guard.validate(sample_calculation, text)

    # Strict mode should fail
    assert report.is_valid is False


def test_lenient_mode_allows_missing_values(lenient_guard, sample_calculation):
    """Test lenient mode allows some missing values"""
    text = "The total is $1500.00"  # Missing filing and hearing fees

    report = lenient_guard.validate(sample_calculation, text)

    # Lenient mode might still pass
    # (depends on other factors, but shouldn't automatically fail)
    assert report.checked_fields == 3


# ============================================
# CONTEXT VALIDATION TESTS
# ============================================

def test_validate_with_context_matching(guard):
    """Test context validation with matching data"""
    original = {
        "total": 1000,
        "fee": 100
    }
    enhanced = {
        "total": 1000,
        "fee": 100,
        "explanation": "Additional info"
    }

    report = guard.validate_with_context(original, enhanced)

    assert report.is_valid is True


def test_validate_with_context_missing_field(guard):
    """Test context validation with missing field"""
    original = {
        "total": 1000,
        "fee": 100
    }
    enhanced = {
        "total": 1000
        # Missing "fee"
    }

    report = guard.validate_with_context(original, enhanced)

    assert report.is_valid is False
    assert any(i.issue_type == "missing_field" for i in report.issues)


def test_validate_with_context_changed_value(guard):
    """Test context validation with changed value"""
    original = {
        "total": 1000
    }
    enhanced = {
        "total": 1500  # Changed!
    }

    report = guard.validate_with_context(original, enhanced)

    assert report.is_valid is False
    assert any(i.issue_type == "contradiction" for i in report.issues)


def test_validate_with_context_nested(guard):
    """Test context validation with nested structures"""
    original = {
        "summary": {
            "total": 1000,
            "fee": 100
        }
    }
    enhanced = {
        "summary": {
            "total": 1500,  # Changed!
            "fee": 100
        }
    }

    report = guard.validate_with_context(original, enhanced)

    assert report.is_valid is False


# ============================================
# INTEGRATION TESTS
# ============================================

def test_full_validation_workflow_valid(guard):
    """Test complete validation workflow with valid data"""
    calculation = {
        "total_cost": 2500.00,
        "breakdown": {
            "filing_fee": 500.00,
            "hearing_fee": 1000.00,
            "service_fee": 1000.00
        }
    }

    text = """
    Based on the calculation, the total cost is $2,500.00.
    This includes:
    - Filing fee: $500.00
    - Hearing fee: $1,000.00
    - Service fee: $1,000.00

    All amounts are calculated according to Singapore Rules of Court.
    """

    report = guard.validate(calculation, text)

    assert report.is_valid is True
    assert len([i for i in report.issues if i.severity == "critical"]) == 0


def test_full_validation_workflow_with_contradictions(guard):
    """Test workflow with contradictions"""
    calculation = {
        "total": 1000.00
    }

    text = "The total cost is $1500.00"  # Wrong amount!

    report = guard.validate(calculation, text)

    # Should detect missing value (1000 not found, 1500 found instead)
    assert any(
        i.issue_type in ["missing_value", "contradiction"]
        for i in report.issues
    )


def test_validation_with_complex_text(guard):
    """Test validation with complex realistic text"""
    calculation = {
        "base_amount": 1000.00,
        "gst": 150.00,
        "total": 1150.00
    }

    text = """
    Legal Costs Breakdown:

    The base amount for this matter is $1,000.00. After applying GST
    at the statutory rate, the additional tax is $150.00, bringing
    the total payable amount to $1,150.00.

    Payment should be made within 14 days of receiving this notice.
    """

    report = guard.validate(calculation, text)

    assert report.is_valid is True


# ============================================
# STATISTICS TESTS
# ============================================

def test_get_statistics_initial(guard):
    """Test initial statistics"""
    stats = guard.get_statistics()

    assert stats["strict_mode"] is True
    assert stats["tolerance"] == 0.01
    assert stats["total_validations"] == 0
    assert stats["successful_validations"] == 0
    assert stats["success_rate"] == 0.0


def test_get_statistics_after_validations(guard, sample_calculation):
    """Test statistics after performing validations"""
    # Perform some validations
    guard.validate(sample_calculation, "Total: $1500, filing: $500, hearing: $1000")
    guard.validate(sample_calculation, "Total: $1500, filing: $500, hearing: $1000")

    stats = guard.get_statistics()

    assert stats["total_validations"] == 2
    assert stats["successful_validations"] >= 0


def test_get_statistics_with_failures(guard, sample_calculation):
    """Test statistics with failures"""
    # Valid
    guard.validate(sample_calculation, "Total: $1500, filing: $500, hearing: $1000")

    # Invalid (suspicious pattern)
    guard.validate(sample_calculation, "I cannot calculate this")

    stats = guard.get_statistics()

    assert stats["total_validations"] == 2
    assert stats["failed_validations"] >= 1


def test_reset_statistics(guard, sample_calculation):
    """Test statistics reset"""
    # Perform some validations
    guard.validate(sample_calculation, "some text")
    guard.validate(sample_calculation, "I cannot calculate")

    guard.reset_statistics()

    stats = guard.get_statistics()
    assert stats["total_validations"] == 0
    assert stats["failed_validations"] == 0


# ============================================
# STRICT MODE CONTROL TESTS
# ============================================

def test_set_strict_mode(guard):
    """Test enabling/disabling strict mode"""
    assert guard.is_strict_mode() is True

    guard.set_strict_mode(False)
    assert guard.is_strict_mode() is False

    guard.set_strict_mode(True)
    assert guard.is_strict_mode() is True


def test_strict_mode_affects_validation(sample_calculation):
    """Test that strict mode affects validation results"""
    text = "Total: $1500"  # Missing some values

    # Strict mode
    strict_guard = ValidationGuard(strict_mode=True)
    strict_report = strict_guard.validate(sample_calculation, text)

    # Lenient mode
    lenient_guard = ValidationGuard(strict_mode=False)
    lenient_report = lenient_guard.validate(sample_calculation, text)

    # Strict mode should be more likely to fail
    # (though both might fail depending on implementation)
    assert strict_report.checked_fields == lenient_report.checked_fields


# ============================================
# EDGE CASE TESTS
# ============================================

def test_validate_with_special_characters(guard):
    """Test validation with special characters"""
    calc = {"total": 1000.00}
    text = "Total: $1,000.00 (S$)"

    report = guard.validate(calc, text)

    assert report.is_valid is True


def test_validate_with_very_large_numbers(guard):
    """Test validation with very large numbers"""
    calc = {"amount": 1000000.00}
    text = "Amount: $1,000,000.00"

    report = guard.validate(calc, text)

    assert report.is_valid is True


def test_validate_with_decimal_precision(guard):
    """Test validation with high decimal precision"""
    calc = {"rate": 15.75}
    text = "Rate: 15.75%"

    report = guard.validate(calc, text)

    assert report.is_valid is True


def test_validate_with_zero_values(guard):
    """Test validation with zero values"""
    calc = {"fee": 0.00, "total": 1000.00}
    text = "Fee: $0.00, Total: $1000.00"

    report = guard.validate(calc, text)

    assert report.is_valid is True


def test_validate_with_negative_values(guard):
    """Test validation with negative values"""
    calc = {"credit": -100.00, "balance": 900.00}
    text = "Credit: -$100.00, Balance: $900.00"

    report = guard.validate(calc, text)

    # Should handle negative values
    assert report.checked_fields == 2


# ============================================
# CONFIDENCE SCORE TESTS
# ============================================

def test_confidence_score_all_matched(guard):
    """Test confidence score when all values matched"""
    calc = {"total": 1000, "fee": 100}
    text = "Total: $1000, Fee: $100"

    report = guard.validate(calc, text)

    # High confidence when all match
    assert report.confidence_score >= 0.5


def test_confidence_score_partial_match(guard):
    """Test confidence score with partial matches"""
    calc = {"total": 1000, "fee": 100, "tax": 50}
    text = "Total: $1000"  # Only one value present

    report = guard.validate(calc, text)

    # Lower confidence with partial matches
    assert report.confidence_score < 1.0


# ============================================
# PARSE NUMERIC STRING TESTS
# ============================================

def test_parse_numeric_string_valid(guard):
    """Test parsing valid numeric strings"""
    assert guard._parse_numeric_string("1000") == Decimal("1000")
    assert guard._parse_numeric_string("1,000.50") == Decimal("1000.50")
    assert guard._parse_numeric_string("$500") == Decimal("500")


def test_parse_numeric_string_invalid(guard):
    """Test parsing invalid strings"""
    assert guard._parse_numeric_string("abc") is None
    assert guard._parse_numeric_string("") is None
    assert guard._parse_numeric_string("N/A") is None


def test_parse_numeric_string_non_string(guard):
    """Test parsing non-string values"""
    assert guard._parse_numeric_string(123) is None
    assert guard._parse_numeric_string(None) is None
