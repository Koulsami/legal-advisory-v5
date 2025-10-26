"""
System Builder for v6.0
Legal Advisory System v6.0

Factory pattern to build and wire all v6 components together.
Ensures proper initialization and dependency injection.
"""

from typing import Optional
import os

from backend.common_services.logging_config import get_logger
from backend.common_services.module_registry import ModuleRegistry
from backend.common_services.analysis_engine import AnalysisEngine
from backend.common_services.logic_tree_framework import LogicTreeFramework
from backend.common_services.matching_engine import UniversalMatchingEngine

from backend.hybrid_ai.claude_ai_service import ClaudeAIService
from backend.modules.order_21 import Order21Module

from backend.mykraws.personality_manager import PersonalityManager
from backend.mykraws.conversation_manager_v6 import ConversationManagerV6
from backend.mykraws.ai_interrogator import AIInterrogator
from backend.mykraws.response_validator import ResponseValidator
from backend.mykraws.comprehensive_advisor import ComprehensiveAdvisor

logger = get_logger(__name__)


class SystemBuilderV6:
    """
    Builds complete v6.0 system with all components properly wired.

    Usage:
        builder = SystemBuilderV6()
        conversation_manager = builder.build()
    """

    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Initialize system builder.

        Args:
            anthropic_api_key: Optional Claude API key (uses env var if not provided)
        """
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        logger.info("SystemBuilderV6 initialized")

    def build(self) -> ConversationManagerV6:
        """
        Build complete v6 system.

        Returns:
            Fully initialized ConversationManagerV6
        """
        logger.info("Building Legal Advisory System v6.0...")

        # Step 1: Build foundation components (from v5)
        logger.info("Step 1: Building foundation components...")
        tree_framework = LogicTreeFramework()
        matching_engine = UniversalMatchingEngine()
        module_registry = ModuleRegistry(tree_framework)
        analysis_engine = AnalysisEngine(module_registry, matching_engine, tree_framework)

        # Step 2: Register Order 21 module
        logger.info("Step 2: Registering Order 21 module...")
        order21_module = Order21Module()
        module_registry.register_module(order21_module)

        # Step 3: Build AI service
        logger.info("Step 3: Building AI service...")
        ai_service = self._build_ai_service()

        # Step 4: Build v6 components
        logger.info("Step 4: Building v6 components...")

        # MyKraws personality
        personality_manager = PersonalityManager()

        # Response validator (CRITICAL!)
        response_validator = ResponseValidator(module_registry=module_registry)

        # AI interrogator
        ai_interrogator = AIInterrogator(
            ai_service=ai_service,
            module_registry=module_registry,
            personality_manager=personality_manager
        )

        # Comprehensive advisor
        comprehensive_advisor = ComprehensiveAdvisor(
            module_registry=module_registry
        )

        # Step 5: Build conversation manager v6
        logger.info("Step 5: Building ConversationManagerV6...")
        conversation_manager = ConversationManagerV6(
            personality_manager=personality_manager,
            ai_interrogator=ai_interrogator,
            response_validator=response_validator,
            comprehensive_advisor=comprehensive_advisor,
            module_registry=module_registry,
            analysis_engine=analysis_engine
        )

        logger.info("✅ Legal Advisory System v6.0 built successfully!")
        logger.info(f"   - 4-Phase Conversation: ENABLED")
        logger.info(f"   - MyKraws Personality: ENABLED")
        logger.info(f"   - AI Interrogation: {'ENABLED' if ai_service._client else 'MOCK MODE'}")
        logger.info(f"   - Mandatory Validation: ENABLED")
        logger.info(f"   - Comprehensive Advisory: ENABLED")

        return conversation_manager

    def _build_ai_service(self) -> ClaudeAIService:
        """
        Build AI service (Claude or mock).

        Returns:
            ClaudeAIService instance
        """
        if self.anthropic_api_key:
            logger.info("✅ Real Claude AI enabled (API key found)")
            ai_service = ClaudeAIService(api_key=self.anthropic_api_key)
        else:
            logger.warning("⚠️  No ANTHROPIC_API_KEY - running in MOCK mode")
            logger.warning("⚠️  Set ANTHROPIC_API_KEY for full v6 functionality")
            ai_service = ClaudeAIService(api_key=None)

        return ai_service
