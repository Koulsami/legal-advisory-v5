"""
Tests for Claude AI Service
Legal Advisory System v5.0

Comprehensive tests for ClaudeAIService implementation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from backend.hybrid_ai.claude_ai_service import ClaudeAIService, ClaudeAIServiceError
from backend.interfaces.data_structures import (
    AIRequest,
    AIResponse,
    AIProvider,
    AIServiceType
)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def mock_service():
    """Create ClaudeAIService in mock mode (no API key)"""
    return ClaudeAIService(api_key=None)


@pytest.fixture
def service_with_key():
    """Create ClaudeAIService with mock API key"""
    return ClaudeAIService(api_key="sk-ant-test-key-123")


@pytest.fixture
def sample_request():
    """Create sample AIRequest"""
    return AIRequest(
        service_type=AIServiceType.ENHANCEMENT,
        prompt="Explain this legal calculation: cost = $100",
        context={"case_type": "order_21"},
        max_tokens=1000,
        temperature=0.7
    )


@pytest.fixture
def mock_anthropic_client():
    """Create mock Anthropic client"""
    mock_client = AsyncMock()

    # Mock message response
    mock_message = Mock()
    mock_message.content = [Mock(text="This is a test response from Claude.")]
    mock_message.stop_reason = "end_turn"
    mock_message.id = "msg_123"
    mock_message.usage = Mock(input_tokens=50, output_tokens=20)

    mock_client.messages.create = AsyncMock(return_value=mock_message)

    return mock_client


# ============================================
# INITIALIZATION TESTS
# ============================================

def test_init_without_api_key():
    """Test initialization without API key (mock mode)"""
    service = ClaudeAIService(api_key=None)

    assert service.provider == AIProvider.ANTHROPIC_CLAUDE
    assert service.model_name == ClaudeAIService.DEFAULT_MODEL
    assert service._client is None  # No client in mock mode


def test_init_with_api_key():
    """Test initialization with API key"""
    service = ClaudeAIService(api_key="sk-ant-test")

    assert service.provider == AIProvider.ANTHROPIC_CLAUDE
    assert service.model_name == ClaudeAIService.DEFAULT_MODEL


def test_init_with_custom_model():
    """Test initialization with custom model"""
    custom_model = "claude-3-opus-20240229"
    service = ClaudeAIService(api_key="sk-ant-test", model=custom_model)

    assert service.model_name == custom_model


def test_init_with_custom_config():
    """Test initialization with custom configuration"""
    service = ClaudeAIService(
        api_key="sk-ant-test",
        model="claude-3-haiku-20240307",
        max_retries=5,
        timeout_seconds=60.0
    )

    assert service._max_retries == 5
    assert service._timeout == 60.0


# ============================================
# PROPERTY TESTS
# ============================================

def test_provider_property(mock_service):
    """Test provider property returns correct value"""
    assert mock_service.provider == AIProvider.ANTHROPIC_CLAUDE


def test_model_name_property(mock_service):
    """Test model_name property returns correct value"""
    assert mock_service.model_name == ClaudeAIService.DEFAULT_MODEL


# ============================================
# GENERATE TESTS (MOCK MODE)
# ============================================

@pytest.mark.asyncio
async def test_generate_mock_response(mock_service, sample_request):
    """Test generate in mock mode returns valid response"""
    response = await mock_service.generate(sample_request)

    assert isinstance(response, AIResponse)
    assert response.content is not None
    assert len(response.content) > 0
    assert response.service_type == AIServiceType.ENHANCEMENT
    assert response.tokens_used > 0
    assert response.finish_reason == "stop"
    assert response.metadata["mock"] is True


@pytest.mark.asyncio
async def test_generate_mock_with_different_prompts(mock_service):
    """Test mock responses vary based on prompt content"""
    # Test explanation prompt
    explain_request = AIRequest(
        service_type=AIServiceType.ENHANCEMENT,
        prompt="Explain this calculation"
    )
    explain_response = await mock_service.generate(explain_request)
    assert "Enhanced explanation" in explain_response.content or "MOCK" in explain_response.content

    # Test validation prompt
    validate_request = AIRequest(
        service_type=AIServiceType.ANALYSIS,
        prompt="Validate this response"
    )
    validate_response = await mock_service.generate(validate_request)
    assert "Validation" in validate_response.content or "MOCK" in validate_response.content

    # Test analysis prompt
    analyze_request = AIRequest(
        service_type=AIServiceType.ANALYSIS,
        prompt="Analyze this case"
    )
    analyze_response = await mock_service.generate(analyze_request)
    assert "Analysis" in analyze_response.content or "MOCK" in analyze_response.content


@pytest.mark.asyncio
async def test_generate_empty_prompt_error(mock_service):
    """Test generate raises error for empty prompt"""
    empty_request = AIRequest(
        service_type=AIServiceType.ENHANCEMENT,
        prompt=""
    )

    with pytest.raises(ClaudeAIServiceError, match="prompt cannot be empty"):
        await mock_service.generate(empty_request)


@pytest.mark.asyncio
async def test_generate_whitespace_prompt_error(mock_service):
    """Test generate raises error for whitespace-only prompt"""
    whitespace_request = AIRequest(
        service_type=AIServiceType.ENHANCEMENT,
        prompt="   \n\t  "
    )

    with pytest.raises(ClaudeAIServiceError, match="prompt cannot be empty"):
        await mock_service.generate(whitespace_request)


# ============================================
# GENERATE TESTS (WITH API CLIENT)
# ============================================

@pytest.mark.asyncio
async def test_generate_with_api_client(service_with_key, sample_request, mock_anthropic_client):
    """Test generate with mocked Anthropic client"""
    # Replace client with mock
    service_with_key._client = mock_anthropic_client

    response = await service_with_key.generate(sample_request)

    assert isinstance(response, AIResponse)
    assert response.content == "This is a test response from Claude."
    assert response.tokens_used == 70  # 50 input + 20 output
    assert response.finish_reason == "end_turn"
    assert response.metadata["model"] == ClaudeAIService.DEFAULT_MODEL
    assert response.metadata["message_id"] == "msg_123"


@pytest.mark.asyncio
async def test_generate_with_custom_model_in_request(service_with_key, mock_anthropic_client):
    """Test generate respects model specified in request"""
    service_with_key._client = mock_anthropic_client

    custom_request = AIRequest(
        service_type=AIServiceType.ENHANCEMENT,
        prompt="Test prompt",
        model="claude-3-opus-20240229"
    )

    await service_with_key.generate(custom_request)

    # Verify the custom model was used
    call_args = mock_anthropic_client.messages.create.call_args
    assert call_args.kwargs["model"] == "claude-3-opus-20240229"


@pytest.mark.asyncio
async def test_generate_with_context(service_with_key, mock_anthropic_client):
    """Test generate passes context correctly"""
    service_with_key._client = mock_anthropic_client

    request_with_context = AIRequest(
        service_type=AIServiceType.ANALYSIS,
        prompt="Analyze this",
        context={
            "system_message": "You are a legal expert.",
            "case_id": "12345"
        }
    )

    await service_with_key.generate(request_with_context)

    # Verify system message was passed
    call_args = mock_anthropic_client.messages.create.call_args
    assert call_args.kwargs["system"] == "You are a legal expert."


@pytest.mark.asyncio
async def test_generate_updates_statistics(mock_service, sample_request):
    """Test generate updates service statistics"""
    initial_stats = mock_service.get_statistics()
    initial_requests = initial_stats["total_requests"]

    await mock_service.generate(sample_request)

    updated_stats = mock_service.get_statistics()
    assert updated_stats["total_requests"] == initial_requests + 1
    assert updated_stats["total_tokens"] > 0


# ============================================
# RETRY TESTS
# ============================================

@pytest.mark.asyncio
async def test_generate_retries_on_failure(service_with_key, sample_request):
    """Test generate retries on API failure"""
    # Create mock client that fails twice then succeeds
    mock_client = AsyncMock()

    call_count = 0
    async def mock_create(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("API error")

        # Success on third try
        mock_message = Mock()
        mock_message.content = [Mock(text="Success after retries")]
        mock_message.stop_reason = "end_turn"
        mock_message.id = "msg_retry"
        mock_message.usage = Mock(input_tokens=10, output_tokens=5)
        return mock_message

    mock_client.messages.create = mock_create
    service_with_key._client = mock_client

    response = await service_with_key.generate(sample_request)

    assert response.content == "Success after retries"
    assert call_count == 3


@pytest.mark.asyncio
async def test_generate_fails_after_max_retries(service_with_key, sample_request):
    """Test generate fails after exhausting retries"""
    # Create mock client that always fails
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(side_effect=Exception("Persistent error"))

    service_with_key._client = mock_client
    service_with_key._max_retries = 2  # Reduce retries for faster test

    with pytest.raises(ClaudeAIServiceError, match="All 2 attempts failed"):
        await service_with_key.generate(sample_request)

    # Verify failed request was counted
    stats = service_with_key.get_statistics()
    assert stats["failed_requests"] == 1


# ============================================
# VALIDATION TESTS
# ============================================

@pytest.mark.asyncio
async def test_validate_response_valid(mock_service):
    """Test validate_response with valid response"""
    valid_response = AIResponse(
        content="This is a valid response with sufficient content.",
        service_type=AIServiceType.ENHANCEMENT,
        tokens_used=100,
        finish_reason="stop"
    )

    is_valid = await mock_service.validate_response(valid_response)
    assert is_valid is True


@pytest.mark.asyncio
async def test_validate_response_empty_content(mock_service):
    """Test validate_response rejects empty content"""
    empty_response = AIResponse(
        content="",
        service_type=AIServiceType.ENHANCEMENT,
        tokens_used=0,
        finish_reason="stop"
    )

    is_valid = await mock_service.validate_response(empty_response)
    assert is_valid is False


@pytest.mark.asyncio
async def test_validate_response_whitespace_only(mock_service):
    """Test validate_response rejects whitespace-only content"""
    whitespace_response = AIResponse(
        content="   \n\t  ",
        service_type=AIServiceType.ENHANCEMENT,
        tokens_used=0,
        finish_reason="stop"
    )

    is_valid = await mock_service.validate_response(whitespace_response)
    assert is_valid is False


@pytest.mark.asyncio
async def test_validate_response_too_short(mock_service):
    """Test validate_response rejects content that's too short"""
    short_response = AIResponse(
        content="Short",  # Less than 10 characters
        service_type=AIServiceType.ENHANCEMENT,
        tokens_used=5,
        finish_reason="stop"
    )

    is_valid = await mock_service.validate_response(short_response)
    assert is_valid is False


