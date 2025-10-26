"""
Conversation Layer
Legal Advisory System v5.0

Manages dialogue flow and information gathering.
"""

from backend.conversation.conversation_manager import ConversationManager
from backend.conversation.deductive_engine import DeductiveQuestioningEngine
from backend.conversation.flow_controller import ConversationFlowController

__all__ = ["ConversationManager", "DeductiveQuestioningEngine", "ConversationFlowController"]
