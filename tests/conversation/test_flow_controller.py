"""
Tests for Conversation Flow Controller
Legal Advisory System v5.0
"""

import pytest
from backend.conversation.flow_controller import (
    ConversationFlowController,
    FlowState,
    FlowAction,
)
from backend.interfaces import ConversationSession, ConversationStatus


@pytest.fixture
def flow_controller():
    """Create flow controller"""
    return ConversationFlowController()


@pytest.fixture
def sample_session():
    """Create sample session"""
    return ConversationSession(
        session_id="test_session",
        user_id="test_user",
        status=ConversationStatus.ACTIVE,
    )


def test_flow_controller_initialization(flow_controller):
    """Test flow controller initialization"""
    assert flow_controller is not None
    stats = flow_controller.get_statistics()
    assert stats["total_transitions"] == 0


def test_get_current_state_initial(flow_controller, sample_session):
    """Test getting current state for initial session"""
    state = flow_controller.get_current_state(sample_session)
    assert state == FlowState.INITIAL


def test_get_current_state_information_gathering(flow_controller, sample_session):
    """Test state detection for information gathering"""
    sample_session.status = ConversationStatus.INFORMATION_GATHERING
    state = flow_controller.get_current_state(sample_session)
    assert state == FlowState.INFORMATION_GATHERING


def test_determine_next_state(flow_controller, sample_session):
    """Test determining next state"""
    current_state = FlowState.INITIAL
    next_state = flow_controller.determine_next_state(
        current_state, FlowAction.START_CONVERSATION, sample_session
    )
    assert next_state == FlowState.GREETING


def test_can_transition_valid(flow_controller):
    """Test valid transition check"""
    can_transition = flow_controller.can_transition(
        FlowState.INITIAL, FlowState.GREETING
    )
    assert can_transition is True


def test_can_transition_invalid(flow_controller):
    """Test invalid transition check"""
    can_transition = flow_controller.can_transition(
        FlowState.INITIAL, FlowState.ANALYSIS
    )
    assert can_transition is False


def test_transition_success(flow_controller, sample_session):
    """Test successful transition"""
    success = flow_controller.transition(
        sample_session, FlowState.GREETING
    )
    assert success is True
    assert sample_session.status == ConversationStatus.ACTIVE


def test_transition_failure(flow_controller, sample_session):
    """Test failed transition"""
    # Try invalid transition
    success = flow_controller.transition(
        sample_session, FlowState.ANALYSIS  # Can't go directly to analysis
    )
    assert success is False


def test_handle_error(flow_controller, sample_session):
    """Test error handling"""
    error = ValueError("Test error")
    recovery_state = flow_controller.handle_error(sample_session, error)
    
    assert recovery_state in [FlowState.GREETING, FlowState.INFORMATION_GATHERING]
    assert "errors" in sample_session.metadata


def test_get_recommended_action_initial(flow_controller, sample_session):
    """Test recommended action for initial state"""
    action = flow_controller.get_recommended_action(sample_session)
    assert action == "start_conversation"


def test_statistics_tracking(flow_controller, sample_session):
    """Test statistics tracking"""
    initial_stats = flow_controller.get_statistics()
    
    flow_controller.transition(sample_session, FlowState.GREETING)
    
    stats = flow_controller.get_statistics()
    assert stats["total_transitions"] > initial_stats["total_transitions"]


def test_complete_flow(flow_controller, sample_session):
    """Test complete conversation flow"""
    # Start
    flow_controller.transition(sample_session, FlowState.GREETING)
    assert sample_session.status == ConversationStatus.ACTIVE
    
    # Select module
    sample_session.module_id = "ORDER_21"
    flow_controller.transition(sample_session, FlowState.MODULE_SELECTION)
    
    # Gather information
    flow_controller.transition(sample_session, FlowState.INFORMATION_GATHERING)
    assert sample_session.status == ConversationStatus.INFORMATION_GATHERING
    
    # Analysis
    sample_session.completeness_score = 0.8
    flow_controller.transition(sample_session, FlowState.ANALYSIS)
    assert sample_session.status == ConversationStatus.ANALYZING
