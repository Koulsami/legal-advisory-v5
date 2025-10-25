"""
AI Validation Guard
Legal Advisory System v5.0

Validates that AI-enhanced responses don't contradict calculation results.
This is a CRITICAL safety component of the hybrid AI architecture.

CRITICAL PRINCIPLE: AI must NEVER contradict calculations. This guard
ensures that principle is enforced.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Represents a validation issue found"""
    issue_type: str  # "contradiction", "missing_value", "suspicious_pattern"
    severity: str  # "critical", "warning", "info"
    description: str
    field_name: Optional[str] = None
    expected_value: Optional[Any] = None
    found_value: Optional[Any] = None
    location: Optional[str] = None


@dataclass
class ValidationReport:
    """Complete validation report"""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checked_fields: int = 0
    matched_fields: int = 0
    confidence_score: float = 1.0


class ValidationGuardError(Exception):
    """Exception raised for validation guard errors"""
    pass


class ValidationGuard:
    """
    Validates AI-enhanced responses against calculation results.

    This is a critical safety component that ensures AI never contradicts
    or modifies the original calculation results.

    Key Features:
    - Numeric value extraction and comparison
    - Contradiction detection
    - Suspicious pattern detection
    - Detailed validation reports
    - Configurable strictness

    Example:
        >>> guard = ValidationGuard(strict_mode=True)
        >>> calculation = {"total_cost": 1500.00, "filing_fee": 500.00}
        >>> ai_text = "The total cost is $1500.00 with a filing fee of $500.00"
        >>> report = guard.validate(calculation, ai_text)
        >>> assert report.is_valid is True
    """

    def __init__(
        self,
        strict_mode: bool = True,
        tolerance: float = 0.01
    ):
        """
        Initialize Validation Guard.

        Args:
            strict_mode: If True, any discrepancy fails validation
            tolerance: Tolerance for numeric comparisons (default: 0.01)
        """
        self._strict_mode = strict_mode
        self._tolerance = tolerance

        # Statistics
        self._validation_count = 0
        self._validation_failures = 0
        self._contradictions_found = 0

        logger.info(
            f"ValidationGuard initialized "
            f"(strict_mode: {strict_mode}, tolerance: {tolerance})"
        )

    def validate(
        self,
        calculation_result: Dict[str, Any],
        ai_enhanced_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationReport:
        """
        Validate AI-enhanced text against calculation results.

        This is the main validation method. It:
        1. Extracts all numeric values from both calculation and AI text
        2. Compares values to detect contradictions
        3. Checks for suspicious patterns
        4. Generates comprehensive validation report

        Args:
            calculation_result: Original calculation results
            ai_enhanced_text: AI-generated text to validate
            context: Optional context for validation

        Returns:
            ValidationReport with validation results

        Example:
            >>> calc = {"total": 1000, "subtotal": 800, "tax": 200}
            >>> text = "Total is $1000 (subtotal $800 + tax $200)"
            >>> report = guard.validate(calc, text)
            >>> assert report.is_valid is True
        """
        self._validation_count += 1

        report = ValidationReport(
            is_valid=True,
            issues=[],
            warnings=[],
            checked_fields=0,
            matched_fields=0,
            confidence_score=1.0
        )

        # Basic validation
        if not calculation_result:
            report.warnings.append("Empty calculation result")
            report.confidence_score = 0.5
            return report

        if not ai_enhanced_text or not ai_enhanced_text.strip():
            report.is_valid = False
            report.issues.append(ValidationIssue(
                issue_type="missing_content",
                severity="critical",
                description="AI text is empty"
            ))
            return report

        # Step 1: Check for suspicious patterns
        suspicious_issues = self._check_suspicious_patterns(ai_enhanced_text)
        if suspicious_issues:
            report.issues.extend(suspicious_issues)
            if self._strict_mode and any(i.severity == "critical" for i in suspicious_issues):
                report.is_valid = False
                self._validation_failures += 1
                return report

        # Step 2: Extract and compare numeric values
        calc_values = self._extract_values_from_calculation(calculation_result)
        ai_values = self._extract_values_from_text(ai_enhanced_text)

        report.checked_fields = len(calc_values)

        # Step 3: Compare values
        comparison_issues = self._compare_values(calc_values, ai_values)
        if comparison_issues:
            report.issues.extend(comparison_issues)
            self._contradictions_found += len([
                i for i in comparison_issues if i.issue_type == "contradiction"
            ])

            # Critical contradictions fail validation
            critical_issues = [i for i in comparison_issues if i.severity == "critical"]
            if critical_issues:
                report.is_valid = False
                self._validation_failures += 1

        # Step 4: Calculate confidence score
        if calc_values:
            # Count how many calculation values were found in AI text
            matched = 0
            for calc_val in calc_values.values():
                for ai_val in ai_values:
                    if self._values_match(calc_val, ai_val):
                        matched += 1
                        break

            report.matched_fields = matched
            report.confidence_score = matched / len(calc_values) if len(calc_values) > 0 else 0.0
        else:
            report.confidence_score = 1.0 if not report.issues else 0.5

        # Step 5: Add warnings for missing values
        if len(calc_values) > len(ai_values):
            report.warnings.append(
                f"Some calculation values not found in AI text "
                f"({len(calc_values)} expected, {len(ai_values)} found)"
            )

        logger.info(
            f"Validation complete: valid={report.is_valid}, "
            f"issues={len(report.issues)}, confidence={report.confidence_score:.2f}"
        )

        return report

    def _check_suspicious_patterns(self, text: str) -> List[ValidationIssue]:
        """
        Check for suspicious patterns in AI text.

        Patterns that indicate potential problems:
        - Disclaimers about inability to calculate
        - References to hypothetical scenarios
        - Statements about changing calculations
        - Apologies or uncertainty markers

        Args:
            text: AI-generated text

        Returns:
            List of ValidationIssue objects
        """
        issues = []
        text_lower = text.lower()

        # Critical patterns (complete failures)
        critical_patterns = [
            (r"i\s+(cannot|can't|couldn't)\s+calculate", "AI claims inability to calculate"),
            (r"i\s+(don't|do not)\s+have\s+access", "AI claims lack of access to data"),
            (r"\[error\]|\[invalid\]|\[unknown\]", "Error markers in text"),
            (r"please\s+verify\s+these\s+calculations", "AI suggests verification needed"),
            (r"these\s+are\s+estimates?\s+only", "AI treating calculations as estimates"),
        ]

        for pattern, description in critical_patterns:
            if re.search(pattern, text_lower):
                issues.append(ValidationIssue(
                    issue_type="suspicious_pattern",
                    severity="critical",
                    description=description,
                    location=pattern
                ))

        # Warning patterns (potential issues)
        warning_patterns = [
            (r"approximately|roughly|about", "Imprecise language for calculations"),
            (r"may\s+be|might\s+be|could\s+be", "Uncertainty markers"),
            (r"assuming\s+that|if\s+we\s+assume", "Hypothetical scenarios"),
            (r"in\s+theory|theoretically", "Theoretical language"),
        ]

        for pattern, description in warning_patterns:
            if re.search(pattern, text_lower):
                issues.append(ValidationIssue(
                    issue_type="suspicious_pattern",
                    severity="warning",
                    description=description,
                    location=pattern
                ))

        return issues

    def _extract_values_from_calculation(
        self,
        calculation: Dict[str, Any],
        prefix: str = ""
    ) -> Dict[str, Decimal]:
        """
        Extract all numeric values from calculation result.

        Handles nested dictionaries recursively.

        Args:
            calculation: Calculation result dictionary
            prefix: Prefix for nested keys

        Returns:
            Dictionary mapping field names to Decimal values
        """
        values = {}

        for key, value in calculation.items():
            full_key = f"{prefix}{key}" if prefix else key

            if isinstance(value, dict):
                # Recursively extract from nested dict
                nested_values = self._extract_values_from_calculation(
                    value,
                    prefix=f"{full_key}."
                )
                values.update(nested_values)
            elif isinstance(value, (int, float, Decimal)):
                # Convert to Decimal for precise comparison
                values[full_key] = Decimal(str(value))
            elif isinstance(value, str):
                # Try to parse numeric strings
                numeric_value = self._parse_numeric_string(value)
                if numeric_value is not None:
                    values[full_key] = numeric_value

        return values

    def _extract_values_from_text(self, text: str) -> List[Decimal]:
        """
        Extract all numeric values from AI text.

        Handles various formats:
        - Currency: $1,500.00 or S$1500.00
        - Plain numbers: 1500.00 or 1,500
        - Percentages: 15% (converted to decimal)

        Args:
            text: AI-generated text

        Returns:
            List of Decimal values found in text
        """
        values = []

        # Pattern for currency values: $1,500.00 or S$1500.00
        currency_pattern = r'(?:S?\$\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)'

        # Pattern for percentage values: 15% or 15.5%
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*%'

        # Find all currency values
        for match in re.finditer(currency_pattern, text):
            value_str = match.group(1).replace(',', '')
            try:
                values.append(Decimal(value_str))
            except (ValueError, TypeError):
                pass

        # Find all percentage values
        for match in re.finditer(percentage_pattern, text):
            value_str = match.group(1)
            try:
                # Convert percentage to decimal
                values.append(Decimal(value_str))
            except (ValueError, TypeError):
                pass

        return values

    def _parse_numeric_string(self, value: str) -> Optional[Decimal]:
        """
        Try to parse a string as a numeric value.

        Args:
            value: String to parse

        Returns:
            Decimal value if parseable, None otherwise
        """
        if not isinstance(value, str):
            return None

        # Remove currency symbols and commas
        cleaned = value.replace('$', '').replace(',', '').strip()

        try:
            return Decimal(cleaned)
        except (ValueError, TypeError, Exception):
            return None

    def _compare_values(
        self,
        calc_values: Dict[str, Decimal],
        ai_values: List[Decimal]
    ) -> List[ValidationIssue]:
        """
        Compare calculation values with AI text values.

        Args:
            calc_values: Dictionary of calculation values
            ai_values: List of values found in AI text

        Returns:
            List of ValidationIssue objects
        """
        issues = []

        # Convert AI values list to set for efficient lookup
        ai_values_set = set(ai_values)

        for field_name, calc_value in calc_values.items():
            # Check if calculation value appears in AI text
            found_match = False

            for ai_value in ai_values_set:
                if self._values_match(calc_value, ai_value):
                    found_match = True
                    break

            if not found_match:
                # Check if there's a close match (within tolerance)
                close_matches = [
                    ai_val for ai_val in ai_values_set
                    if abs(float(calc_value - ai_val)) < 10 * self._tolerance
                ]

                if close_matches:
                    # Found close but not exact match - warning
                    issues.append(ValidationIssue(
                        issue_type="near_match",
                        severity="warning",
                        description=f"Value for '{field_name}' has near match but not exact",
                        field_name=field_name,
                        expected_value=float(calc_value),
                        found_value=float(close_matches[0])
                    ))
                else:
                    # No match at all - could be missing or contradiction
                    issues.append(ValidationIssue(
                        issue_type="missing_value",
                        severity="warning" if not self._strict_mode else "critical",
                        description=f"Value for '{field_name}' not found in AI text",
                        field_name=field_name,
                        expected_value=float(calc_value)
                    ))

        return issues

    def _values_match(self, value1: Decimal, value2: Decimal) -> bool:
        """
        Check if two decimal values match within tolerance.

        Args:
            value1: First value
            value2: Second value

        Returns:
            True if values match within tolerance
        """
        diff = abs(float(value1 - value2))
        return diff <= self._tolerance

    def validate_with_context(
        self,
        original_result: Dict[str, Any],
        enhanced_result: Dict[str, Any]
    ) -> ValidationReport:
        """
        Validate that enhanced result preserves original calculation.

        This validates structured data rather than text.

        Args:
            original_result: Original calculation result
            enhanced_result: Enhanced result to validate

        Returns:
            ValidationReport
        """
        report = ValidationReport(is_valid=True)

        # Check if enhanced result contains original result
        for key, original_value in original_result.items():
            if key not in enhanced_result:
                report.issues.append(ValidationIssue(
                    issue_type="missing_field",
                    severity="critical",
                    description=f"Field '{key}' missing from enhanced result",
                    field_name=key
                ))
                report.is_valid = False
                continue

            enhanced_value = enhanced_result[key]

            # Compare values
            if isinstance(original_value, dict) and isinstance(enhanced_value, dict):
                # Recursively validate nested dicts
                nested_report = self.validate_with_context(
                    original_value,
                    enhanced_value
                )
                report.issues.extend(nested_report.issues)
                if not nested_report.is_valid:
                    report.is_valid = False

            elif original_value != enhanced_value:
                report.issues.append(ValidationIssue(
                    issue_type="contradiction",
                    severity="critical",
                    description=f"Value for '{key}' changed in enhanced result",
                    field_name=key,
                    expected_value=original_value,
                    found_value=enhanced_value
                ))
                report.is_valid = False
                self._contradictions_found += 1

        return report

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get validation statistics.

        Returns:
            Dictionary with statistics
        """
        success_count = self._validation_count - self._validation_failures
        success_rate = (
            success_count / self._validation_count
            if self._validation_count > 0
            else 0.0
        )

        return {
            "strict_mode": self._strict_mode,
            "tolerance": self._tolerance,
            "total_validations": self._validation_count,
            "successful_validations": success_count,
            "failed_validations": self._validation_failures,
            "success_rate": success_rate,
            "contradictions_found": self._contradictions_found
        }

    def reset_statistics(self):
        """Reset validation statistics"""
        self._validation_count = 0
        self._validation_failures = 0
        self._contradictions_found = 0
        logger.info("Statistics reset")

    def set_strict_mode(self, enabled: bool):
        """Enable or disable strict mode"""
        self._strict_mode = enabled
        logger.info(f"Strict mode: {enabled}")

    def is_strict_mode(self) -> bool:
        """Check if strict mode is enabled"""
        return self._strict_mode