@pytest.mark.asyncio
async def test_validate_response_with_format_requirements(mock_service):
    """Test validate_response with expected format"""
    response = AIResponse(
        content="This response contains: calculation and explanation keywords.",
        service_type=AIServiceType.ENHANCEMENT,
        tokens_used=100,
        finish_reason="stop"
    )

    # Valid - contains required keys
    expected_format = {
        "required_keys": ["calculation", "explanation"],
        "min_length": 20
    }
    is_valid = await mock_service.validate_response(response, expected_format)
    assert is_valid is True

    # Invalid - missing required key
    expected_format_missing = {
        "required_keys": ["missing_keyword"]
    }
    is_valid = await mock_service.validate_response(response, expected_format_missing)
    assert is_valid is False


# ============================================
# HEALTH CHECK TESTS
# ============================================

@pytest.mark.asyncio
async def test_health_check_mock_mode(mock_service):
    """Test health_check in mock mode always returns True"""
    is_healthy = await mock_service.health_check()
    assert is_healthy is True


@pytest.mark.asyncio
async def test_health_check_with_client(service_with_key, mock_anthropic_client):
    """Test health_check with API client"""
    service_with_key._client = mock_anthropic_client

    is_healthy = await service_with_key.health_check()
    assert is_healthy is True


@pytest.mark.asyncio
async def test_health_check_failure(service_with_key):
    """Test health_check returns False on failure"""
    # Mock client that raises error
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(side_effect=Exception("Connection error"))

    service_with_key._client = mock_client

    is_healthy = await service_with_key.health_check()
    assert is_healthy is False


