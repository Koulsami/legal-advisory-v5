"""
Pattern-Based Information Extractor
Legal Advisory System v5.0

Extracts structured information from natural language using regex patterns.
This runs BEFORE AI extraction to catch obvious patterns reliably.
"""

import re
from typing import Dict, Optional, Any
from decimal import Decimal


class PatternExtractor:
    """
    Extracts legal information from natural language using pattern matching.

    More reliable than AI for common patterns:
    - Court levels
    - Case types
    - Monetary amounts
    - Trial durations
    - Claim types (liquidated/unliquidated)
    """

    # Court level patterns
    COURT_PATTERNS = {
        "High Court": r'\b(high\s*court|hc)\b',
        "District Court": r'\b(district\s*court|dc)\b',
        "Magistrates Court": r'\b(magistrates?\s*court|mc)\b',
    }

    # Case type patterns
    CASE_TYPE_PATTERNS = {
        "default_judgment": r'\bdefault\s*judgment\b',
        "summary_judgment": r'\bsummary\s*judgment\b',
        "contested_trial": r'\bcontested\s*trial\b|\btrial\b',
        "assessment_of_damages": r'\bassessment\s*of\s*damages\b',
    }

    # Liquidated/Unliquidated patterns
    CLAIM_NATURE_PATTERNS = {
        "liquidated": r'\bliquidated\b',
        "unliquidated": r'\bunliquidated\b',
    }

    # Amount patterns (SGD, $, etc.)
    AMOUNT_PATTERNS = [
        r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $50,000 or $50000.00
        r'SGD\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # SGD 50,000
        r'(?:SGD|S\$)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # S$ 50,000
        r'\b(\d+(?:,\d{3})*)\s*(?:dollars?|sgd)\b',  # 50,000 dollars
        r'\b(\d{4,})\b',  # Plain numbers >= 1000 (likely amounts)
    ]

    # Trial duration patterns
    TRIAL_DAYS_PATTERNS = [
        r'(\d+)\s*[-]?\s*days?\s*(?:contested\s*)?trial',  # 3-day trial, 3 day trial
        r'trial\s*[,.]?\s*(\d+)\s*days?',  # trial, 3 days or trial 3 days
        r'contested\s*trial\s*[,.]?\s*(\d+)\s*days?',  # contested trial, 3 days
        r'(\d+)\s*trial\s*days?',  # 3 trial days
        r'trial\s*(?:of\s*|for\s*)?(\d+)\s*days?',  # trial of 3 days / trial for 3 days
        r'(\d+)\s*days?\s*(?:of\s*)?(?:contested\s*)?trial',  # 3 days of contested trial
        r'(\d+)\s*days?\s*contested',  # 3 days contested
    ]

    # ADR refusal patterns
    ADR_REFUSAL_PATTERNS = [
        r'\brefused\s*(?:to\s*participate\s*in\s*)?(?:adr|mediation|arbitration)',
        r'\b(?:adr|mediation|arbitration)\s*(?:was\s*)?refused',
        r'\brejected\s*(?:adr|mediation|arbitration)',
        r'\b(?:adr|mediation|arbitration)\s*(?:was\s*)?rejected',
        r'\bdeclined\s*(?:adr|mediation|arbitration)',
        r'\brefused\s*(?:mediation|arbitration|adr)',
    ]

    def __init__(self):
        """Initialize pattern extractor."""
        pass

    def extract_all(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract all possible information from text.

        Args:
            text: User message text
            context: Optional context (current field values)

        Returns:
            Dictionary of extracted field values
        """
        text_lower = text.lower()
        extracted = {}

        # Extract court level
        court = self.extract_court_level(text_lower)
        if court:
            extracted["court_level"] = court

        # Extract case type
        case_type = self.extract_case_type(text_lower)
        if case_type:
            extracted["case_type"] = case_type

        # Extract claim nature (liquidated/unliquidated)
        claim_nature = self.extract_claim_nature(text_lower)
        if claim_nature:
            extracted["claim_nature"] = claim_nature

        # Extract claim amount
        amount = self.extract_amount(text)
        if amount:
            extracted["claim_amount"] = float(amount)

        # Extract trial days
        trial_days = self.extract_trial_days(text_lower)
        if trial_days:
            extracted["trial_days"] = int(trial_days)

        # Extract ADR refusal
        adr_refused = self.extract_adr_refusal(text_lower)
        if adr_refused:
            extracted["adr_refused"] = True

        return extracted

    def extract_court_level(self, text: str) -> Optional[str]:
        """
        Extract court level from text.

        Args:
            text: Lowercase text

        Returns:
            Court level or None
        """
        for court, pattern in self.COURT_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return court
        return None

    def extract_case_type(self, text: str) -> Optional[str]:
        """
        Extract case type from text.

        Args:
            text: Lowercase text

        Returns:
            Case type or None
        """
        for case_type, pattern in self.CASE_TYPE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                # Special handling: if text contains "default", prioritize it
                if "default" in text and case_type == "default_judgment":
                    return case_type
                # Don't match "trial" alone if "default" or "summary" is present
                if case_type == "contested_trial":
                    if "default" in text or "summary" in text:
                        continue
                return case_type
        return None

    def extract_claim_nature(self, text: str) -> Optional[str]:
        """
        Extract claim nature (liquidated/unliquidated).

        Args:
            text: Lowercase text

        Returns:
            "liquidated" or "unliquidated" or None
        """
        for nature, pattern in self.CLAIM_NATURE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return nature
        return None

    def extract_amount(self, text: str) -> Optional[Decimal]:
        """
        Extract monetary amount from text.

        Args:
            text: Text (preserve case for numbers)

        Returns:
            Decimal amount or None
        """
        for pattern in self.AMOUNT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get the number, remove commas
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = Decimal(amount_str)
                    # Sanity check: legal claims are usually between 1,000 and 10,000,000
                    if 100 <= amount <= 100000000:
                        return amount
                except (ValueError, IndexError):
                    continue
        return None

    def extract_trial_days(self, text: str) -> Optional[int]:
        """
        Extract trial duration in days.

        Args:
            text: Lowercase text

        Returns:
            Number of days or None
        """
        for pattern in self.TRIAL_DAYS_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    days = int(match.group(1))
                    # Sanity check: trials are usually 1-100 days
                    if 1 <= days <= 100:
                        return days
                except (ValueError, IndexError):
                    continue
        return None

    def extract_adr_refusal(self, text: str) -> bool:
        """
        Extract ADR refusal indicator.

        Args:
            text: Lowercase text

        Returns:
            True if ADR refusal detected, False otherwise
        """
        for pattern in self.ADR_REFUSAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def extract_field(self, field_name: str, text: str) -> Optional[Any]:
        """
        Extract specific field from text.

        Args:
            field_name: Name of field to extract
            text: User message text

        Returns:
            Extracted value or None
        """
        text_lower = text.lower()

        if field_name == "court_level":
            return self.extract_court_level(text_lower)
        elif field_name == "case_type":
            return self.extract_case_type(text_lower)
        elif field_name == "claim_nature":
            return self.extract_claim_nature(text_lower)
        elif field_name == "claim_amount":
            amount = self.extract_amount(text)
            return float(amount) if amount else None
        elif field_name == "trial_days":
            return self.extract_trial_days(text_lower)
        elif field_name == "adr_refused":
            return self.extract_adr_refusal(text_lower)

        return None
