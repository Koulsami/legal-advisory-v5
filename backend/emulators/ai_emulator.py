"""
AI Emulator for testing and development.

Provides deterministic AI responses without making actual API calls.
"""

import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
from backend.interfaces.ai_service import IAIService
from backend.interfaces.data_structures import AIRequest, AIResponse, AIProvider


@dataclass
class AIEmulatorConfig:
    """Configuration for AI emulator behavior"""
    simulate_latency: bool = True
    latency_ms: int = 50
    deterministic: bool = True
    response_templates: Optional[Dict[str, str]] = None


class AIEmulator(IAIService):
    """AI service emulator that returns deterministic responses."""
    
    def __init__(self, config: Optional[AIEmulatorConfig] = None):
        """Initialize AI emulator with configuration"""
        self.config = config or AIEmulatorConfig()
        self._call_count = 0
        
        # Default response templates
        self._templates = self.config.response_templates or {
            "legal_analysis": "Based on the provided information, the legal analysis is: [DETERMINISTIC_RESPONSE]",
            "question": "To better assist you, could you please provide: [DETERMINISTIC_QUESTION]",
            "default": "This is a deterministic AI response for testing purposes."
        }
    
    @property
    def model_name(self) -> str:
        """Return emulator model name"""
        return "emulator-v1"
    
    @property
    def provider(self) -> AIProvider:
        """Return emulator as provider"""
        return AIProvider.CUSTOM
    
    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate a deterministic AI response"""
        # Simulate latency
        if self.config.simulate_latency:
            await asyncio.sleep(self.config.latency_ms / 1000.0)
        
        self._call_count += 1
        
        # Generate deterministic response based on prompt content
        response_content = self._generate_response(request.prompt)
        
        # Calculate token usage
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(response_content.split())
        total_tokens = prompt_tokens + completion_tokens
        
        return AIResponse(
            content=response_content,
            service_type=request.service_type,
            tokens_used=total_tokens,
            finish_reason="stop",
            metadata={
                "model": "emulator-v1",
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens
            }
        )
    
    def _generate_response(self, prompt: str) -> str:
        """Generate deterministic response based on prompt"""
        prompt_lower = prompt.lower()
        
        # Pattern matching for different types of queries
        if "legal" in prompt_lower or "law" in prompt_lower:
            return self._templates["legal_analysis"]
        elif "?" in prompt:
            return self._templates["question"]
        else:
            return self._templates["default"]
    
    def validate_response(self, response: AIResponse) -> bool:
        """Validate emulator response (always valid)"""
        return response.content is not None and len(response.content) > 0
    
    async def health_check(self) -> bool:
        """Check emulator health (always healthy)"""
        return True
    
    def get_call_count(self) -> int:
        """Get number of generate calls made"""
        return self._call_count
    
    def reset(self):
        """Reset emulator state"""
        self._call_count = 0
