"""
Tests for Conversation Manager
Legal Advisory System v5.0
"""

import pytest
from backend.common_services.analysis_engine import AnalysisEngine
from backend.common_services.logic_tree_framework import LogicTreeFramework
from backend.common_services.matching_engine import UniversalMatchingEngine
from backend.common_services.module_registry import ModuleRegistry
from backend.conversation import ConversationManager
from backend.hybrid_ai import ClaudeAIService, HybridAIOrchestrator
from backend.interfaces import ConversationStatus
from backend.modules.order_21 import Order21Module


@pytest.fixture
def order21_module():
    """Create Order 21 module"""
    return Order21Module()


@pytest.fixture
def tree_framework():
    """Create tree framework"""
    return LogicTreeFramework()


@pytest.fixture
def module_registry(order21_module, tree_framework):
    """Create module registry with Order 21"""
    registry = ModuleRegistry(tree_framework)
    registry.register_module(order21_module)
    return registry


@pytest.fixture
def matching_engine():
    """Create matching engine"""
    return UniversalMatchingEngine()


@pytest.fixture
def analysis_engine(module_registry, matching_engine, tree_framework):
    """Create analysis engine"""
    return AnalysisEngine(module_registry, matching_engine, tree_framework)


@pytest.fixture
def hybrid_ai():
    """Create hybrid AI orchestrator (mock mode)"""
    ai_service = ClaudeAIService(api_key=None)  # Mock mode
    return HybridAIOrchestrator(ai_service)


@pytest.fixture
def conversation_manager(hybrid_ai, analysis_engine, module_registry):
    """Create conversation manager"""
    return ConversationManager(hybrid_ai, analysis_engine, module_registry)


# ============================================
# SESSION MANAGEMENT TESTS
# ============================================


def test_create_session(conversation_manager):
    """Test session creation"""
    session = conversation_manager.create_session(user_id="user_123")

    assert session.session_id is not None
    assert session.user_id == "user_123"
    assert session.status == ConversationStatus.ACTIVE
    assert len(session.filled_fields) == 0
    assert len(session.messages) == 0


def test_get_session(conversation_manager):
    """Test retrieving session"""
    # Create session
    created_session = conversation_manager.create_session(user_id="user_123")

    # Retrieve it
    retrieved_session = conversation_manager.get_session(created_session.session_id)

    assert retrieved_session is not None
    assert retrieved_session.session_id == created_session.session_id
    assert retrieved_session.user_id == "user_123"


def test_get_nonexistent_session(conversation_manager):
    """Test retrieving non-existent session"""
    session = conversation_manager.get_session("nonexistent_id")
    assert session is None


def test_save_session(conversation_manager):
    """Test saving session"""
    session = conversation_manager.create_session(user_id="user_123")
    original_updated_at = session.updated_at

    # Modify session
    session.filled_fields["test_field"] = "test_value"

    # Save
    conversation_manager.save_session(session)

    # Retrieve
    saved_session = conversation_manager.get_session(session.session_id)
    assert saved_session.filled_fields["test_field"] == "test_value"
    assert saved_session.updated_at > original_updated_at


def test_list_sessions(conversation_manager):
    """Test listing sessions"""
    # Create multiple sessions
    session1 = conversation_manager.create_session(user_id="user_1")
    session2 = conversation_manager.create_session(user_id="user_2")
    session3 = conversation_manager.create_session(user_id="user_1")

    # List all
    all_sessions = conversation_manager.list_sessions()
    assert len(all_sessions) == 3

    # List by user
    user1_sessions = conversation_manager.list_sessions(user_id="user_1")
    assert len(user1_sessions) == 2
    assert all(s.user_id == "user_1" for s in user1_sessions)


# ============================================
# MESSAGE PROCESSING TESTS
# ============================================


@pytest.mark.asyncio
async def test_process_message_invalid_session(conversation_manager):
    """Test processing message with invalid session"""
    response = await conversation_manager.process_message(
        user_message="Hello", session_id="invalid_session_id"
    )

    assert response.status == ConversationStatus.ERROR
    assert "not found" in response.message.lower()


