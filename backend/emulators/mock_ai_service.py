"""
Mock AI Service for Testing
Implements IAIService interface with predictable responses
"""

from typing import Any, Dict, Optional

from backend.interfaces.ai_service import IAIService
from backend.interfaces.data_structures import AIProvider, AIRequest, AIResponse, AIServiceType


class MockAIService(IAIService):
    """
    Mock implementation of IAIService for testing.
    Returns predictable responses without making real API calls.
    """

    def __init__(self):
        self._provider = AIProvider.ANTHROPIC_CLAUDE
        self._model = "mock-claude-v1"
        self._call_count = 0

    @property
    def provider(self) -> AIProvider:
        """Return AI provider"""
        return self._provider

    @property
    def model_name(self) -> str:
        """Return model name"""
        return self._model

    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate mock AI response"""
        self._call_count += 1

        # Generate response based on service type
        if request.service_type == AIServiceType.CONVERSATION:
            response_text = self._generate_conversation_response(request)
        elif request.service_type == AIServiceType.ANALYSIS:
            response_text = self._generate_analysis_response(request)
        elif request.service_type == AIServiceType.ENHANCEMENT:
            response_text = self._generate_enhancement_response(request)
        else:
            response_text = "Mock response for unknown service type"

        return AIResponse(
            content=response_text,
            service_type=request.service_type,
            tokens_used=len(response_text.split()),
            finish_reason="stop",
            metadata={"call_number": self._call_count, "mock": True},
        )

    def _generate_conversation_response(self, request: AIRequest) -> str:
        """Generate mock conversation response"""
        context = request.context or {}
        filled_fields = context.get("filled_fields", {})

        if "case_type" not in filled_fields:
            return "To help you better, I need to know: What type of case is this? (civil, criminal, or family)"
        elif "amount_claimed" not in filled_fields:
            return "Thank you. Now, what is the amount claimed in this case?"
        elif "court_level" not in filled_fields:
            return "Great! Which court level will hear this case? (district, high, or appeal)"
        else:
            return "Thank you for providing all the information. I now have everything needed to analyze your case."

    def _generate_analysis_response(self, request: AIRequest) -> str:
        """Generate mock analysis response"""
        return """Based on the information provided, here is my analysis:

1. **Case Assessment**: This appears to be a standard case with clear parameters.
2. **Cost Implications**: The calculated costs are in line with typical cases of this nature.
3. **Procedural Considerations**: Ensure all filing deadlines are met.
4. **Strategic Recommendations**: The cost-benefit analysis favors proceeding.

This is a mock analysis generated for testing purposes."""

    def _generate_enhancement_response(self, request: AIRequest) -> str:
        """Generate mock enhancement response"""
        return """Enhanced Legal Advisory:

The calculated costs represent a fair assessment based on the applicable rules.
The breakdown shows transparent allocation across filing, hearing, and miscellaneous fees.

**Legal Basis**: The calculation follows established precedents and court schedules.
**Next Steps**: Review the detailed breakdown and consider settlement negotiations.

This enhancement provides additional context while preserving calculation accuracy."""

    async def validate_response(
        self, response: AIResponse, expected_format: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Validate AI response"""
        if not response.content:
            return False
        if not response.service_type:
            return False
        if response.tokens_used < 0:
            return False
        return True

    async def health_check(self) -> bool:
        """Check if AI service is functioning"""
        try:
            test_request = AIRequest(
                service_type=AIServiceType.CONVERSATION, prompt="test", context={}
            )
            response = await self.generate(test_request)
            return await self.validate_response(response)
        except Exception:
            return False

    def get_call_count(self) -> int:
        """Get number of generate() calls made"""
        return self._call_count

    def reset_call_count(self) -> None:
        """Reset call counter"""
        self._call_count = 0
