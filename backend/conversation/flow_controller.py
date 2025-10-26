"""
Conversation Flow Controller
Legal Advisory System v5.0

Manages conversation state transitions and flow patterns.
"""

from enum import Enum
from typing import Any, Dict, Optional

from backend.interfaces import ConversationSession, ConversationStatus


class FlowState(Enum):
    """Conversation flow states"""

    INITIAL = "initial"
    GREETING = "greeting"
    MODULE_SELECTION = "module_selection"
    INFORMATION_GATHERING = "information_gathering"
    ANALYSIS = "analysis"
    RESULTS_PRESENTATION = "results_presentation"
    FOLLOW_UP = "follow_up"
    COMPLETE = "complete"
    ERROR = "error"


class FlowAction(Enum):
    """Actions that can trigger state transitions"""

    START_CONVERSATION = "start_conversation"
    SELECT_MODULE = "select_module"
    PROVIDE_INFORMATION = "provide_information"
    REQUEST_ANALYSIS = "request_analysis"
    PRESENT_RESULTS = "present_results"
    ASK_FOLLOW_UP = "ask_follow_up"
    END_CONVERSATION = "end_conversation"
    HANDLE_ERROR = "handle_error"


class ConversationFlowController:
    """
    Manages conversation flow and state transitions.

    Implements a state machine for conversation flow with
    clear transition rules and error recovery.
    """

    def __init__(self):
        """Initialize flow controller"""
        # Define valid state transitions
        self._transitions = {
            FlowState.INITIAL: [FlowState.GREETING, FlowState.ERROR],
            FlowState.GREETING: [FlowState.MODULE_SELECTION, FlowState.ERROR],
            FlowState.MODULE_SELECTION: [FlowState.INFORMATION_GATHERING, FlowState.ERROR],
            FlowState.INFORMATION_GATHERING: [
                FlowState.INFORMATION_GATHERING,  # Stay in same state for more questions
                FlowState.ANALYSIS,
                FlowState.ERROR,
            ],
            FlowState.ANALYSIS: [FlowState.RESULTS_PRESENTATION, FlowState.ERROR],
            FlowState.RESULTS_PRESENTATION: [FlowState.FOLLOW_UP, FlowState.COMPLETE, FlowState.ERROR],
            FlowState.FOLLOW_UP: [
                FlowState.INFORMATION_GATHERING,  # User wants to modify
                FlowState.ANALYSIS,  # Reanalyze
                FlowState.COMPLETE,  # Done
                FlowState.ERROR,
            ],
            FlowState.COMPLETE: [FlowState.INITIAL],  # Can start new conversation
            FlowState.ERROR: [FlowState.INITIAL, FlowState.ERROR],  # Can recover or fail again
        }

        # Statistics
        self._stats = {
            "total_transitions": 0,
            "state_counts": {state.value: 0 for state in FlowState},
            "error_recoveries": 0,
        }

    def get_current_state(self, session: ConversationSession) -> FlowState:
        """
        Determine current flow state from session.

        Args:
            session: Conversation session

        Returns:
            Current FlowState
        """
        # Map ConversationStatus to FlowState
        status = session.status

        if status == ConversationStatus.ACTIVE:
            if not session.module_id:
                if len(session.messages) == 0:
                    return FlowState.INITIAL
                return FlowState.GREETING
            elif session.completeness_score < 0.6:
                return FlowState.INFORMATION_GATHERING
            else:
                return FlowState.ANALYSIS

        elif status == ConversationStatus.INFORMATION_GATHERING:
            return FlowState.INFORMATION_GATHERING

        elif status == ConversationStatus.ANALYZING:
            return FlowState.ANALYSIS

        elif status == ConversationStatus.COMPLETE:
            if session.analysis_result:
                return FlowState.RESULTS_PRESENTATION
            return FlowState.COMPLETE

        elif status == ConversationStatus.ERROR:
            return FlowState.ERROR

        return FlowState.INITIAL

    def determine_next_state(
        self,
        current_state: FlowState,
        action: FlowAction,
        session: ConversationSession,
    ) -> FlowState:
        """
        Determine next state based on current state and action.

        Args:
            current_state: Current flow state
            action: Action being performed
            session: Conversation session

        Returns:
            Next FlowState
        """
        # Handle error action
        if action == FlowAction.HANDLE_ERROR:
            return FlowState.ERROR

        # Handle specific actions
        if action == FlowAction.START_CONVERSATION:
            return FlowState.GREETING

        elif action == FlowAction.SELECT_MODULE:
            return FlowState.MODULE_SELECTION

        elif action == FlowAction.PROVIDE_INFORMATION:
            # Check if we have enough information
            if session.completeness_score >= 0.6:
                return FlowState.ANALYSIS
            return FlowState.INFORMATION_GATHERING

        elif action == FlowAction.REQUEST_ANALYSIS:
            return FlowState.ANALYSIS

        elif action == FlowAction.PRESENT_RESULTS:
            return FlowState.RESULTS_PRESENTATION

        elif action == FlowAction.ASK_FOLLOW_UP:
            return FlowState.FOLLOW_UP

        elif action == FlowAction.END_CONVERSATION:
            return FlowState.COMPLETE

        # Default: stay in current state
        return current_state

    def can_transition(self, from_state: FlowState, to_state: FlowState) -> bool:
        """
        Check if transition is valid.

        Args:
            from_state: Current state
            to_state: Desired next state

        Returns:
            True if transition is valid
        """
        valid_transitions = self._transitions.get(from_state, [])
        return to_state in valid_transitions

    def transition(
        self,
        session: ConversationSession,
        to_state: FlowState,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Perform state transition.

        Args:
            session: Conversation session
            to_state: Desired next state
            metadata: Optional metadata about transition

        Returns:
            True if transition successful
        """
        current_state = self.get_current_state(session)

        # Check if transition is valid
        if not self.can_transition(current_state, to_state):
            return False

        # Update session status based on new state
        if to_state == FlowState.INFORMATION_GATHERING:
            session.status = ConversationStatus.INFORMATION_GATHERING
        elif to_state == FlowState.ANALYSIS:
            session.status = ConversationStatus.ANALYZING
        elif to_state == FlowState.COMPLETE:
            session.status = ConversationStatus.COMPLETE
        elif to_state == FlowState.ERROR:
            session.status = ConversationStatus.ERROR
        else:
            session.status = ConversationStatus.ACTIVE

        # Update statistics
        self._stats["total_transitions"] += 1
        self._stats["state_counts"][to_state.value] += 1

        # Store transition metadata in session
        if metadata:
            if "flow_metadata" not in session.metadata:
                session.metadata["flow_metadata"] = []
            session.metadata["flow_metadata"].append(
                {
                    "from": current_state.value,
                    "to": to_state.value,
                    "metadata": metadata,
                }
            )

        return True

    def handle_error(self, session: ConversationSession, error: Exception) -> FlowState:
        """
        Handle error and determine recovery state.

        Args:
            session: Conversation session
            error: Exception that occurred

        Returns:
            Recovery FlowState
        """
        # Log error in session
        if "errors" not in session.metadata:
            session.metadata["errors"] = []

        session.metadata["errors"].append(
            {"error": str(error), "type": type(error).__name__}
        )

        # Update statistics
        self._stats["error_recoveries"] += 1

        # Determine recovery state based on current progress
        if session.completeness_score > 0:
            # Have some information, try to continue gathering
            return FlowState.INFORMATION_GATHERING
        elif session.module_id:
            # Have module selected, go back to gathering
            return FlowState.INFORMATION_GATHERING
        else:
            # Start over
            return FlowState.GREETING

    def get_recommended_action(self, session: ConversationSession) -> str:
        """
        Get recommended next action based on current state.

        Args:
            session: Conversation session

        Returns:
            Recommended action string
        """
        current_state = self.get_current_state(session)

        if current_state == FlowState.INITIAL:
            return "start_conversation"
        elif current_state == FlowState.GREETING:
            return "select_module"
        elif current_state == FlowState.MODULE_SELECTION:
            return "gather_information"
        elif current_state == FlowState.INFORMATION_GATHERING:
            if session.completeness_score >= 0.6:
                return "analyze"
            return "ask_question"
        elif current_state == FlowState.ANALYSIS:
            return "present_results"
        elif current_state == FlowState.RESULTS_PRESENTATION:
            return "ask_follow_up"
        elif current_state == FlowState.FOLLOW_UP:
            return "complete_or_continue"
        elif current_state == FlowState.COMPLETE:
            return "end"
        elif current_state == FlowState.ERROR:
            return "recover"

        return "unknown"

    def get_statistics(self) -> Dict[str, Any]:
        """Get flow controller statistics"""
        return {
            **self._stats,
            "available_states": [state.value for state in FlowState],
            "available_actions": [action.value for action in FlowAction],
        }