@pytest.mark.asyncio
async def test_process_initial_message(conversation_manager):
    """Test processing first message in conversation"""
    # Create session
    session = conversation_manager.create_session(user_id="user_123")

    # Send initial message
    response = await conversation_manager.process_message(
        user_message="I need help calculating legal costs", session_id=session.session_id
    )

    assert response.status in [
        ConversationStatus.INFORMATION_GATHERING,
        ConversationStatus.ACTIVE,
    ]
    assert response.message is not None
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_information_extraction_court_level(conversation_manager):
    """Test extracting court level from message"""
    session = conversation_manager.create_session(user_id="user_123")

    # Message with High Court mentioned
    await conversation_manager.process_message(
        user_message="I have a case in the High Court", session_id=session.session_id
    )

    # Check if extracted
    updated_session = conversation_manager.get_session(session.session_id)
    assert updated_session.filled_fields.get("court_level") == "High Court"


@pytest.mark.asyncio
async def test_information_extraction_case_type(conversation_manager):
    """Test extracting case type from message"""
    session = conversation_manager.create_session(user_id="user_123")

    # Message with default judgment mentioned
    await conversation_manager.process_message(
        user_message="I want to file for default judgment",
        session_id=session.session_id,
    )

    # Check if extracted
    updated_session = conversation_manager.get_session(session.session_id)
    assert updated_session.filled_fields.get("case_type") == "default_judgment_liquidated"


@pytest.mark.asyncio
async def test_information_extraction_claim_amount(conversation_manager):
    """Test extracting claim amount from message"""
    session = conversation_manager.create_session(user_id="user_123")

    # Message with amount
    await conversation_manager.process_message(
        user_message="The claim is for $50,000", session_id=session.session_id
    )

    # Check if extracted
    updated_session = conversation_manager.get_session(session.session_id)
    assert updated_session.filled_fields.get("claim_amount") == 50000.0


@pytest.mark.asyncio
async def test_message_history_tracking(conversation_manager):
    """Test that messages are tracked in history"""
    session = conversation_manager.create_session(user_id="user_123")

    # Send first message
    await conversation_manager.process_message(
        user_message="First message", session_id=session.session_id
    )

    # Send second message
    await conversation_manager.process_message(
        user_message="Second message", session_id=session.session_id
    )

    # Check history
    updated_session = conversation_manager.get_session(session.session_id)
    assert len(updated_session.messages) >= 4  # 2 user + 2 assistant minimum


# ============================================
# COMPLETE CONVERSATION FLOW TESTS
# ============================================


@pytest.mark.asyncio
async def test_complete_conversation_flow(conversation_manager):
    """Test complete conversation from start to calculation"""
    # Create session
    session = conversation_manager.create_session(user_id="user_123")

    # Step 1: Initial message
    response1 = await conversation_manager.process_message(
        user_message="I need help with legal costs", session_id=session.session_id
    )
    assert response1.status in [
        ConversationStatus.ACTIVE,
        ConversationStatus.INFORMATION_GATHERING,
    ]

    # Step 2: Provide comprehensive information
    response2 = await conversation_manager.process_message(
        user_message=(
            "I have a default judgment case in the High Court for a claim amount of $50,000"
        ),
        session_id=session.session_id,
    )

    # Should either ask for clarification or complete analysis
    assert response2.status in [
        ConversationStatus.INFORMATION_GATHERING,
        ConversationStatus.ANALYZING,
        ConversationStatus.COMPLETE,
    ]

    # If not complete, provide any missing information
    if response2.status != ConversationStatus.COMPLETE:
        response3 = await conversation_manager.process_message(
            user_message="High Court, default judgment liquidated, $50,000",
            session_id=session.session_id,
        )

        # Check final response
        final_session = conversation_manager.get_session(session.session_id)
        assert final_session is not None


@pytest.mark.asyncio
async def test_conversation_with_all_fields(conversation_manager):
    """Test conversation providing all required fields"""
    session = conversation_manager.create_session(user_id="user_123")

    # Provide complete information
    response = await conversation_manager.process_message(
        user_message=(
            "I need costs for a default judgment in the High Court. "
            "The claim amount is $75,000."
        ),
        session_id=session.session_id,
    )

    # Check that calculation was performed
    final_session = conversation_manager.get_session(session.session_id)
    assert final_session.filled_fields.get("court_level") == "High Court"
    assert final_session.filled_fields.get("case_type") is not None
    assert final_session.filled_fields.get("claim_amount") == 75000.0


