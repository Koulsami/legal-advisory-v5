"""
Hybrid AI Orchestrator
Legal Advisory System v5.0

Orchestrates the complete hybrid AI workflow combining:
- Claude AI Service (AI generation)
- Response Enhancer (explanation enhancement)
- Validation Guard (safety validation)

CRITICAL PRINCIPLE: This orchestrator ensures the hybrid AI workflow
maintains 100% calculation accuracy while enhancing user experience.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from backend.hybrid_ai.claude_ai_service import ClaudeAIService
from backend.hybrid_ai.response_enhancer import ResponseEnhancer, EnhancementResult
from backend.hybrid_ai.validation_guard import ValidationGuard, ValidationReport

logger = logging.getLogger(__name__)


@dataclass
class HybridResult:
    """Complete hybrid AI result"""
    original_calculation: Dict[str, Any]
    enhanced_result: EnhancementResult
    validation_report: ValidationReport
    is_safe: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class HybridAIOrchestrator:
    """
    Orchestrates the complete hybrid AI workflow.

    This is the top-level component that coordinates:
    1. ClaudeAIService - AI generation
    2. ResponseEnhancer - Explanation enhancement
    3. ValidationGuard - Safety validation

    The workflow ensures:
    - Calculations are never modified
    - AI enhancements are validated
    - Unsafe responses are rejected
    - Fallback to basic explanations if needed

    Example:
        >>> orchestrator = HybridAIOrchestrator(ai_service)
        >>> calculation = {"total": 1500, "fee": 500}
        >>> result = await orchestrator.enhance_and_validate(calculation)
        >>> assert result.is_safe is True
        >>> print(result.enhanced_result.enhanced_explanation)
    """

    def __init__(
        self,
        ai_service: ClaudeAIService,
        enable_enhancement: bool = True,
        strict_validation: bool = True
    ):
        """
        Initialize Hybrid AI Orchestrator.

        Args:
            ai_service: Claude AI service for generation
            enable_enhancement: Enable AI enhancement (default: True)
            strict_validation: Use strict validation mode (default: True)
        """
        self._ai_service = ai_service
        self._enhancer = ResponseEnhancer(
            ai_service,
            enable_enhancement=enable_enhancement
        )
        self._validator = ValidationGuard(
            strict_mode=strict_validation
        )

        # Statistics
        self._total_orchestrations = 0
        self._safe_results = 0
        self._unsafe_results = 0
        self._fallback_count = 0

        logger.info(
            f"HybridAIOrchestrator initialized "
            f"(enhancement: {enable_enhancement}, strict: {strict_validation})"
        )

    async def enhance_and_validate(
        self,
        calculation_result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        recommendations: Optional[list] = None
    ) -> HybridResult:
        """
        Enhance calculation with AI and validate for safety.

        This is the main orchestration method:
        1. Enhance calculation with AI explanations
        2. Validate enhancement doesn't contradict calculations
        3. Return safe result or fallback if validation fails

        Args:
            calculation_result: Original calculation results
            context: Optional context information
            recommendations: Optional recommendations list

        Returns:
            HybridResult with enhanced and validated result

        Example:
            >>> calc = {"total_cost": 1500, "filing_fee": 500}
            >>> result = await orchestrator.enhance_and_validate(calc)
            >>> if result.is_safe:
            ...     print(result.enhanced_result.enhanced_explanation)
        """
        self._total_orchestrations += 1

        logger.debug("Starting hybrid orchestration")

        # Step 1: Enhance calculation with AI
        try:
            enhanced_result = await self._enhancer.enhance_calculation_result(
                calculation_result,
                context=context,
                recommendations=recommendations
            )
        except Exception as e:
            logger.error(f"Enhancement failed: {e}")
            # Create fallback result
            enhanced_result = self._create_fallback_enhancement(calculation_result)
            self._fallback_count += 1

        # Step 2: Validate enhancement
        validation_report = self._validator.validate(
            calculation_result,
            enhanced_result.enhanced_explanation,
            context=context
        )

        # Step 3: Determine safety
        is_safe = self._determine_safety(enhanced_result, validation_report)

        if is_safe:
            self._safe_results += 1
        else:
            self._unsafe_results += 1
            logger.warning(
                f"Unsafe result detected: {len(validation_report.issues)} issues"
            )

            # If unsafe and strict, use fallback
            if self._validator.is_strict_mode():
                enhanced_result = self._create_fallback_enhancement(calculation_result)
                self._fallback_count += 1

        # Step 4: Build hybrid result
        result = HybridResult(
            original_calculation=calculation_result,
            enhanced_result=enhanced_result,
            validation_report=validation_report,
            is_safe=is_safe,
            metadata={
                "orchestration_id": self._total_orchestrations,
                "enhancement_enabled": self._enhancer.is_enhancement_enabled(),
                "strict_validation": self._validator.is_strict_mode(),
                "used_fallback": enhanced_result.enhancement_metadata.get("fallback", False)
            }
        )

        logger.info(
            f"Orchestration complete: safe={is_safe}, "
            f"confidence={validation_report.confidence_score:.2f}"
        )

        return result

    async def enhance_with_safety_check(
        self,
        calculation_result: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convenience method that returns a safe dictionary result.

        Args:
            calculation_result: Calculation to enhance
            **kwargs: Additional arguments

        Returns:
            Dictionary with safe results
        """
        hybrid_result = await self.enhance_and_validate(
            calculation_result,
            **kwargs
        )

        return {
            "calculation": hybrid_result.original_calculation,
            "explanation": hybrid_result.enhanced_result.enhanced_explanation,
            "is_safe": hybrid_result.is_safe,
            "validation_confidence": hybrid_result.validation_report.confidence_score,
            "validation_issues": len(hybrid_result.validation_report.issues),
            "metadata": hybrid_result.metadata
        }

    def _determine_safety(
        self,
        enhancement: EnhancementResult,
        validation: ValidationReport
    ) -> bool:
        """
        Determine if result is safe to use.

        A result is safe if:
        - Validation passed
        - Calculation was preserved
        - No critical issues
        - Sufficient confidence

        Args:
            enhancement: Enhancement result
            validation: Validation report

        Returns:
            True if safe, False otherwise
        """
        # Must preserve calculation
        if not enhancement.calculation_preserved:
            return False

        # Must pass validation
        if not validation.is_valid:
            return False

        # Check for critical issues
        critical_issues = [
            i for i in validation.issues
            if i.severity == "critical"
        ]
        if critical_issues:
            return False

        # Check confidence threshold
        if validation.confidence_score < 0.3:
            return False

        return True

    def _create_fallback_enhancement(
        self,
        calculation_result: Dict[str, Any]
    ) -> EnhancementResult:
        """
        Create fallback enhancement without AI.

        Args:
            calculation_result: Original calculation

        Returns:
            EnhancementResult with basic explanation
        """
        basic_explanation = self._generate_basic_explanation(calculation_result)

        return EnhancementResult(
            original_result=calculation_result,
            enhanced_explanation=basic_explanation,
            calculation_preserved=True,
            enhancement_metadata={
                "enhanced": False,
                "fallback": True,
                "reason": "Safety fallback"
            }
        )

    def _generate_basic_explanation(self, calculation: Dict[str, Any]) -> str:
        """Generate basic explanation without AI"""
        lines = ["Calculation Results:"]

        for key, value in calculation.items():
            formatted_key = key.replace("_", " ").title()
            if isinstance(value, dict):
                lines.append(f"\n{formatted_key}:")
                for sub_key, sub_value in value.items():
                    formatted_sub_key = sub_key.replace("_", " ").title()
                    lines.append(f"  - {formatted_sub_key}: {sub_value}")
            else:
                lines.append(f"- {formatted_key}: {value}")

        return "\n".join(lines)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get orchestration statistics.

        Returns:
            Dictionary with statistics
        """
        success_rate = (
            self._safe_results / self._total_orchestrations
            if self._total_orchestrations > 0
            else 0.0
        )

        return {
            "total_orchestrations": self._total_orchestrations,
            "safe_results": self._safe_results,
            "unsafe_results": self._unsafe_results,
            "fallback_count": self._fallback_count,
            "success_rate": success_rate,
            "enhancement_enabled": self._enhancer.is_enhancement_enabled(),
            "strict_validation": self._validator.is_strict_mode(),
            "ai_service_stats": self._ai_service.get_statistics(),
            "enhancer_stats": self._enhancer.get_statistics(),
            "validator_stats": self._validator.get_statistics()
        }

    def enable_enhancement(self):
        """Enable AI enhancement"""
        self._enhancer.enable_enhancement()

    def disable_enhancement(self):
        """Disable AI enhancement"""
        self._enhancer.disable_enhancement()

    def set_strict_validation(self, enabled: bool):
        """Enable or disable strict validation"""
        self._validator.set_strict_mode(enabled)
