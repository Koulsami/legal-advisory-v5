"""
Claude AI Service Implementation
Legal Advisory System v5.0

Production implementation of IAIService using Anthropic's Claude API.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
import os

from backend.interfaces.ai_service import IAIService
from backend.interfaces.data_structures import (
    AIRequest,
    AIResponse,
    AIProvider,
    AIServiceType
)

logger = logging.getLogger(__name__)

# Try to import anthropic, but make it optional for testing
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("anthropic package not installed - ClaudeAIService will run in mock mode")


class ClaudeAIServiceError(Exception):
    """Exception raised for Claude AI service errors"""
    pass


class ClaudeAIService(IAIService):
    """
    Production Claude AI Service using Anthropic API.

    Features:
    - Async API calls to Claude
    - Automatic retry with exponential backoff
    - Rate limiting protection
    - Error handling and logging
    - Token usage tracking
    - Health checking

    Example:
        >>> service = ClaudeAIService(api_key="sk-ant-...", model="claude-sonnet-4")
        >>> request = AIRequest(
        ...     service_type=AIServiceType.ENHANCEMENT,
        ...     prompt="Explain this calculation: 1 + 1 = 2"
        ... )
        >>> response = await service.generate(request)
        >>> print(response.content)
    """

    # Default models
    DEFAULT_MODEL = "claude-sonnet-4-20250514"
    FALLBACK_MODEL = "claude-3-5-sonnet-20241022"

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 1.0
    RETRY_BACKOFF_FACTOR = 2.0

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = MAX_RETRIES,
        timeout_seconds: float = 30.0
    ):
        """
        Initialize Claude AI Service.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model name (defaults to claude-sonnet-4-20250514)
            max_retries: Maximum number of retries for failed requests
            timeout_seconds: Request timeout in seconds

        Raises:
            ClaudeAIServiceError: If API key is not provided and not in environment
        """
        # Get API key from parameter or environment
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self._api_key and ANTHROPIC_AVAILABLE:
            raise ClaudeAIServiceError(
                "API key required. Provide via api_key parameter or ANTHROPIC_API_KEY env var"
            )

        self._model = model or self.DEFAULT_MODEL
        self._max_retries = max_retries
        self._timeout = timeout_seconds

        # Initialize client if anthropic is available
        if ANTHROPIC_AVAILABLE and self._api_key:
            self._client = anthropic.AsyncAnthropic(api_key=self._api_key)
        else:
            self._client = None
            logger.warning("Running in mock mode - no real API calls will be made")

        # Statistics
        self._total_requests = 0
        self._total_tokens = 0
        self._failed_requests = 0

        logger.info(f"ClaudeAIService initialized (model: {self._model})")

    @property
    def provider(self) -> AIProvider:
        """Return Anthropic Claude as provider"""
        return AIProvider.ANTHROPIC_CLAUDE

    @property
    def model_name(self) -> str:
        """Return the model name"""
        return self._model

    async def generate(self, request: AIRequest) -> AIResponse:
        """
        Generate AI response using Claude API.

        This method:
        1. Validates the request
        2. Constructs Claude API call
        3. Handles retries with exponential backoff
        4. Parses and returns response

        Args:
            request: AIRequest with prompt and parameters

        Returns:
            AIResponse with generated content

        Raises:
            ClaudeAIServiceError: If generation fails after all retries

        Example:
            >>> request = AIRequest(
            ...     service_type=AIServiceType.ENHANCEMENT,
            ...     prompt="Explain: cost = $100",
            ...     temperature=0.7
            ... )
            >>> response = await service.generate(request)
        """
        self._total_requests += 1

        # Validate request
        if not request.prompt or not request.prompt.strip():
            raise ClaudeAIServiceError("prompt cannot be empty")

        # Use request model if specified, otherwise use service default
        model = request.model or self._model

        logger.debug(
            f"Generating response (model: {model}, "
            f"service_type: {request.service_type.value})"
        )

        # If client is not available, return mock response
        if not self._client:
            response = self._generate_mock_response(request)
            self._total_tokens += response.tokens_used
            return response

        # Retry loop with exponential backoff
        last_error = None
        for attempt in range(self._max_retries):
            try:
                # Make API call
                response = await self._call_claude_api(
                    model=model,
                    prompt=request.prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    context=request.context
                )

                # Update statistics
                self._total_tokens += response.tokens_used

                logger.info(
                    f"Generated response successfully "
                    f"(tokens: {response.tokens_used}, attempt: {attempt + 1})"
                )

                return response

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt + 1}/{self._max_retries} failed: {e}"
                )

                # If not the last attempt, wait before retrying
                if attempt < self._max_retries - 1:
                    delay = self.RETRY_DELAY_SECONDS * (self.RETRY_BACKOFF_FACTOR ** attempt)
                    logger.info(f"Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)

        # All retries failed
        self._failed_requests += 1
        error_msg = f"All {self._max_retries} attempts failed. Last error: {last_error}"
        logger.error(error_msg)
        raise ClaudeAIServiceError(error_msg)

    async def _call_claude_api(
        self,
        model: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
        context: Dict[str, Any]
    ) -> AIResponse:
        """
        Make actual API call to Claude.

        Args:
            model: Model name
            prompt: Prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            context: Additional context

        Returns:
            AIResponse with generated content
        """
        # Construct system message from context if provided
        system_message = context.get("system_message", "")

        # Build API call parameters
        api_params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        # Add system message if provided (must be list format for newer API)
        if system_message:
            if isinstance(system_message, str):
                api_params["system"] = [{"type": "text", "text": system_message}]
            else:
                api_params["system"] = system_message

        # Make API call
        message = await self._client.messages.create(**api_params)

        # Extract response content
        content = message.content[0].text if message.content else ""

        # Calculate token usage
        tokens_used = message.usage.input_tokens + message.usage.output_tokens

        # Construct AIResponse
        return AIResponse(
            content=content,
            service_type=context.get("service_type", AIServiceType.ENHANCEMENT),
            tokens_used=tokens_used,
            finish_reason=message.stop_reason,
            metadata={
                "model": model,
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
                "message_id": message.id
            }
        )

    def _generate_mock_response(self, request: AIRequest) -> AIResponse:
        """
        Generate mock response when Anthropic client is not available.

        Used for testing without API key.

        Args:
            request: AIRequest

        Returns:
            AIResponse with mock content
        """
        logger.debug("Generating mock response (no API client available)")

        # Generate deterministic mock content
        prompt_lower = request.prompt.lower()

        if "explain" in prompt_lower or "enhance" in prompt_lower:
            content = f"[MOCK] Enhanced explanation: {request.prompt[:100]}"
        elif "validate" in prompt_lower:
            content = "[MOCK] Validation passed: The response is consistent with calculations."
        elif "analyze" in prompt_lower:
            content = "[MOCK] Analysis: Based on the provided information..."
        else:
            content = f"[MOCK] Response to: {request.prompt[:100]}"

        # Estimate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(content.split())
        total_tokens = prompt_tokens + completion_tokens

        return AIResponse(
            content=content,
            service_type=request.service_type,
            tokens_used=total_tokens,
            finish_reason="stop",
            metadata={
                "model": "mock-model",
                "input_tokens": prompt_tokens,
                "output_tokens": completion_tokens,
                "mock": True
            }
        )

    async def validate_response(
        self,
        response: AIResponse,
        expected_format: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Validate AI response format.

        Checks:
        - Content is not empty
        - Contains expected keys (if specified)
        - Meets minimum length requirements

        Args:
            response: AIResponse to validate
            expected_format: Expected format specification

        Returns:
            True if valid, False otherwise

        Example:
            >>> response = await service.generate(request)
            >>> is_valid = await service.validate_response(response)
        """
        # Basic validation
        if not response.content or not response.content.strip():
            logger.warning("Validation failed: empty content")
            return False

        # Check minimum length (at least 10 characters)
        if len(response.content.strip()) < 10:
            logger.warning("Validation failed: content too short")
            return False

        # If expected_format is specified, validate against it
        if expected_format:
            # Check for required keys
            required_keys = expected_format.get("required_keys", [])
            for key in required_keys:
                if key not in response.content:
                    logger.warning(f"Validation failed: missing required key '{key}'")
                    return False

            # Check minimum length
            min_length = expected_format.get("min_length", 0)
            if len(response.content) < min_length:
                logger.warning(
                    f"Validation failed: content length {len(response.content)} "
                    f"< minimum {min_length}"
                )
                return False

        return True

    async def health_check(self) -> bool:
        """
        Check if Claude AI service is available.

        Makes a minimal API call to verify connectivity.

        Returns:
            True if service is healthy, False otherwise

        Example:
            >>> is_healthy = await service.health_check()
            >>> if not is_healthy:
            ...     logger.error("Claude AI service is down")
        """
        try:
            # If no client, return True for mock mode
            if not self._client:
                logger.debug("Health check: OK (mock mode)")
                return True

            # Make a minimal API call
            test_request = AIRequest(
                service_type=AIServiceType.ENHANCEMENT,
                prompt="Health check",
                max_tokens=10,
                temperature=0.0
            )

            response = await self.generate(test_request)

            is_healthy = response.content is not None

            if is_healthy:
                logger.debug("Health check: OK")
            else:
                logger.warning("Health check: FAILED (no content)")

            return is_healthy

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get service statistics.

        Returns:
            Dictionary with statistics about service usage

        Example:
            >>> stats = service.get_statistics()
            >>> print(f"Total requests: {stats['total_requests']}")
            >>> print(f"Success rate: {stats['success_rate']:.2%}")
        """
        success_rate = (
            (self._total_requests - self._failed_requests) / self._total_requests
            if self._total_requests > 0
            else 0.0
        )

        return {
            "provider": self.provider.value,
            "model": self._model,
            "total_requests": self._total_requests,
            "failed_requests": self._failed_requests,
            "success_rate": success_rate,
            "total_tokens": self._total_tokens,
            "average_tokens_per_request": (
                self._total_tokens / self._total_requests
                if self._total_requests > 0
                else 0
            ),
            "mock_mode": self._client is None
        }

    def reset_statistics(self):
        """Reset service statistics"""
        self._total_requests = 0
        self._total_tokens = 0
        self._failed_requests = 0
        logger.info("Statistics reset")