# ============================================
# STATISTICS TESTS
# ============================================

def test_get_statistics_initial(mock_service):
    """Test get_statistics returns correct initial values"""
    stats = mock_service.get_statistics()

    assert stats["provider"] == "anthropic_claude"
    assert stats["model"] == ClaudeAIService.DEFAULT_MODEL
    assert stats["total_requests"] == 0
    assert stats["failed_requests"] == 0
    assert stats["success_rate"] == 0.0
    assert stats["total_tokens"] == 0
    assert stats["average_tokens_per_request"] == 0
    assert stats["mock_mode"] is True


@pytest.mark.asyncio
async def test_get_statistics_after_requests(mock_service, sample_request):
    """Test get_statistics after making requests"""
    # Make several requests
    await mock_service.generate(sample_request)
    await mock_service.generate(sample_request)

    stats = mock_service.get_statistics()

    assert stats["total_requests"] == 2
    assert stats["total_tokens"] > 0
    assert stats["success_rate"] == 1.0  # All succeeded


def test_reset_statistics(mock_service):
    """Test reset_statistics clears all counters"""
    # Manually set some statistics
    mock_service._total_requests = 10
    mock_service._failed_requests = 2
    mock_service._total_tokens = 1000

    mock_service.reset_statistics()

    stats = mock_service.get_statistics()
    assert stats["total_requests"] == 0
    assert stats["failed_requests"] == 0
    assert stats["total_tokens"] == 0


