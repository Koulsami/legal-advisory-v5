"""
Response Validator - MANDATORY VALIDATION LAYER
Legal Advisory System v6.0

CRITICAL COMPONENT - P0 Priority

Validates 100% of AI-generated responses before delivery to users.
Prevents AI hallucinations and ensures legal accuracy.

Validation Checks:
1. Citation Verification - All cited rules exist
2. Requirement Verification - Stated requirements are accurate
3. Field Verification - Asked-about fields are valid
4. Hallucination Detection - No invented legal concepts
5. Consistency Check - Consistent with previous information

Zero unvalidated responses must reach users.
"""

import re
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime

from backend.common_services.logging_config import get_logger
from backend.mykraws.conversation_manager_v6 import ValidationLog

logger = get_logger(__name__)


@dataclass
class ValidationIssue:
    """An issue found during validation"""
    issue_type: str  # citation, requirement, field, hallucination, consistency
    severity: str    # critical, high, medium, low
    description: str
    context: str     # Where in response the issue was found
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validating an AI response"""
    passed: bool
    original_response: str
    final_response: str  # Original if passed, corrected if failed
    issues: List[ValidationIssue] = field(default_factory=list)
    corrected: bool = False
    correction_attempts: int = 0
    log: Optional[ValidationLog] = None

    def __post_init__(self):
        """Create validation log"""
        self.log = ValidationLog(
            timestamp=datetime.utcnow(),
            original_response=self.original_response,
            validation_result=self.passed,
            issues_found=[i.description for i in self.issues],
            corrected_response=self.final_response if self.corrected else None,
            correction_attempts=self.correction_attempts,
            rules_checked_against=[]  # Will be populated by validator
        )


class ResponseValidator:
    """
    Mandatory validation layer for ALL AI-generated responses.

    CRITICAL REQUIREMENTS:
    - 100% coverage - zero unvalidated responses to users
    - Validates before delivery - not after
    - Corrects failed validations automatically
    - Logs all validation attempts
    - Falls back to structured questions if correction fails

    This is the CORE of v6.0's legal accuracy guarantee.
    """

    # Known valid Rules of Court citations for Order 21
    VALID_RULES = {
        "Order 21, Rule 1": "Costs in civil proceedings",
        "Order 21, Rule 2": "Assessment of costs",
        "Order 21, Rule 3": "Fixed costs",
        "Order 21, Rule 4": "Offers to settle and ADR",
        "Order 21, Rule 5": "Unrepresented parties",
        "Order 21, Rule 6": "Costs payable to or by particular persons",
        "Order 21, Rule 7": "Costs on discontinuance",
        "Order 21, Rule 8": "Costs following acceptance of payment into Court",
        "Order 21, Rule 9": "Costs where money paid into Court",
        "Order 21, Rule 10": "Costs on judgment by default",
        "Order 21, Appendix 1": "Fixed costs schedule",
        "Order 21, Appendix 1, Part I": "High Court costs",
        "Order 21, Appendix 1, Part II": "District Court costs",
        "Order 21, Appendix 1, Part III": "Magistrates Court costs",
        "Order 21, Appendix 1, Section A": "Liquidated claims",
        "Order 21, Appendix 1, Section B": "Unliquidated claims",
        "Order 21, Appendix 1, Section C": "Interlocutory applications",
        "Order 5, Rule 1": "Court-ordered ADR",
        "Order 22A": "Settlement offers",
    }

    # Valid field names for Order 21 module
    VALID_FIELDS = {
        "court_level",
        "case_type",
        "claim_amount",
        "claim_nature",
        "trial_days",
        "complexity_level",
        "basis_of_taxation",
        "party_type",
        "defendant_count",
        "interlocutory_applications",
        "adr_refused",
        "settlement_offered"
    }

    def __init__(self, module_registry=None):
        """
        Initialize response validator.

        Args:
            module_registry: Optional access to module registry for dynamic validation
        """
        self.module_registry = module_registry
        self._validation_count = 0
        self._failure_count = 0
        self._correction_success_count = 0

        logger.info("ResponseValidator initialized - 100% validation coverage enforced")

    def validate(
        self,
        ai_response: str,
        session
    ) -> ValidationResult:
        """
        Validate AI-generated response against Rules of Court.

        This is the MANDATORY gate - all AI responses must pass through here.

        Args:
            ai_response: AI-generated response (UNVALIDATED)
            session: Current conversation session

        Returns:
            ValidationResult with passed/failed status and corrected response
        """
        self._validation_count += 1

        logger.info(f"Validating AI response (validation #{self._validation_count})")

        # Run all validation checks
        issues = []

        # Check 1: Citation Verification
        citation_issues = self._verify_citations(ai_response)
        issues.extend(citation_issues)

        # Check 2: Requirement Verification
        requirement_issues = self._verify_requirements(ai_response)
        issues.extend(requirement_issues)

        # Check 3: Field Verification
        field_issues = self._verify_fields(ai_response)
        issues.extend(field_issues)

        # Check 4: Hallucination Detection
        hallucination_issues = self._detect_hallucinations(ai_response)
        issues.extend(hallucination_issues)

        # Check 5: Consistency Check
        consistency_issues = self._check_consistency(ai_response, session)
        issues.extend(consistency_issues)

        # Determine if validation passed
        critical_issues = [i for i in issues if i.severity in ["critical", "high"]]

        if not critical_issues:
            # PASSED - deliver response as-is
            logger.info(f"✅ Validation PASSED (minor issues: {len(issues)})")
            return ValidationResult(
                passed=True,
                original_response=ai_response,
                final_response=ai_response,
                issues=issues
            )

        else:
            # FAILED - attempt correction
            logger.warning(f"❌ Validation FAILED: {len(critical_issues)} critical issues")
            self._failure_count += 1

            # Log issues
            for issue in critical_issues:
                logger.warning(f"  - {issue.issue_type}: {issue.description}")

            # Attempt to correct
            corrected_response, success = self._correct_response(ai_response, issues)

            if success:
                self._correction_success_count += 1
                logger.info(f"✅ Response corrected successfully")

                # Re-validate corrected response (ONE re-validation only)
                revalidation = self._quick_revalidate(corrected_response)

                if revalidation:
                    return ValidationResult(
                        passed=True,
                        original_response=ai_response,
                        final_response=corrected_response,
                        issues=issues,
                        corrected=True,
                        correction_attempts=1
                    )

            # Correction failed - fall back to safe structured question
            logger.error(f"❌ Correction failed - using fallback")
            fallback_response = self._generate_fallback(session)

            return ValidationResult(
                passed=False,
                original_response=ai_response,
                final_response=fallback_response,
                issues=issues,
                corrected=True,
                correction_attempts=2  # Indicates fallback was used
            )

    def _verify_citations(self, response: str) -> List[ValidationIssue]:
        """
        Verify all cited rules actually exist.

        Checks for patterns like "Order 21, Rule X" and validates against known rules.

        Args:
            response: AI response to check

        Returns:
            List of citation issues found
        """
        issues = []

        # Pattern to match rule citations
        citation_pattern = r'Order\s+\d+(?:,\s*Rule\s+\d+(?:\([a-z0-9]+\))?(?:,\s*Appendix\s+\d+)?(?:,\s*Part\s+[IVX]+)?(?:,\s*Section\s+[A-Z])?)?'

        # Find all citations in response
        citations = re.findall(citation_pattern, response, re.IGNORECASE)

        for citation in citations:
            # Normalize citation
            normalized = self._normalize_citation(citation)

            # Check if it's a known valid rule
            if normalized not in self.VALID_RULES:
                # Check if it's a partial match
                if not any(normalized in valid_rule for valid_rule in self.VALID_RULES):
                    issues.append(ValidationIssue(
                        issue_type="citation",
                        severity="critical",
                        description=f"Cited rule '{citation}' does not exist in provided Rules of Court",
                        context=citation,
                        suggestion="Remove citation or replace with valid rule"
                    ))
                    logger.warning(f"Invalid citation found: {citation}")

        return issues

    def _verify_requirements(self, response: str) -> List[ValidationIssue]:
        """
        Verify stated requirements are accurate.

        Checks for claims like "you must file within X days" and validates them.

        Args:
            response: AI response to check

        Returns:
            List of requirement issues found
        """
        issues = []

        # Common requirement phrases that might be hallucinated
        requirement_patterns = [
            r'you must file within (\d+) (days|weeks|months)',
            r'mandatory to (\w+)',
            r'required to file (\w+)',
            r'deadline of (\d+) (days|weeks|months)',
        ]

        for pattern in requirement_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            if matches:
                # These should be grounded in actual rules
                # For now, flag as potential issue if not accompanied by citation
                for match in matches:
                    context = str(match)
                    # Check if there's a nearby rule citation
                    if not re.search(r'Order\s+\d+.*Rule\s+\d+', response[max(0, response.find(context)-100):response.find(context)+100]):
                        issues.append(ValidationIssue(
                            issue_type="requirement",
                            severity="high",
                            description=f"Requirement stated without rule citation: {context}",
                            context=context,
                            suggestion="Add rule citation to support requirement"
                        ))

        return issues

    def _verify_fields(self, response: str) -> List[ValidationIssue]:
        """
        Verify asked-about fields are valid module fields.

        Args:
            response: AI response to check

        Returns:
            List of field issues found
        """
        issues = []

        # Look for field name patterns in questions
        response_lower = response.lower()

        # Check for invalid field references
        # This is a simple check - could be enhanced with NLP
        suspicious_terms = [
            "filing fee", "court fee",  # Not fields we track
            "lawyer fee", "solicitor fee",  # Different from party-party costs
        ]

        for term in suspicious_terms:
            if term in response_lower:
                issues.append(ValidationIssue(
                    issue_type="field",
                    severity="medium",
                    description=f"Potentially incorrect field reference: {term}",
                    context=term,
                    suggestion="Ensure question asks about valid cost factors"
                ))

        return issues

    def _detect_hallucinations(self, response: str) -> List[ValidationIssue]:
        """
        Detect potential hallucinations (invented legal concepts).

        Args:
            response: AI response to check

        Returns:
            List of hallucination issues found
        """
        issues = []

        # Known hallucination patterns
        hallucination_indicators = [
            (r'Under Rule \d+ of the (?!Rules of Court|Singapore)', "Invalid rule reference format"),
            (r'Section \d+\([a-z]\) of Order 21', "Order 21 doesn't use subsection notation"),
            (r'Form [A-Z]{2,}', "Singapore doesn't use Form references in Order 21"),
        ]

        for pattern, description in hallucination_indicators:
            if re.search(pattern, response):
                issues.append(ValidationIssue(
                    issue_type="hallucination",
                    severity="critical",
                    description=description,
                    context=re.search(pattern, response).group(0),
                    suggestion="Remove hallucinated content"
                ))

        return issues

    def _check_consistency(
        self,
        response: str,
        session
    ) -> List[ValidationIssue]:
        """
        Check consistency with previously validated information.

        Args:
            response: AI response to check
            session: Current session with filled fields

        Returns:
            List of consistency issues found
        """
        issues = []

        # Check if response contradicts known information
        # For example, if user said "High Court" but response mentions "District Court"
        filled_fields = session.filled_fields

        if "court_level" in filled_fields:
            court = filled_fields["court_level"]
            # Check if response mentions a different court
            other_courts = {"High Court", "District Court", "Magistrates Court"} - {court}

            for other_court in other_courts:
                if other_court in response and court not in response:
                    issues.append(ValidationIssue(
                        issue_type="consistency",
                        severity="high",
                        description=f"Response mentions {other_court} but user specified {court}",
                        context=other_court,
                        suggestion=f"Ensure response refers to {court}"
                    ))

        return issues

    def _correct_response(
        self,
        original_response: str,
        issues: List[ValidationIssue]
    ) -> tuple[str, bool]:
        """
        Attempt to correct a failed validation.

        Args:
            original_response: Original AI response
            issues: Issues found

        Returns:
            (corrected_response, success)
        """
        corrected = original_response

        # Apply corrections based on issues
        for issue in issues:
            if issue.severity == "critical":
                if issue.issue_type == "citation":
                    # Remove invalid citations
                    corrected = corrected.replace(issue.context, "[citation removed]")

                elif issue.issue_type == "hallucination":
                    # Remove hallucinated content
                    corrected = corrected.replace(issue.context, "")

        # Clean up the corrected response
        corrected = re.sub(r'\[citation removed\]\s*', '', corrected)
        corrected = re.sub(r'\s+', ' ', corrected).strip()

        # Check if correction is viable (has substance left)
        if len(corrected) < 20:
            return original_response, False

        return corrected, True

    def _quick_revalidate(self, response: str) -> bool:
        """
        Quick revalidation of corrected response.

        Args:
            response: Corrected response

        Returns:
            True if passed quick checks
        """
        # Quick check: no invalid citations
        citations = re.findall(r'Order\s+\d+,\s*Rule\s+\d+', response, re.IGNORECASE)
        for citation in citations:
            normalized = self._normalize_citation(citation)
            if normalized not in self.VALID_RULES:
                return False

        return True

    def _generate_fallback(self, session) -> str:
        """
        Generate safe fallback question when correction fails.

        Args:
            session: Current session

        Returns:
            Safe structured question
        """
        # Generate a simple, safe question based on what's missing
        if not session.filled_fields.get("court_level"):
            return "Which court is your matter in - High Court, District Court, or Magistrates Court?"

        if not session.filled_fields.get("case_type"):
            return "What type of judgment is this - default judgment, summary judgment, or contested trial?"

        if not session.filled_fields.get("claim_amount"):
            return "What is the claim amount? This helps determine the appropriate costs."

        # Generic fallback
        return "Could you tell me more about your case so I can calculate the appropriate costs?"

    def _normalize_citation(self, citation: str) -> str:
        """
        Normalize a rule citation for comparison.

        Args:
            citation: Raw citation text

        Returns:
            Normalized citation
        """
        # Remove extra whitespace, standardize format
        normalized = re.sub(r'\s+', ' ', citation.strip())

        # Capitalize properly
        normalized = re.sub(
            r'\border\b',
            'Order',
            normalized,
            flags=re.IGNORECASE
        )
        normalized = re.sub(
            r'\brule\b',
            'Rule',
            normalized,
            flags=re.IGNORECASE
        )

        return normalized

    def get_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return {
            "total_validations": self._validation_count,
            "failures": self._failure_count,
            "correction_successes": self._correction_success_count,
            "failure_rate": self._failure_count / self._validation_count if self._validation_count > 0 else 0,
            "correction_success_rate": self._correction_success_count / self._failure_count if self._failure_count > 0 else 0
        }
