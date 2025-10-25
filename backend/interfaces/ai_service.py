"""
IAIService Interface
Legal Advisory System v5.0

All AI providers (Claude, GPT, emulators) must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .data_structures import AIProvider, AIRequest, AIResponse


class IAIService(ABC):
    """
    Abstract base class for AI services.

    Implementations:
    - ClaudeAIService (Anthropic)
    - GPT4AIService (OpenAI)
    - AIEmulator (for testing)
    """

    @property
    @abstractmethod
    def provider(self) -> AIProvider:
        """Return the AI provider type"""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model name (e.g., 'claude-sonnet-4')"""
        pass

    @abstractmethod
    async def generate(self, request: AIRequest) -> AIResponse:
        """
        Generate AI response.

        Args:
            request: AIRequest with prompt and parameters

        Returns:
            AIResponse with generated content

        Raises:
            AIServiceError: If generation fails
        """
        pass

    @abstractmethod
    async def validate_response(
        self, response: AIResponse, expected_format: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Validate AI response format.

        Args:
            response: AIResponse to validate
            expected_format: Expected format specification

        Returns:
            True if valid, False otherwise
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if AI service is available.

        Returns:
            True if service is healthy
        """
        pass
