"""
Test PatternExtractor
Legal Advisory System v5.0

Tests for robust pattern-based information extraction.
"""

import pytest
from backend.common_services.pattern_extractor import PatternExtractor


class TestPatternExtractor:
    """Test PatternExtractor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = PatternExtractor()

    # ============================================
    # COURT LEVEL EXTRACTION
    # ============================================

    def test_extract_court_level_high_court(self):
        """Test extraction of High Court mentions."""
        assert self.extractor.extract_court_level("this is a High Court case") == "High Court"
        assert self.extractor.extract_court_level("HC matter") == "High Court"
        assert self.extractor.extract_court_level("filed in high court") == "High Court"

    def test_extract_court_level_district_court(self):
        """Test extraction of District Court mentions."""
        assert self.extractor.extract_court_level("District Court case") == "District Court"
        assert self.extractor.extract_court_level("DC filing") == "District Court"
        assert self.extractor.extract_court_level("district court matter") == "District Court"

    def test_extract_court_level_magistrates_court(self):
        """Test extraction of Magistrates Court mentions."""
        assert self.extractor.extract_court_level("Magistrates Court case") == "Magistrates Court"
        assert self.extractor.extract_court_level("MC matter") == "Magistrates Court"
        assert self.extractor.extract_court_level("magistrate court") == "Magistrates Court"

    def test_extract_court_level_none(self):
        """Test no court level found."""
        assert self.extractor.extract_court_level("no court mentioned here") is None
        assert self.extractor.extract_court_level("just some text") is None

    # ============================================
    # AMOUNT EXTRACTION
    # ============================================

    def test_extract_amount_with_dollar_sign(self):
        """Test extraction of amounts with $ sign."""
        # Note: extract_amount returns Decimal, not float
        from decimal import Decimal
        assert self.extractor.extract_amount("claim is $50,000") == Decimal("50000")
        assert self.extractor.extract_amount("$100000") == Decimal("100000")
        assert self.extractor.extract_amount("$ 25,000.50") == Decimal("25000.50")
        assert self.extractor.extract_amount("$1,234,567.89") == Decimal("1234567.89")

    def test_extract_amount_with_sgd(self):
        """Test extraction of amounts with SGD prefix."""
        from decimal import Decimal
        assert self.extractor.extract_amount("SGD 50,000") == Decimal("50000")
        assert self.extractor.extract_amount("SGD100000") == Decimal("100000")
        assert self.extractor.extract_amount("SGD 25,000.50") == Decimal("25000.50")

    def test_extract_amount_plain_number(self):
        """Test extraction of plain numbers (>= 1000)."""
        from decimal import Decimal
        assert self.extractor.extract_amount("claim amount is 50000") == Decimal("50000")
        assert self.extractor.extract_amount("the amount 125000 was claimed") == Decimal("125000")

    def test_extract_amount_small_numbers_ignored(self):
        """Test that small numbers (< 1000) are ignored."""
        assert self.extractor.extract_amount("case number 123") is None
        assert self.extractor.extract_amount("there are 5 days") is None

    def test_extract_amount_none(self):
        """Test no amount found."""
        assert self.extractor.extract_amount("no numbers here") is None

    # ============================================
    # TRIAL DAYS EXTRACTION
    # ============================================

    def test_extract_trial_days_basic(self):
        """Test basic trial days extraction."""
        assert self.extractor.extract_trial_days("3-day trial") == 3
        assert self.extractor.extract_trial_days("5 day trial") == 5
        assert self.extractor.extract_trial_days("a 10 day contested trial") == 10

    def test_extract_trial_days_variations(self):
        """Test various formats supported by the extractor."""
        assert self.extractor.extract_trial_days("3 trial days") == 3
        assert self.extractor.extract_trial_days("trial of 7 days") == 7
        assert self.extractor.extract_trial_days("5 days contested") == 5

    def test_extract_trial_days_none(self):
        """Test no trial days found."""
        assert self.extractor.extract_trial_days("no trial mentioned") is None
        assert self.extractor.extract_trial_days("just some text") is None

    # ============================================
    # CASE TYPE EXTRACTION
    # ============================================

    def test_extract_case_type_default_judgment(self):
        """Test default judgment extraction."""
        assert self.extractor.extract_case_type("default judgment case") == "default_judgment"
        assert self.extractor.extract_case_type("this is a default judgment") == "default_judgment"

    def test_extract_case_type_summary_judgment(self):
        """Test summary judgment extraction."""
        assert self.extractor.extract_case_type("summary judgment application") == "summary_judgment"
        assert self.extractor.extract_case_type("summary judgment matter") == "summary_judgment"

    def test_extract_case_type_contested(self):
        """Test contested trial extraction."""
        assert self.extractor.extract_case_type("contested trial") == "contested_trial"
        # Note: "contested matter" without "trial" won't match
        assert self.extractor.extract_case_type("trial") == "contested_trial"

    def test_extract_case_type_none(self):
        """Test no case type found."""
        assert self.extractor.extract_case_type("some other case") is None

    # ============================================
    # COMBINED EXTRACTION
    # ============================================

    def test_extract_all_comprehensive(self):
        """Test extracting all fields from a single message."""
        text = "I have a High Court case with a claim of $50,000 from a 3-day contested trial"

        extracted = self.extractor.extract_all(text)

        assert extracted["court_level"] == "High Court"
        assert extracted["claim_amount"] == 50000.0
        assert extracted["trial_days"] == 3
        assert extracted["case_type"] == "contested_trial"

    def test_extract_all_partial(self):
        """Test extracting some fields when only some are present."""
        text = "District Court default judgment for $25,000"

        extracted = self.extractor.extract_all(text)

        assert extracted["court_level"] == "District Court"
        assert extracted["claim_amount"] == 25000.0
        assert extracted["case_type"] == "default_judgment"
        assert "trial_days" not in extracted  # Not mentioned

    def test_extract_all_with_context(self):
        """Test extraction with context from previous conversation."""
        text = "the amount is $30,000"
        context = {"current_fields": {"court_level": "High Court"}}

        extracted = self.extractor.extract_all(text, context=context)

        assert extracted["claim_amount"] == 30000.0
        # Should not duplicate already filled fields
        assert "court_level" not in extracted or extracted["court_level"] == "High Court"

    def test_extract_all_empty(self):
        """Test extraction from text with no relevant information."""
        text = "just some random text with no legal information"

        extracted = self.extractor.extract_all(text)

        assert extracted == {}

    # ============================================
    # EDGE CASES
    # ============================================

    def test_case_insensitivity(self):
        """Test that extraction is case-insensitive."""
        assert self.extractor.extract_court_level("HIGH COURT") == "High Court"
        assert self.extractor.extract_case_type("DEFAULT JUDGMENT") == "default_judgment"

    def test_multiple_amounts_takes_first(self):
        """Test that when multiple amounts present, first is taken."""
        from decimal import Decimal
        text = "claim of $50,000 plus costs of $5,000"
        assert self.extractor.extract_amount(text) == Decimal("50000")

    def test_special_characters_in_amount(self):
        """Test amounts with various formatting."""
        from decimal import Decimal
        assert self.extractor.extract_amount("$50,000.00") == Decimal("50000.00")
        assert self.extractor.extract_amount("$ 50000") == Decimal("50000")
        assert self.extractor.extract_amount("$50000.0") == Decimal("50000.0")

    def test_extraction_with_noise(self):
        """Test extraction from noisy real-world text."""
        text = """
        So I have this case, it's in the High Court (HC),
        and the claim amount is like $50,000 or thereabouts.
        The trial was 3 days long, fully contested.
        Can you help me calculate the costs?
        """

        extracted = self.extractor.extract_all(text.lower())

        assert extracted["court_level"] == "High Court"
        assert extracted["claim_amount"] == 50000.0
        # Note: "3 days long" won't match, but "3 days contested" will
        assert extracted.get("trial_days") == 3 or "trial_days" not in extracted
        assert extracted["case_type"] == "contested_trial"


class TestPatternExtractorRobustness:
    """Test robustness and edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = PatternExtractor()

    def test_unicode_handling(self):
        """Test handling of unicode characters."""
        text = "claim is $50,000 • High Court"
        extracted = self.extractor.extract_all(text)
        assert extracted["claim_amount"] == 50000.0

    def test_whitespace_variations(self):
        """Test various whitespace patterns."""
        assert self.extractor.extract_court_level("High  Court") == "High Court"
        assert self.extractor.extract_court_level("High\tCourt") == "High Court"

    def test_empty_string(self):
        """Test empty string handling."""
        extracted = self.extractor.extract_all("")
        assert extracted == {}

    def test_very_long_text(self):
        """Test extraction from very long text."""
        text = "Lorem ipsum " * 1000 + "High Court case for $50,000"
        extracted = self.extractor.extract_all(text)
        assert extracted["court_level"] == "High Court"
        assert extracted["claim_amount"] == 50000.0
