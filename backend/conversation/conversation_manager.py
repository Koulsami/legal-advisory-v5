"""
Conversation Manager
Legal Advisory System v5.0

Primary orchestrator for all conversations.
Manages dialogue flow and information gathering.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.common_services.analysis_engine import AnalysisEngine
from backend.common_services.module_registry import ModuleRegistry
from backend.hybrid_ai.hybrid_orchestrator import HybridAIOrchestrator
from backend.interfaces import (
    ConversationMessage,
    ConversationResponse,
    ConversationSession,
    ConversationStatus,
    MessageRole,
)


class ConversationManager:
    """
    Primary orchestrator for all conversations.

    Manages:
    - Session lifecycle (create, load, save)
    - Message processing
    - Information extraction
    - Routing to appropriate modules
    - Integration with Hybrid AI and Analysis Engine
    """

    def __init__(
        self,
        hybrid_ai: HybridAIOrchestrator,
        analysis_engine: AnalysisEngine,
        module_registry: ModuleRegistry,
    ):
        """
        Initialize Conversation Manager.

        Args:
            hybrid_ai: Hybrid AI Orchestrator for AI enhancement
            analysis_engine: Analysis Engine for calculations
            module_registry: Module Registry for module selection
        """
        self._hybrid_ai = hybrid_ai
        self._analysis_engine = analysis_engine
        self._module_registry = module_registry

        # In-memory session store (will be replaced with Redis/Database in Phase 7)
        self._sessions: Dict[str, ConversationSession] = {}

        # Statistics
        self._stats = {
            "total_sessions": 0,
            "total_messages": 0,
            "completed_sessions": 0,
        }

    # ============================================
    # SESSION MANAGEMENT
    # ============================================

    def create_session(self, user_id: str) -> ConversationSession:
        """
        Create new conversation session.

        Args:
            user_id: User identifier

        Returns:
            New ConversationSession
        """
        session_id = str(uuid.uuid4())
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status=ConversationStatus.ACTIVE,
        )

        self._sessions[session_id] = session
        self._stats["total_sessions"] += 1

        return session

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        Retrieve existing session.

        Args:
            session_id: Session identifier

        Returns:
            ConversationSession if exists, None otherwise
        """
        return self._sessions.get(session_id)

    def save_session(self, session: ConversationSession) -> None:
        """
        Save session state.

        Args:
            session: Session to save
        """
        session.updated_at = datetime.utcnow()
        self._sessions[session.session_id] = session

    def list_sessions(self, user_id: Optional[str] = None) -> List[ConversationSession]:
        """
        List all sessions, optionally filtered by user.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of ConversationSession objects
        """
        sessions = list(self._sessions.values())
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        return sessions

    # ============================================
    # MESSAGE PROCESSING
    # ============================================

    async def process_message(
        self, user_message: str, session_id: str
    ) -> ConversationResponse:
        """
        Main entry point for processing user messages.

        Flow:
        1. Load/validate session
        2. Add user message to history
        3. Extract information from message
        4. Determine next action
        5. Execute action (ask question, analyze, or complete)
        6. Save session
        7. Return response

        Args:
            user_message: User's message text
            session_id: Session identifier

        Returns:
            ConversationResponse with assistant's reply and session state
        """
        # Load session
        session = self.get_session(session_id)
        if not session:
            return ConversationResponse(
                message="Session not found. Please start a new conversation.",
                session_id=session_id,
                status=ConversationStatus.ERROR,
                next_action="restart",
            )

        # Add user message to history
        user_msg = ConversationMessage(
            role=MessageRole.USER, content=user_message, timestamp=datetime.utcnow()
        )
        session.messages.append(user_msg)
        self._stats["total_messages"] += 1

        try:
            # Extract information from user message
            await self._extract_information(user_message, session)

            # Determine next action
            next_action = self._determine_next_action(session)

            if next_action == "analyze":
                # Enough information - perform analysis
                response = await self._perform_analysis(session)
            elif next_action == "select_module":
                # Need to select module first
                response = await self._select_module(session)
            else:  # ask_question
                # Need more information
                response = await self._ask_for_information(session)

            # Add assistant message to history
            assistant_msg = ConversationMessage(
                role=MessageRole.ASSISTANT,
                content=response.message,
                timestamp=datetime.utcnow(),
            )
            session.messages.append(assistant_msg)

            # Save session
            self.save_session(session)

            return response

        except Exception as e:
            # Error handling
            session.status = ConversationStatus.ERROR
            self.save_session(session)

            return ConversationResponse(
                message=f"An error occurred: {str(e)}",
                session_id=session_id,
                status=ConversationStatus.ERROR,
                next_action="error",
                metadata={"error": str(e)},
            )

    # ============================================
    # INFORMATION EXTRACTION
    # ============================================

    async def _extract_information(
        self, user_message: str, session: ConversationSession
    ) -> None:
        """
        Extract structured information from user message.

        Uses AI to parse user input and extract field values.

        Args:
            user_message: User's message
            session: Current session
        """
        # Build context for AI
        context = {
            "current_fields": session.filled_fields,
            "module_id": session.module_id,
            "conversation_history": [
                {"role": msg.role.value, "content": msg.content}
                for msg in session.messages[-5:]  # Last 5 messages for context
            ],
        }

        # Get module to understand what fields we're looking for
        if session.module_id:
            module = self._module_registry.get_module(session.module_id)
            if module:
                field_requirements = module.get_field_requirements()
                context["field_requirements"] = [
                    {
                        "field_name": fr.field_name,
                        "field_type": fr.field_type,
                        "description": fr.description,
                    }
                    for fr in field_requirements
                ]

        # For now, use simple keyword extraction
        # In production, this would use AI to intelligently extract fields
        await self._simple_extract(user_message, session)

    async def _simple_extract(
        self, user_message: str, session: ConversationSession
    ) -> None:
        """
        Simple extraction logic (non-AI fallback).

        Looks for keywords and patterns in user message.

        Args:
            user_message: User's message
            session: Current session
        """
        message_lower = user_message.lower()

        # Extract court level
        if "high court" in message_lower:
            session.filled_fields["court_level"] = "High Court"
        elif "district court" in message_lower:
            session.filled_fields["court_level"] = "District Court"
        elif "magistrate" in message_lower:
            session.filled_fields["court_level"] = "Magistrates Court"

        # Extract case type
        if "default judgment" in message_lower or "default judgement" in message_lower:
            session.filled_fields["case_type"] = "default_judgment_liquidated"
        elif "summary judgment" in message_lower or "summary judgement" in message_lower:
            session.filled_fields["case_type"] = "summary_judgment"
        elif "trial" in message_lower or "contested" in message_lower:
            session.filled_fields["case_type"] = "contested_trial"
        elif "interlocutory" in message_lower or "application" in message_lower:
            session.filled_fields["case_type"] = "interlocutory_application"
        elif "appeal" in message_lower:
            session.filled_fields["case_type"] = "appeal"
        elif "striking out" in message_lower or "strike out" in message_lower:
            session.filled_fields["case_type"] = "striking_out"

        # Extract claim amount (look for numbers with $ or SGD)
        import re

        # Pattern: $XX,XXX or SGD XX,XXX or just numbers
        amount_patterns = [
            r"\$\s*([0-9,]+(?:\.[0-9]{2})?)",
            r"SGD\s*([0-9,]+(?:\.[0-9]{2})?)",
            r"([0-9,]+(?:\.[0-9]{2})?)\s*dollars?",
        ]

        for pattern in amount_patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(",", "")
                try:
                    session.filled_fields["claim_amount"] = float(amount_str)
                    break
                except ValueError:
                    pass

        # Extract trial days
        days_pattern = r"([0-9]+)\s*days?"
        match = re.search(days_pattern, message_lower)
        if match and "trial" in message_lower:
            try:
                session.filled_fields["trial_days"] = int(match.group(1))
            except ValueError:
                pass

    # ============================================
    # ACTION DETERMINATION
    # ============================================

    def _determine_next_action(self, session: ConversationSession) -> str:
        """
        Determine what to do next based on session state.

        Returns:
            Action string: "select_module", "ask_question", or "analyze"
        """
        # If no module selected, need to select one
        if not session.module_id:
            return "select_module"

        # Get module to check completeness
        module = self._module_registry.get_module(session.module_id)
        if not module:
            return "select_module"

        # Check if we have enough information
        completeness_score, missing_fields = module.check_completeness(
            session.filled_fields
        )
        session.completeness_score = completeness_score
        session.missing_fields = missing_fields

        # If 60% or more complete, we can analyze
        if completeness_score >= 0.6:
            return "analyze"

        # Otherwise, ask for more information
        return "ask_question"

    # ============================================
    # ACTION HANDLERS
    # ============================================

    async def _select_module(self, session: ConversationSession) -> ConversationResponse:
        """
        Select appropriate module based on conversation so far.

        For now, defaults to ORDER_21 since it's the only module we have.

        Args:
            session: Current session

        Returns:
            ConversationResponse
        """
        # For now, default to ORDER_21 (will be enhanced with module selection logic later)
        session.module_id = "ORDER_21"
        session.module_confidence = 0.9

        # Update status
        session.status = ConversationStatus.INFORMATION_GATHERING

        return ConversationResponse(
            message=(
                "I'll help you calculate legal costs under Order 21 of the Singapore Rules of Court. "
                "To provide an accurate estimate, I need some information about your case. "
                "What type of matter is this? (e.g., default judgment, summary judgment, contested trial)"
            ),
            session_id=session.session_id,
            status=session.status,
            completeness_score=session.completeness_score,
            next_action="ask_question",
        )

    async def _ask_for_information(
        self, session: ConversationSession
    ) -> ConversationResponse:
        """
        Ask for missing information.

        Args:
            session: Current session

        Returns:
            ConversationResponse with questions
        """
        # Get module
        module = self._module_registry.get_module(session.module_id)
        if not module:
            return ConversationResponse(
                message="Unable to find the selected module.",
                session_id=session.session_id,
                status=ConversationStatus.ERROR,
                next_action="restart",
            )

        # Get missing required fields
        field_requirements = module.get_field_requirements()
        required_fields = [fr for fr in field_requirements if fr.required]

        # Find first missing required field
        missing_required = [
            fr
            for fr in required_fields
            if fr.field_name not in session.filled_fields
            or session.filled_fields[fr.field_name] is None
        ]

        if missing_required:
            # Ask about first missing required field
            first_missing = missing_required[0]
            question_templates = module.get_question_templates()

            # Find template for this field
            template = next(
                (qt for qt in question_templates if qt.field_name == first_missing.field_name),
                None,
            )

            if template:
                question = template.template
            else:
                # Fallback question
                question = f"What is the {first_missing.field_name.replace('_', ' ')}?"

            return ConversationResponse(
                message=question,
                session_id=session.session_id,
                status=ConversationStatus.INFORMATION_GATHERING,
                completeness_score=session.completeness_score,
                next_action="ask_question",
                questions=[question],
            )
        else:
            # All required fields filled, proceed to analysis
            return await self._perform_analysis(session)

    async def _perform_analysis(
        self, session: ConversationSession
    ) -> ConversationResponse:
        """
        Perform analysis with current information.

        Args:
            session: Current session

        Returns:
            ConversationResponse with results
        """
        # Update status
        session.status = ConversationStatus.ANALYZING

        # Get module
        module = self._module_registry.get_module(session.module_id)
        if not module:
            return ConversationResponse(
                message="Unable to find the selected module.",
                session_id=session.session_id,
                status=ConversationStatus.ERROR,
                next_action="restart",
            )

        # Validate fields
        is_valid, errors = module.validate_fields(session.filled_fields)
        if not is_valid:
            error_msg = "Please provide the following information:\n" + "\n".join(
                f"- {error}" for error in errors
            )
            session.status = ConversationStatus.INFORMATION_GATHERING
            return ConversationResponse(
                message=error_msg,
                session_id=session.session_id,
                status=session.status,
                completeness_score=session.completeness_score,
                next_action="ask_question",
                metadata={"validation_errors": errors},
            )

        # Perform calculation (100% accurate)
        calculation_result = module.calculate(session.filled_fields)
        session.calculation_result = calculation_result

        # Get arguments and recommendations
        arguments = module.get_arguments(calculation_result, session.filled_fields)
        recommendations = module.get_recommendations(calculation_result)

        # Build comprehensive result
        result = {
            "calculation": calculation_result,
            "arguments": arguments,
            "recommendations": recommendations,
        }
        session.analysis_result = result

        # Enhance with AI
        enhanced_result = await self._hybrid_ai.enhance_and_validate(calculation_result)

        # Build response message
        total_costs = calculation_result.get("total_costs", 0)
        cost_range_min = calculation_result.get("cost_range_min", 0)
        cost_range_max = calculation_result.get("cost_range_max", 0)
        court_level = calculation_result.get("court_level", "")
        case_type = calculation_result.get("case_type", "").replace("_", " ").title()

        message = f"""Based on the information provided, here are the cost calculations:

**Case Details:**
- Court: {court_level}
- Case Type: {case_type}
- Claim Amount: ${calculation_result.get('claim_amount', 0):,.2f}

**Cost Estimate:**
- Estimated Costs: ${total_costs:,.2f}
- Cost Range: ${cost_range_min:,.2f} - ${cost_range_max:,.2f}
- Basis: {calculation_result.get('calculation_basis', 'N/A')}

**Recommendations:**
{chr(10).join(f'- {rec}' for rec in recommendations[:3])}

{enhanced_result.enhanced_result.enhanced_explanation if enhanced_result.enhanced_result.enhanced_explanation else ''}

Would you like more details on any aspect of these costs?"""

        # Update status to complete
        session.status = ConversationStatus.COMPLETE
        self._stats["completed_sessions"] += 1

        return ConversationResponse(
            message=message,
            session_id=session.session_id,
            status=session.status,
            completeness_score=1.0,
            next_action="complete",
            result=result,
            metadata={"enhanced": enhanced_result.is_safe},
        )

    # ============================================
    # STATISTICS
    # ============================================

    def get_statistics(self) -> Dict[str, Any]:
        """Return conversation statistics"""
        return {
            **self._stats,
            "active_sessions": len([s for s in self._sessions.values() if s.status == ConversationStatus.ACTIVE]),
            "total_sessions_stored": len(self._sessions),
        }