# ============================================
# MODULE SELECTION TESTS
# ============================================


@pytest.mark.asyncio
async def test_module_selection(conversation_manager):
    """Test that module is selected automatically"""
    session = conversation_manager.create_session(user_id="user_123")

    # Send message
    await conversation_manager.process_message(
        user_message="I need help with costs", session_id=session.session_id
    )

    # Check module was selected
    updated_session = conversation_manager.get_session(session.session_id)
    assert updated_session.module_id is not None
    assert updated_session.module_id == "ORDER_21"  # Default to Order 21


# ============================================
# ERROR HANDLING TESTS
# ============================================


@pytest.mark.asyncio
async def test_error_handling(conversation_manager):
    """Test error handling in message processing"""
    session = conversation_manager.create_session(user_id="user_123")

    # Force an error by providing invalid session_id after creation
    # (simulate session corruption)
    response = await conversation_manager.process_message(
        user_message="Test message", session_id="corrupted_session"
    )

    assert response.status == ConversationStatus.ERROR


# ============================================
# STATISTICS TESTS
# ============================================


def test_statistics_tracking(conversation_manager):
    """Test statistics are tracked correctly"""
    initial_stats = conversation_manager.get_statistics()

    # Create sessions
    session1 = conversation_manager.create_session(user_id="user_1")
    session2 = conversation_manager.create_session(user_id="user_2")

    stats = conversation_manager.get_statistics()
    assert stats["total_sessions"] == initial_stats["total_sessions"] + 2
    assert stats["active_sessions"] >= 2


@pytest.mark.asyncio
async def test_message_count_statistics(conversation_manager):
    """Test message count tracking"""
    initial_stats = conversation_manager.get_statistics()
    initial_count = initial_stats["total_messages"]

    session = conversation_manager.create_session(user_id="user_123")

    # Send messages
    await conversation_manager.process_message(
        user_message="First message", session_id=session.session_id
    )
    await conversation_manager.process_message(
        user_message="Second message", session_id=session.session_id
    )

    # Check stats
    stats = conversation_manager.get_statistics()
    assert stats["total_messages"] >= initial_count + 2  # At least 2 user messages


# ============================================
# INTEGRATION TESTS
# ============================================


@pytest.mark.asyncio
async def test_integration_with_order21_module(
    conversation_manager, module_registry
):
    """Test integration with Order 21 module"""
    # Verify module is registered
    module = module_registry.get_module("ORDER_21")
    assert module is not None

    # Create session and process message
    session = conversation_manager.create_session(user_id="user_123")

    response = await conversation_manager.process_message(
        user_message=(
            "High Court default judgment for $50,000"
        ),
        session_id=session.session_id,
    )

    # Should successfully process
    assert response.status in [
        ConversationStatus.INFORMATION_GATHERING,
        ConversationStatus.ANALYZING,
        ConversationStatus.COMPLETE,
    ]


@pytest.mark.asyncio
async def test_integration_with_hybrid_ai(conversation_manager):
    """Test integration with Hybrid AI"""
    session = conversation_manager.create_session(user_id="user_123")

    # Provide complete information to trigger analysis
    await conversation_manager.process_message(
        user_message="High Court default judgment liquidated $50,000",
        session_id=session.session_id,
    )

    # Session should have progressed
    updated_session = conversation_manager.get_session(session.session_id)
    assert updated_session is not None
    assert updated_session.module_id == "ORDER_21"


def test_conversation_manager_initialization(
    hybrid_ai, analysis_engine, module_registry
):
    """Test Conversation Manager initialization"""
    manager = ConversationManager(hybrid_ai, analysis_engine, module_registry)

    assert manager._hybrid_ai is not None
    assert manager._analysis_engine is not None
    assert manager._module_registry is not None
    assert len(manager._sessions) == 0