# ============================================
# ERROR HANDLING TESTS
# ============================================

def test_claude_ai_service_error():
    """Test ClaudeAIServiceError can be raised and caught"""
    with pytest.raises(ClaudeAIServiceError):
        raise ClaudeAIServiceError("Test error")


@pytest.mark.asyncio
async def test_generate_handles_api_timeout(service_with_key, sample_request):
    """Test generate handles API timeout gracefully"""
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(side_effect=asyncio.TimeoutError("Request timeout"))

    service_with_key._client = mock_client
    service_with_key._max_retries = 1  # Reduce retries for faster test

    with pytest.raises(ClaudeAIServiceError):
        await service_with_key.generate(sample_request)


# ============================================
# INTEGRATION TESTS
# ============================================

@pytest.mark.asyncio
async def test_full_workflow_mock_mode(mock_service):
    """Test complete workflow in mock mode"""
    # 1. Check health
    is_healthy = await mock_service.health_check()
    assert is_healthy is True

    # 2. Generate response
    request = AIRequest(
        service_type=AIServiceType.ENHANCEMENT,
        prompt="Explain: filing fee = $100"
    )
    response = await mock_service.generate(request)

    # 3. Validate response
    is_valid = await mock_service.validate_response(response)
    assert is_valid is True

    # 4. Check statistics
    stats = mock_service.get_statistics()
    assert stats["total_requests"] >= 1
    assert stats["success_rate"] == 1.0


@pytest.mark.asyncio
async def test_concurrent_requests(mock_service):
    """Test service handles concurrent requests"""
    requests = [
        AIRequest(
            service_type=AIServiceType.ENHANCEMENT,
            prompt=f"Request {i}"
        )
        for i in range(5)
    ]

    # Make concurrent requests
    responses = await asyncio.gather(*[
        mock_service.generate(req) for req in requests
    ])

    assert len(responses) == 5
    for response in responses:
        assert isinstance(response, AIResponse)
        assert response.content is not None

    # Verify statistics
    stats = mock_service.get_statistics()
    assert stats["total_requests"] == 5


# ============================================
# EDGE CASE TESTS
# ============================================

@pytest.mark.asyncio
async def test_generate_with_very_long_prompt(mock_service):
    """Test generate handles very long prompts"""
    long_prompt = "A" * 10000  # 10k characters

    request = AIRequest(
        service_type=AIServiceType.ANALYSIS,
        prompt=long_prompt
    )

    response = await mock_service.generate(request)
    assert response.content is not None


@pytest.mark.asyncio
async def test_generate_with_special_characters(mock_service):
    """Test generate handles special characters in prompt"""
    special_prompt = "Test with: !@#$%^&*()[]{}|\\;:'\",.<>?/~`±§"

    request = AIRequest(
        service_type=AIServiceType.ENHANCEMENT,
        prompt=special_prompt
    )

    response = await mock_service.generate(request)
    assert response.content is not None


@pytest.mark.asyncio
async def test_generate_with_unicode(mock_service):
    """Test generate handles Unicode characters"""
    unicode_prompt = "Legal terms: § 123, © 2024, € 1000, 中文, العربية"

    request = AIRequest(
        service_type=AIServiceType.ANALYSIS,
        prompt=unicode_prompt
    )

    response = await mock_service.generate(request)
    assert response.content is not None


def test_multiple_service_instances():
    """Test multiple service instances can coexist"""
    service1 = ClaudeAIService(api_key=None, model="claude-3-opus-20240229")
    service2 = ClaudeAIService(api_key=None, model="claude-3-sonnet-20240229")

    assert service1.model_name != service2.model_name
    assert service1.get_statistics()["total_requests"] == 0
    assert service2.get_statistics()["total_requests"] == 0
