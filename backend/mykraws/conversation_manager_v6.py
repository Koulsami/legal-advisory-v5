"""
4-Phase Conversation Manager v6.0
Legal Advisory System v6.0

Orchestrates the 4-phase conversational flow:
- Phase 1: Greeting & Introduction
- Phase 2: Understanding User Need
- Phase 3: AI-Driven Information Gathering (with validation)
- Phase 4: Specialist Analysis & Comprehensive Advisory
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from backend.common_services.logging_config import get_logger
from backend.mykraws.personality_manager import PersonalityManager
from backend.interfaces import ConversationStatus, MessageRole

logger = get_logger(__name__)


class ConversationPhase(Enum):
    """4-Phase conversation states"""
    GREETING = "greeting"
    ASK_HELP = "ask_help"
    INTERROGATION = "interrogation"
    ANALYSIS = "analysis"
    COMPLETE = "complete"


@dataclass
class ValidationLog:
    """Log entry for AI response validation"""
    timestamp: datetime
    original_response: str
    validation_result: bool
    issues_found: List[str] = field(default_factory=list)
    corrected_response: Optional[str] = None
    correction_attempts: int = 0
    rules_checked_against: List[str] = field(default_factory=list)


@dataclass
class ConversationSessionV6:
    """
    Extended session state for v6.0 4-phase conversation.

    Tracks phase progression, validation history, and user context.
    """
    # Core identifiers
    session_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    # Phase state
    current_phase: ConversationPhase = ConversationPhase.GREETING
    greeting_delivered: bool = False
    help_requested: bool = False
    sufficient_information: bool = False
    analysis_complete: bool = False

    # Module and data
    module_id: Optional[str] = None
    filled_fields: Dict[str, Any] = field(default_factory=dict)

    # Conversation history
    messages: List[Dict[str, Any]] = field(default_factory=list)

    # User context for personalization
    user_context: Dict[str, Any] = field(default_factory=dict)
    # {
    #   "returning_user": bool,
    #   "user_name": str (optional),
    #   "last_visit": datetime (optional)
    # }

    # Validation tracking (CRITICAL for v6.0)
    validation_history: List[ValidationLog] = field(default_factory=list)

    # Analysis results
    calculation_result: Optional[Dict[str, Any]] = None
    analysis_result: Optional[Dict[str, Any]] = None
    completeness_score: float = 0.0

    def add_message(self, role: MessageRole, content: str, validated: bool = True):
        """Add message to conversation history"""
        self.messages.append({
            "role": role.value,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "validated": validated
        })
        self.updated_at = datetime.utcnow()

    def add_validation_log(self, log: ValidationLog):
        """Add validation log entry"""
        self.validation_history.append(log)


class PhaseManager:
    """
    Manages phase state machine and transitions.

    Phase flow:
    GREETING → ASK_HELP → INTERROGATION → ANALYSIS → COMPLETE
    """

    @staticmethod
    def determine_phase(session: ConversationSessionV6) -> ConversationPhase:
        """
        Determine current phase based on session state.

        Args:
            session: Current conversation session

        Returns:
            Current ConversationPhase
        """
        if not session.greeting_delivered:
            return ConversationPhase.GREETING

        if not session.help_requested:
            return ConversationPhase.ASK_HELP

        if not session.sufficient_information:
            return ConversationPhase.INTERROGATION

        if not session.analysis_complete:
            return ConversationPhase.ANALYSIS

        return ConversationPhase.COMPLETE

    @staticmethod
    def can_transition_to_phase_4(session: ConversationSessionV6) -> bool:
        """
        Check if we have sufficient information for Phase 4 analysis.

        Args:
            session: Current session

        Returns:
            True if ready for Phase 4
        """
        # Need module identified
        if not session.module_id:
            return False

        # Need some filled fields
        if not session.filled_fields:
            return False

        # Check completeness score (≥70% threshold per requirements)
        return session.completeness_score >= 0.7


class ConversationManagerV6:
    """
    Main orchestrator for v6.0 4-phase conversational system.

    Responsibilities:
    - Session lifecycle management
    - Phase transition orchestration
    - Integration with MyKraws personality
    - Coordination of AI interrogation and validation
    - Triggering specialist analysis
    """

    def __init__(
        self,
        personality_manager: Optional[PersonalityManager] = None,
        ai_interrogator=None,  # Type hint avoided to prevent circular import
        response_validator=None,
        comprehensive_advisor=None,
        module_registry=None,
        analysis_engine=None
    ):
        """
        Initialize v6 Conversation Manager.

        Args:
            personality_manager: MyKraws personality system
            ai_interrogator: AI interrogation engine
            response_validator: Response validation layer
            comprehensive_advisor: Phase 4 advisory system
            module_registry: Legal module registry
            analysis_engine: Analysis engine for calculations
        """
        self.personality = personality_manager or PersonalityManager()
        self.ai_interrogator = ai_interrogator
        self.validator = response_validator
        self.advisor = comprehensive_advisor
        self.module_registry = module_registry
        self.analysis_engine = analysis_engine

        # In-memory session store (will be replaced with Redis/Database later)
        self._sessions: Dict[str, ConversationSessionV6] = {}

        # Statistics
        self._stats = {
            "total_sessions": 0,
            "total_messages": 0,
            "validation_failures": 0,
            "validation_corrections": 0
        }

        logger.info("ConversationManagerV6 initialized with 4-phase architecture")

    # ============================================
    # SESSION MANAGEMENT
    # ============================================

    def create_session(
        self,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> ConversationSessionV6:
        """
        Create new v6 conversation session.

        Args:
            user_id: User identifier
            user_context: Optional user context for personalization

        Returns:
            New ConversationSessionV6
        """
        session_id = str(uuid.uuid4())
        session = ConversationSessionV6(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            user_context=user_context or {}
        )

        self._sessions[session_id] = session
        self._stats["total_sessions"] += 1

        logger.info(f"Created v6 session: {session_id[:8]}...")
        return session

    def get_session(self, session_id: str) -> Optional[ConversationSessionV6]:
        """Retrieve existing session"""
        return self._sessions.get(session_id)

    def save_session(self, session: ConversationSessionV6) -> None:
        """Save session state"""
        session.updated_at = datetime.utcnow()
        self._sessions[session.session_id] = session

    # ============================================
    # MAIN MESSAGE PROCESSING
    # ============================================

    async def process_message(
        self,
        user_message: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Main entry point for processing user messages in v6 architecture.

        Flow:
        1. Load session
        2. Determine current phase
        3. Route to appropriate phase handler
        4. Save session
        5. Return response

        Args:
            user_message: User's message text
            session_id: Session identifier

        Returns:
            Response dict with message, phase, metadata
        """
        # Load session
        session = self.get_session(session_id)
        if not session:
            return {
                "response": "Session not found. Please start a new conversation.",
                "phase": "error",
                "continue_conversation": False,
                "metadata": {"error": "session_not_found"}
            }

        # Add user message to history (if not greeting phase)
        if session.current_phase != ConversationPhase.GREETING:
            session.add_message(MessageRole.USER, user_message)
            self._stats["total_messages"] += 1

        try:
            # Determine and update current phase
            session.current_phase = PhaseManager.determine_phase(session)

            logger.info(f"[{session_id[:8]}] Phase: {session.current_phase.value}")

            # Route to appropriate phase handler
            if session.current_phase == ConversationPhase.GREETING:
                response = await self._handle_phase_1_greeting(session)

            elif session.current_phase == ConversationPhase.ASK_HELP:
                response = await self._handle_phase_2_ask_help(session, user_message)

            elif session.current_phase == ConversationPhase.INTERROGATION:
                response = await self._handle_phase_3_interrogation(session, user_message)

            elif session.current_phase == ConversationPhase.ANALYSIS:
                response = await self._handle_phase_4_analysis(session)

            else:  # COMPLETE
                response = {
                    "response": "Thank you for using MyKraws! Is there anything else I can help you with?",
                    "phase": "complete",
                    "continue_conversation": False,
                    "metadata": {"session_complete": True}
                }

            # Add assistant message to history
            session.add_message(
                MessageRole.ASSISTANT,
                response["response"],
                validated=response.get("metadata", {}).get("validation_passed", True)
            )

            # Save session
            self.save_session(session)

            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "response": f"I encountered an error. Let me try to help you differently. Could you rephrase that?",
                "phase": "error",
                "continue_conversation": True,
                "metadata": {"error": str(e)}
            }

    # ============================================
    # PHASE HANDLERS
    # ============================================

    async def _handle_phase_1_greeting(
        self,
        session: ConversationSessionV6
    ) -> Dict[str, Any]:
        """
        Phase 1: Greeting & Introduction

        Generate contextual MyKraws greeting.
        """
        logger.info(f"[{session.session_id[:8]}] Generating MyKraws greeting")

        # Generate contextual greeting
        greeting = self.personality.generate_greeting(session.user_context)

        # Mark greeting as delivered
        session.greeting_delivered = True

        return {
            "response": greeting.text,
            "phase": ConversationPhase.GREETING.value,
            "continue_conversation": True,
            "metadata": {
                "greeting_time": greeting.time_of_day.value,
                "returning_user": greeting.is_returning_user,
                "personalized": greeting.includes_name
            }
        }

    async def _handle_phase_2_ask_help(
        self,
        session: ConversationSessionV6,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Phase 2: Understanding User Need

        Ask open-ended help question and identify module.
        """
        logger.info(f"[{session.session_id[:8]}] Asking how to help (Phase 2)")

        # Generate help question
        help_question = self.personality.generate_help_question()

        # If user provided a message, identify module and extract info
        if user_message:
            user_response = user_message

            # Identify module (simple keyword matching for now)
            # TODO: Use AI for better intent recognition
            module_id = self._identify_module(user_response)

            if module_id:
                session.module_id = module_id
                session.help_requested = True

                logger.info(f"[{session.session_id[:8]}] Module identified: {module_id}")

                # CRITICAL: Extract any information from user's initial message
                # User may have provided details like "High Court default judgment for $50k"
                extracted = {}
                if self.ai_interrogator:
                    from backend.common_services.pattern_extractor import PatternExtractor
                    pattern_extractor = PatternExtractor()

                    logger.info(f"[{session.session_id[:8]}] Extracting from: '{user_response}'")

                    extracted = pattern_extractor.extract_all(
                        user_response,
                        context={"current_fields": session.filled_fields}
                    )

                    logger.info(f"[{session.session_id[:8]}] Phase 2 extraction: {len(extracted)} fields found: {list(extracted.keys())}")

                    # Update session with extracted fields
                    for field, value in extracted.items():
                        session.filled_fields[field] = value
                        logger.info(f"[{session.session_id[:8]}] Extracted from Phase 2: {field} = {value}")

                # Acknowledge and transition to Phase 3
                acknowledgment = f"{self.personality.acknowledge_response(user_response)} I can help you with that."
                return {
                    "response": acknowledgment,
                    "phase": ConversationPhase.ASK_HELP.value,
                    "continue_conversation": True,
                    "metadata": {
                        "module_identified": module_id,
                        "transitioning_to_phase_3": True,
                        "fields_extracted": len(extracted) if 'extracted' in locals() else 0
                    }
                }

        # First time asking
        return {
            "response": help_question,
            "phase": ConversationPhase.ASK_HELP.value,
            "continue_conversation": True,
            "metadata": {
                "awaiting_user_need": True
            }
        }

    async def _handle_phase_3_interrogation(
        self,
        session: ConversationSessionV6,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Phase 3: AI-Driven Information Gathering

        Use AI to ask natural questions, validate responses, extract information.
        """
        logger.info(f"[{session.session_id[:8]}] AI interrogation (Phase 3)")

        # Use AI interrogator to generate next question
        # This will be implemented in the AIInterrogator component
        if self.ai_interrogator:
            # AI generates question
            ai_response = await self.ai_interrogator.generate_question(
                session=session,
                user_message=user_message
            )

            # MANDATORY VALIDATION (CRITICAL!)
            if self.validator:
                validation_result = self.validator.validate(
                    ai_response=ai_response,
                    session=session
                )

                # Log validation
                session.add_validation_log(validation_result.log)

                if not validation_result.passed:
                    self._stats["validation_failures"] += 1
                    if validation_result.corrected:
                        self._stats["validation_corrections"] += 1

                # Use validated/corrected response
                validated_response = validation_result.final_response

            else:
                # No validator available - use response as-is (NOT RECOMMENDED!)
                logger.warning("No validator available - AI response not validated!")
                validated_response = ai_response
                validation_result = None

        else:
            # Fallback: use structured questions (no AI available)
            logger.warning("No AI interrogator available - using fallback")
            validated_response = "Could you tell me more about your case?"
            validation_result = None

        # Check if information is sufficient for Phase 4
        if PhaseManager.can_transition_to_phase_4(session):
            session.sufficient_information = True

        return {
            "response": validated_response,
            "phase": ConversationPhase.INTERROGATION.value,
            "continue_conversation": not session.sufficient_information,
            "metadata": {
                "validation_passed": validation_result.passed if validation_result else None,
                "information_completeness": session.completeness_score,
                "fields_filled": list(session.filled_fields.keys()),
                "ready_for_analysis": session.sufficient_information
            }
        }

    async def _handle_phase_4_analysis(
        self,
        session: ConversationSessionV6
    ) -> Dict[str, Any]:
        """
        Phase 4: Specialist Analysis & Comprehensive Advisory

        Perform accurate calculation and generate comprehensive legal advisory.
        """
        logger.info(f"[{session.session_id[:8]}] Specialist analysis (Phase 4)")

        # Use analysis engine for 100% accurate calculation
        if self.analysis_engine and session.module_id:
            calculation_result = await self.analysis_engine.analyze_with_module_id(
                module_id=session.module_id,
                filled_fields=session.filled_fields,
                enhance_with_ai=False  # v6 handles AI separately
            )
            session.calculation_result = calculation_result

        else:
            logger.error("No analysis engine or module_id - cannot calculate")
            return {
                "response": "I'm sorry, I couldn't complete the analysis. Please try again.",
                "phase": "error",
                "continue_conversation": False,
                "metadata": {"error": "missing_analysis_engine_or_module"}
            }

        # Use comprehensive advisor for rich explanation
        if self.advisor:
            advisory_response = await self.advisor.generate_advisory(
                calculation_result=calculation_result,
                filled_fields=session.filled_fields,
                module_id=session.module_id
            )
            session.analysis_result = advisory_response

        else:
            # Fallback: simple explanation
            advisory_response = f"**Total Costs:** ${calculation_result.get('total_costs', 0):,.2f}"

        # Mark analysis as complete
        session.analysis_complete = True

        return {
            "response": advisory_response,
            "phase": ConversationPhase.ANALYSIS.value,
            "continue_conversation": False,
            "metadata": {
                "calculation_complete": True,
                "total_costs": calculation_result.get("total_costs", 0),
                "analysis_complete": True
            }
        }

    # ============================================
    # HELPER METHODS
    # ============================================

    def _identify_module(self, user_message: str) -> Optional[str]:
        """
        Identify which legal module is needed based on user message.

        Simple keyword matching for now.
        TODO: Use AI for better intent recognition.

        Args:
            user_message: User's message describing their need

        Returns:
            Module ID or None
        """
        message_lower = user_message.lower()

        # Keywords for Order 21 (legal costs)
        cost_keywords = [
            "cost", "costs", "fee", "fees", "bill", "billing",
            "order 21", "legal cost", "party-party"
        ]

        if any(keyword in message_lower for keyword in cost_keywords):
            return "ORDER_21"

        # Default to ORDER_21 for now (only module we have)
        return "ORDER_21"

    def get_statistics(self) -> Dict[str, Any]:
        """Return conversation statistics"""
        return {
            **self._stats,
            "active_sessions": len([
                s for s in self._sessions.values()
                if s.current_phase != ConversationPhase.COMPLETE
            ]),
            "total_sessions_stored": len(self._sessions)
        }
