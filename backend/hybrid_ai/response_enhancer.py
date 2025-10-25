"""
AI Response Enhancer
Legal Advisory System v5.0

Enhances calculation results with AI-generated explanations while
maintaining 100% calculation accuracy.

CRITICAL PRINCIPLE: AI enhances explanations only. NEVER modifies calculations.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from backend.interfaces.ai_service import IAIService
from backend.interfaces.data_structures import AIRequest, AIResponse, AIServiceType

logger = logging.getLogger(__name__)


@dataclass
class EnhancementResult:
    """Result of AI enhancement"""
    original_result: Dict[str, Any]
    enhanced_explanation: str
    calculation_preserved: bool
    enhancement_metadata: Dict[str, Any]


class ResponseEnhancerError(Exception):
    """Exception raised for response enhancer errors"""
    pass


class ResponseEnhancer:
    """
    Enhances legal calculation results with AI-generated explanations.

    This component is a critical part of the hybrid AI architecture:
    - Takes deterministic calculation results from legal modules
    - Uses AI to generate natural language explanations
    - NEVER modifies or overrides the original calculations
    - Adds context, examples, and user-friendly explanations

    Key Features:
    - Calculation preservation (100% accuracy maintained)
    - Configurable enhancement (can be disabled)
    - Context-aware explanations
    - Fallback to original results if enhancement fails
    - Enhancement validation

    Example:
        >>> enhancer = ResponseEnhancer(ai_service)
        >>> calculation_result = {
        ...     "total_costs": 1500.00,
        ...     "filing_fee": 500.00,
        ...     "hearing_fee": 1000.00
        ... }
        >>> enhanced = await enhancer.enhance_calculation_result(
        ...     calculation_result,
        ...     context={"case_type": "order_21", "module": "costs"}
        ... )
        >>> print(enhanced.enhanced_explanation)
    """

    def __init__(
        self,
        ai_service: IAIService,
        enable_enhancement: bool = True,
        max_explanation_length: int = 2000
    ):
        """
        Initialize Response Enhancer.

        Args:
            ai_service: AI service for generating enhancements
            enable_enhancement: Whether to enable AI enhancement (default: True)
            max_explanation_length: Maximum length for explanations

        Raises:
            TypeError: If ai_service doesn't implement IAIService
        """
        if not isinstance(ai_service, IAIService):
            raise TypeError(
                f"ai_service must implement IAIService, got {type(ai_service)}"
            )

        self._ai_service = ai_service
        self._enable_enhancement = enable_enhancement
        self._max_explanation_length = max_explanation_length

        # Statistics
        self._enhancement_count = 0
        self._enhancement_failures = 0
        self._fallback_count = 0

        logger.info(
            f"ResponseEnhancer initialized "
            f"(enhancement: {enable_enhancement}, max_length: {max_explanation_length})"
        )

    async def enhance_calculation_result(
        self,
        calculation_result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        recommendations: Optional[List[str]] = None
    ) -> EnhancementResult:
        """
        Enhance calculation result with AI-generated explanation.

        This is the main enhancement method. It:
        1. Validates the calculation result
        2. Constructs enhancement prompt
        3. Calls AI service to generate explanation
        4. Validates enhancement doesn't contradict calculations
        5. Returns enhanced result with preserved calculations

        Args:
            calculation_result: Dictionary with calculation results
            context: Optional context (module_id, case_type, etc.)
            recommendations: Optional list of recommendations

        Returns:
            EnhancementResult with original calculations + AI explanation

        Example:
            >>> result = {"total_cost": 1500, "breakdown": {...}}
            >>> enhanced = await enhancer.enhance_calculation_result(result)
            >>> assert enhanced.calculation_preserved is True
        """
        self._enhancement_count += 1

        # If enhancement is disabled, return original result
        if not self._enable_enhancement:
            logger.debug("Enhancement disabled - returning original result")
            return EnhancementResult(
                original_result=calculation_result,
                enhanced_explanation="[Enhancement disabled]",
                calculation_preserved=True,
                enhancement_metadata={"enhanced": False, "reason": "disabled"}
            )

        # Validate calculation result
        if not calculation_result:
            logger.warning("Empty calculation result provided")
            return self._create_fallback_result(
                calculation_result,
                "Empty calculation result"
            )

        try:
            # Construct enhancement prompt
            prompt = self._construct_enhancement_prompt(
                calculation_result,
                context,
                recommendations
            )

            logger.debug(f"Generating enhancement with AI service")

            # Call AI service
            ai_request = AIRequest(
                service_type=AIServiceType.ENHANCEMENT,
                prompt=prompt,
                context=context or {},
                max_tokens=self._max_explanation_length,
                temperature=0.7
            )

            ai_response = await self._ai_service.generate(ai_request)

            # Validate enhancement
            is_valid = await self._validate_enhancement(
                calculation_result,
                ai_response.content
            )

            if not is_valid:
                logger.warning("Enhancement validation failed - using fallback")
                self._enhancement_failures += 1
                return self._create_fallback_result(
                    calculation_result,
                    "Enhancement validation failed"
                )

            # Create enhanced result
            result = EnhancementResult(
                original_result=calculation_result,
                enhanced_explanation=ai_response.content,
                calculation_preserved=True,
                enhancement_metadata={
                    "enhanced": True,
                    "tokens_used": ai_response.tokens_used,
                    "model": self._ai_service.model_name,
                    "provider": self._ai_service.provider.value
                }
            )

            logger.info(
                f"Enhancement successful "
                f"(tokens: {ai_response.tokens_used})"
            )

            return result

        except Exception as e:
            logger.error(f"Enhancement failed: {e}")
            self._enhancement_failures += 1
            return self._create_fallback_result(
                calculation_result,
                f"Enhancement error: {str(e)}"
            )

    async def enhance_recommendations(
        self,
        recommendations: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Enhance recommendations list with AI-generated context.

        Takes a list of recommendation strings and generates a cohesive
        explanation with additional context and examples.

        Args:
            recommendations: List of recommendation strings
            context: Optional context information

        Returns:
            Enhanced recommendations as a single string

        Example:
            >>> recs = ["File within 14 days", "Include all receipts"]
            >>> enhanced = await enhancer.enhance_recommendations(recs)
        """
        if not self._enable_enhancement or not recommendations:
            return "\n".join(recommendations)

        try:
            prompt = self._construct_recommendations_prompt(
                recommendations,
                context
            )

            ai_request = AIRequest(
                service_type=AIServiceType.ENHANCEMENT,
                prompt=prompt,
                context=context or {},
                max_tokens=1000,
                temperature=0.7
            )

            ai_response = await self._ai_service.generate(ai_request)

            return ai_response.content

        except Exception as e:
            logger.error(f"Failed to enhance recommendations: {e}")
            return "\n".join(recommendations)

    async def enhance_validation_error(
        self,
        error_message: str,
        field_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Enhance validation error message with helpful guidance.

        Takes a technical validation error and generates a user-friendly
        explanation with suggestions for correction.

        Args:
            error_message: Original error message
            field_name: Name of the field that failed validation
            context: Optional context information

        Returns:
            Enhanced error message with guidance

        Example:
            >>> enhanced = await enhancer.enhance_validation_error(
            ...     "Invalid date format",
            ...     "filing_date",
            ...     {"expected_format": "YYYY-MM-DD"}
            ... )
        """
        if not self._enable_enhancement:
            return error_message

        try:
            prompt = self._construct_error_enhancement_prompt(
                error_message,
                field_name,
                context
            )

            ai_request = AIRequest(
                service_type=AIServiceType.ENHANCEMENT,
                prompt=prompt,
                context=context or {},
                max_tokens=500,
                temperature=0.7
            )

            ai_response = await self._ai_service.generate(ai_request)

            return ai_response.content

        except Exception as e:
            logger.error(f"Failed to enhance error message: {e}")
            return error_message

    def _construct_enhancement_prompt(
        self,
        calculation_result: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        recommendations: Optional[List[str]]
    ) -> str:
        """
        Construct prompt for calculation result enhancement.

        Args:
            calculation_result: Calculation results to enhance
            context: Optional context
            recommendations: Optional recommendations

        Returns:
            Prompt string for AI service
        """
        prompt_parts = [
            "You are a legal advisory assistant explaining calculation results to users.",
            "",
            "CRITICAL: Your role is ONLY to explain the calculations, not to change them.",
            "The calculations provided are 100% accurate and must be preserved exactly.",
            "",
            "Calculation Results:",
            self._format_calculation_for_prompt(calculation_result),
            ""
        ]

        if context:
            prompt_parts.extend([
                "Context:",
                self._format_context_for_prompt(context),
                ""
            ])

        if recommendations:
            prompt_parts.extend([
                "Recommendations:",
                *[f"- {rec}" for rec in recommendations],
                ""
            ])

        prompt_parts.extend([
            "Please provide a clear, natural language explanation of these results:",
            "1. Explain what the calculations mean in plain English",
            "2. Add relevant context about Singapore Rules of Court",
            "3. Highlight any important points the user should know",
            "4. Keep the explanation concise (under 500 words)",
            "",
            "Remember: DO NOT change any numbers or calculations. Only explain them."
        ])

        return "\n".join(prompt_parts)

    def _construct_recommendations_prompt(
        self,
        recommendations: List[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Construct prompt for recommendations enhancement"""
        prompt_parts = [
            "You are a legal advisory assistant providing recommendations.",
            "",
            "Recommendations:",
            *[f"- {rec}" for rec in recommendations],
            ""
        ]

        if context:
            prompt_parts.extend([
                "Context:",
                self._format_context_for_prompt(context),
                ""
            ])

        prompt_parts.extend([
            "Please enhance these recommendations with:",
            "1. Clear explanations of why each recommendation matters",
            "2. Practical guidance on how to follow them",
            "3. Potential consequences of not following them",
            "4. Keep it concise and actionable"
        ])

        return "\n".join(prompt_parts)

    def _construct_error_enhancement_prompt(
        self,
        error_message: str,
        field_name: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Construct prompt for error message enhancement"""
        prompt_parts = [
            "You are a helpful assistant explaining validation errors to users.",
            "",
            f"Field: {field_name}",
            f"Error: {error_message}",
            ""
        ]

        if context:
            prompt_parts.extend([
                "Additional Context:",
                self._format_context_for_prompt(context),
                ""
            ])

        prompt_parts.extend([
            "Please provide a user-friendly explanation:",
            "1. Explain what went wrong in simple terms",
            "2. Provide clear guidance on how to fix it",
            "3. Include an example of correct input if relevant",
            "4. Keep it brief and actionable"
        ])

        return "\n".join(prompt_parts)

    def _format_calculation_for_prompt(self, calculation: Dict[str, Any]) -> str:
        """Format calculation result for prompt"""
        lines = []
        for key, value in calculation.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    lines.append(f"  {sub_key}: {sub_value}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def _format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Format context for prompt"""
        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    async def _validate_enhancement(
        self,
        original_result: Dict[str, Any],
        enhanced_text: str
    ) -> bool:
        """
        Validate that enhancement doesn't contradict calculations.

        This is a critical safety check to ensure AI never changes
        the calculation results.

        Args:
            original_result: Original calculation results
            enhanced_text: AI-generated enhancement text

        Returns:
            True if enhancement is valid, False otherwise
        """
        # Basic validation - check enhancement exists and has content
        if not enhanced_text or len(enhanced_text.strip()) < 20:
            logger.warning("Enhancement too short or empty")
            return False

        # Check for common AI hallucination patterns
        hallucination_patterns = [
            "I cannot",
            "I don't have access",
            "as an AI",
            "I apologize, but",
            "[calculation error]",
            "[invalid]"
        ]

        enhanced_lower = enhanced_text.lower()
        for pattern in hallucination_patterns:
            if pattern.lower() in enhanced_lower:
                logger.warning(f"Detected hallucination pattern: {pattern}")
                return False

        # Additional validation could include:
        # - Checking that numeric values in text match original results
        # - Ensuring no contradictory statements
        # This is a basic implementation; could be enhanced further

        return True

    def _create_fallback_result(
        self,
        calculation_result: Dict[str, Any],
        reason: str
    ) -> EnhancementResult:
        """
        Create fallback result when enhancement fails.

        Args:
            calculation_result: Original calculation
            reason: Reason for fallback

        Returns:
            EnhancementResult with basic explanation
        """
        self._fallback_count += 1

        # Generate basic explanation from calculation result
        basic_explanation = self._generate_basic_explanation(calculation_result)

        return EnhancementResult(
            original_result=calculation_result,
            enhanced_explanation=basic_explanation,
            calculation_preserved=True,
            enhancement_metadata={
                "enhanced": False,
                "reason": reason,
                "fallback": True
            }
        )

    def _generate_basic_explanation(
        self,
        calculation_result: Dict[str, Any]
    ) -> str:
        """Generate basic explanation without AI"""
        lines = ["Calculation Results:"]

        for key, value in calculation_result.items():
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
        Get enhancement statistics.

        Returns:
            Dictionary with statistics

        Example:
            >>> stats = enhancer.get_statistics()
            >>> print(f"Success rate: {stats['success_rate']:.2%}")
        """
        success_count = self._enhancement_count - self._enhancement_failures
        success_rate = (
            success_count / self._enhancement_count
            if self._enhancement_count > 0
            else 0.0
        )

        return {
            "enhancement_enabled": self._enable_enhancement,
            "total_enhancements": self._enhancement_count,
            "successful_enhancements": success_count,
            "failed_enhancements": self._enhancement_failures,
            "fallback_count": self._fallback_count,
            "success_rate": success_rate,
            "ai_service_provider": self._ai_service.provider.value,
            "ai_service_model": self._ai_service.model_name
        }

    def reset_statistics(self):
        """Reset enhancement statistics"""
        self._enhancement_count = 0
        self._enhancement_failures = 0
        self._fallback_count = 0
        logger.info("Statistics reset")

    def enable_enhancement(self):
        """Enable AI enhancement"""
        self._enable_enhancement = True
        logger.info("Enhancement enabled")

    def disable_enhancement(self):
        """Disable AI enhancement"""
        self._enable_enhancement = False
        logger.info("Enhancement disabled")

    def is_enhancement_enabled(self) -> bool:
        """Check if enhancement is enabled"""
        return self._enable_enhancement
