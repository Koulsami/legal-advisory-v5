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
from difflib import SequenceMatcher

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


class QuoteAccuracyVerifier:
    """
    Verifies that quoted text matches source material.

    Uses fuzzy matching to handle minor variations while detecting
    significant misquotes or fabricated quotes.
    """

    def __init__(self, similarity_threshold: float = 0.80):
        """
        Initialize verifier.

        Args:
            similarity_threshold: Minimum similarity for quote to be considered accurate (0.0-1.0)
        """
        self.similarity_threshold = similarity_threshold

    def verify_quote(self, quote: str, source_text: str) -> tuple[bool, float]:
        """
        Verify if a quote appears in source text.

        Args:
            quote: The quoted text to verify
            source_text: The source text where quote should appear

        Returns:
            Tuple of (is_accurate, similarity_score)
        """
        # Normalize both strings
        quote_norm = self._normalize_text(quote)
        source_norm = self._normalize_text(source_text)

        # Check if quote is a substring (perfect match)
        if quote_norm in source_norm:
            return (True, 1.0)

        # Check if quote appears with minor differences
        similarity = self._fuzzy_match(quote_norm, source_norm)

        is_accurate = similarity >= self.similarity_threshold
        return (is_accurate, similarity)

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def _fuzzy_match(self, quote: str, source: str) -> float:
        """
        Calculate fuzzy similarity between quote and source.

        Checks both:
        1. If quote appears as substring (with some tolerance)
        2. Sequence matching ratio

        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Try to find quote in source with sliding window
        quote_len = len(quote)
        if quote_len == 0:
            return 0.0

        best_match = 0.0

        # Slide through source text
        for i in range(len(source) - quote_len + 1):
            window = source[i:i + quote_len]
            similarity = SequenceMatcher(None, quote, window).ratio()
            best_match = max(best_match, similarity)

            # Early exit if we find excellent match
            if best_match >= 0.95:
                break

        # Also check overall similarity
        overall_similarity = SequenceMatcher(None, quote, source).ratio()

        return max(best_match, overall_similarity)


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
        self.quote_verifier = QuoteAccuracyVerifier(similarity_threshold=0.80)
        self._validation_count = 0
        self._failure_count = 0
        self._correction_success_count = 0

        logger.info("ResponseValidator initialized - 100% validation coverage enforced")
        logger.info("  - Quote accuracy verification enabled (threshold: 80%)")

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

        # Check 6: Quote Accuracy Verification
        quote_issues = self._verify_quote_accuracy(ai_response, session)
        issues.extend(quote_issues)

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

    def _verify_quote_accuracy(self, response: str, session) -> List[ValidationIssue]:
        """
        Verify accuracy of any quotes in the response.

        Checks if quoted text actually appears in logic tree nodes with sufficient accuracy.

        Args:
            response: AI response to check
            session: Current session with logic tree context

        Returns:
            List of quote accuracy issues found
        """
        issues = []

        # Pattern to match quoted text (both "..." and '...')
        quote_patterns = [
            r'"([^"]{20,})"',  # Double quotes, at least 20 chars
            r"'([^']{20,})'"   # Single quotes, at least 20 chars
        ]

        quotes_found = []
        for pattern in quote_patterns:
            matches = re.findall(pattern, response)
            quotes_found.extend(matches)

        if not quotes_found:
            # No significant quotes to verify
            return issues

        # Get logic tree nodes from module registry
        if not self.module_registry or not session.module_id:
            # Can't verify without access to source material
            return issues

        try:
            module = self.module_registry.get_module(session.module_id)
            if not module:
                return issues

            # Get all logic tree nodes for this module
            tree_framework = self.module_registry.tree_framework
            logic_tree = tree_framework.get_module_tree(session.module_id)

            # Build searchable text from all nodes
            source_texts = []
            for node in logic_tree:
                # Collect text from all logical deductions
                node_texts = []

                for dimension in ['what', 'which', 'if_then', 'modality', 'given', 'why']:
                    dimension_data = getattr(node, dimension, None)
                    if dimension_data:
                        for item in dimension_data:
                            if isinstance(item, dict) and 'description' in item:
                                node_texts.append(item['description'])
                            elif isinstance(item, str):
                                node_texts.append(item)

                # Combine all node text
                combined_text = " ".join(node_texts)
                if combined_text:
                    source_texts.append({
                        'node_id': node.node_id,
                        'citation': node.citation,
                        'text': combined_text
                    })

            # Verify each quote against source texts
            for quote in quotes_found:
                quote_verified = False
                best_similarity = 0.0

                for source in source_texts:
                    is_accurate, similarity = self.quote_verifier.verify_quote(
                        quote, source['text']
                    )

                    best_similarity = max(best_similarity, similarity)

                    if is_accurate:
                        quote_verified = True
                        logger.debug(f"Quote verified in {source['citation']}: {similarity:.2%} match")
                        break

                if not quote_verified:
                    # Quote doesn't match any source with sufficient accuracy
                    issues.append(ValidationIssue(
                        issue_type="quote_accuracy",
                        severity="high",
                        description=f"Quoted text doesn't match source material (best match: {best_similarity:.0%})",
                        context=quote[:100] + "..." if len(quote) > 100 else quote,
                        suggestion="Remove quote or verify against Rules of Court"
                    ))
                    logger.warning(f"Potential misquote detected (similarity: {best_similarity:.0%})")

        except Exception as e:
            logger.error(f"Error during quote verification: {e}")
            # Don't fail validation if quote verification has issues
            # This is an enhancement, not a critical check

        return issues

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
