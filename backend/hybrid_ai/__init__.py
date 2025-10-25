"""
Hybrid AI Layer - AI Enhancement and Validation
Legal Advisory System v5.0

This layer provides AI services that enhance specialized calculations
while maintaining 100% calculation accuracy.

Components:
- ClaudeAIService: Production Claude AI integration
- ResponseEnhancer: Enhances calculation results with AI explanations
- Validation Layer: Ensures AI responses don't contradict calculations
- Hybrid Orchestrator: Coordinates hybrid AI workflow

CRITICAL PRINCIPLE: AI enhances explanations, but NEVER overrides
specialized calculations.
"""

from backend.hybrid_ai.claude_ai_service import ClaudeAIService, ClaudeAIServiceError
from backend.hybrid_ai.response_enhancer import (
    ResponseEnhancer,
    ResponseEnhancerError,
    EnhancementResult
)

__all__ = [
    "ClaudeAIService",
    "ClaudeAIServiceError",
    "ResponseEnhancer",
    "ResponseEnhancerError",
    "EnhancementResult",
]
