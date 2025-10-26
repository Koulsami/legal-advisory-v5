"""
API Routes for v6.0 - 4-Phase Conversational AI
Legal Advisory System v6.0

New endpoints for MyKraws personality-driven conversation.
Side-by-side deployment with v5 for gradual migration.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime

from backend.common_services.logging_config import get_logger
from backend.mykraws.system_builder import SystemBuilderV6

logger = get_logger(__name__)

# Create v6 router
router_v6 = APIRouter(prefix="/api/v6", tags=["v6"])

# Initialize v6 system (singleton)
logger.info("Initializing v6 system...")
system_builder = SystemBuilderV6()
conversation_manager_v6 = system_builder.build()
logger.info("✅ v6 system initialized")


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class CreateSessionRequestV6(BaseModel):
    """Request to create new v6 session"""
    user_id: str
    user_context: Optional[Dict[str, Any]] = None
    # user_context can include:
    # - returning_user: bool
    # - user_name: str
    # - last_visit: datetime


class CreateSessionResponseV6(BaseModel):
    """Response for v6 session creation"""
    session_id: str
    greeting: str
    phase: str
    metadata: Dict[str, Any]


class MessageRequestV6(BaseModel):
    """Request to send message in v6"""
    session_id: str
    message: str


class MessageResponseV6(BaseModel):
    """Response for v6 message"""
    response: str
    phase: str
    continue_conversation: bool
    metadata: Dict[str, Any]


# ============================================
# ENDPOINTS
# ============================================

@router_v6.post("/session", response_model=CreateSessionResponseV6)
async def create_session_v6(request: CreateSessionRequestV6):
    """
    Create new v6 conversation session with MyKraws.

    Automatically delivers Phase 1 greeting.
    """
    try:
        logger.info(f"Creating v6 session for user: {request.user_id}")

        # Create session
        session = conversation_manager_v6.create_session(
            user_id=request.user_id,
            user_context=request.user_context or {}
        )

        # Process first turn (greeting)
        greeting_response = await conversation_manager_v6.process_message(
            user_message="",  # Empty message triggers greeting
            session_id=session.session_id
        )

        return CreateSessionResponseV6(
            session_id=session.session_id,
            greeting=greeting_response["response"],
            phase=greeting_response["phase"],
            metadata=greeting_response.get("metadata", {})
        )

    except Exception as e:
        logger.error(f"Error creating v6 session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router_v6.post("/message", response_model=MessageResponseV6)
async def send_message_v6(request: MessageRequestV6):
    """
    Send message in v6 conversation.

    Processes through 4-phase flow:
    - Phase 1: Greeting (auto-delivered on session creation)
    - Phase 2: Understanding user need
    - Phase 3: AI interrogation (with validation)
    - Phase 4: Comprehensive advisory
    """
    try:
        logger.info(f"Processing v6 message for session: {request.session_id[:8]}...")

        # Process message
        response = await conversation_manager_v6.process_message(
            user_message=request.message,
            session_id=request.session_id
        )

        return MessageResponseV6(
            response=response["response"],
            phase=response["phase"],
            continue_conversation=response["continue_conversation"],
            metadata=response.get("metadata", {})
        )

    except Exception as e:
        logger.error(f"Error processing v6 message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router_v6.get("/session/{session_id}")
async def get_session_v6(session_id: str):
    """
    Get v6 session details.

    Returns session state including phase, filled fields, etc.
    """
    try:
        session = conversation_manager_v6.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "current_phase": session.current_phase.value,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "module_id": session.module_id,
            "filled_fields": session.filled_fields,
            "completeness_score": session.completeness_score,
            "message_count": len(session.messages),
            "validation_failures": len([
                log for log in session.validation_history
                if not log.validation_result
            ])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting v6 session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router_v6.delete("/session/{session_id}")
async def delete_session_v6(session_id: str):
    """Delete v6 session"""
    try:
        session = conversation_manager_v6.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Remove from in-memory store
        conversation_manager_v6._sessions.pop(session_id, None)

        return {
            "message": "Session deleted successfully",
            "session_id": session_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting v6 session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router_v6.get("/health")
async def health_v6():
    """
    Health check for v6 system.

    Returns system status and statistics.
    """
    try:
        stats = conversation_manager_v6.get_statistics()

        # Get validator stats
        validator_stats = {}
        if conversation_manager_v6.validator:
            validator_stats = conversation_manager_v6.validator.get_statistics()

        return {
            "status": "healthy",
            "version": "6.0.0",
            "architecture": "4-Phase Conversational AI with Validation",
            "components": {
                "personality": "MyKraws",
                "phases": ["greeting", "ask_help", "interrogation", "analysis"],
                "validation": "MANDATORY (100% coverage)",
                "ai_service": "enabled" if conversation_manager_v6.ai_interrogator else "disabled"
            },
            "statistics": {
                **stats,
                "validation": validator_stats
            }
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router_v6.get("/stats")
async def get_statistics_v6():
    """
    Get detailed v6 system statistics.

    Includes conversation stats, validation stats, etc.
    """
    try:
        conv_stats = conversation_manager_v6.get_statistics()
        validator_stats = {}

        if conversation_manager_v6.validator:
            validator_stats = conversation_manager_v6.validator.get_statistics()

        return {
            "conversation": conv_stats,
            "validation": validator_stats,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
