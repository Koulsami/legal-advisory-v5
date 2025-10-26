"""
MyKraws - AI-Driven Legal Advisory with Personality
Legal Advisory System v6.0

4-Phase Conversational AI with Validation:
- Phase 1: Greeting & Introduction
- Phase 2: Understanding User Need
- Phase 3: AI-Driven Information Gathering (with mandatory validation)
- Phase 4: Specialist Analysis & Comprehensive Advisory
"""

from backend.mykraws.personality_manager import PersonalityManager, MyKrawsGreeting
from backend.mykraws.conversation_manager_v6 import ConversationManagerV6, ConversationPhase
from backend.mykraws.ai_interrogator import AIInterrogator
from backend.mykraws.response_validator import ResponseValidator, ValidationResult
from backend.mykraws.comprehensive_advisor import ComprehensiveAdvisor

__all__ = [
    "PersonalityManager",
    "MyKrawsGreeting",
    "ConversationManagerV6",
    "ConversationPhase",
    "AIInterrogator",
    "ResponseValidator",
    "ValidationResult",
    "ComprehensiveAdvisor",
]
