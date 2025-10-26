"""
API Routes
Legal Advisory System v5.0

FastAPI routes for the Legal Advisory System.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import os

from backend.common_services.analysis_engine import AnalysisEngine
from backend.common_services.logic_tree_framework import LogicTreeFramework
from backend.common_services.matching_engine import UniversalMatchingEngine
from backend.common_services.module_registry import ModuleRegistry
from backend.common_services.logging_config import setup_logging, get_logger
from backend.conversation import ConversationManager
from backend.hybrid_ai import ClaudeAIService, HybridAIOrchestrator
from backend.modules.order_21 import Order21Module

# Import v6 routes
from backend.api.routes_v6 import router_v6

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(level=log_level)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Legal Advisory System v5.0",
    description="Hybrid AI-powered legal cost advisory system for Singapore Rules of Court",
    version="5.0.0",
)

# Configure CORS
# Default to Netlify frontend + localhost for development
default_origins = "https://legaladvisory.netlify.app,http://localhost:3000,http://localhost:5173"
allowed_origins = os.getenv("CORS_ORIGINS", default_origins).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
tree_framework = LogicTreeFramework()
matching_engine = UniversalMatchingEngine()
module_registry = ModuleRegistry(tree_framework)
analysis_engine = AnalysisEngine(module_registry, matching_engine, tree_framework)

# Register Order 21 module
order21_module = Order21Module()
module_registry.register_module(order21_module)

# Initialize Hybrid AI with real Claude API if key is provided
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if anthropic_api_key:
    logger.info("✅ Initializing with REAL Claude AI (API key found)")
    ai_service = ClaudeAIService(api_key=anthropic_api_key)
else:
    logger.warning("⚠️  No ANTHROPIC_API_KEY found - running in MOCK mode (degraded UX)")
    logger.warning("⚠️  Set ANTHROPIC_API_KEY environment variable for full functionality")
    ai_service = ClaudeAIService(api_key=None)

hybrid_ai = HybridAIOrchestrator(ai_service)

# Initialize Conversation Manager
conversation_manager = ConversationManager(hybrid_ai, analysis_engine, module_registry)

logger.info("🚀 Legal Advisory System v5.0 initialized")
logger.info(f"📊 Registered modules: {module_registry.list_modules()}")
logger.info(f"🌐 CORS origins: {allowed_origins}")

# Initialize v6 conversation manager for default endpoints
from backend.mykraws.system_builder import SystemBuilderV6
v6_builder = SystemBuilderV6(anthropic_api_key=anthropic_api_key)
conversation_manager_v6 = v6_builder.build()
logger.info("✅ v6 conversation manager initialized for default endpoints")

# Include v6 routes
app.include_router(router_v6)
logger.info("✅ v6 routes mounted at /api/v6/*")


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================


class CreateSessionRequest(BaseModel):
    """Request to create new session"""

    user_id: str


class CreateSessionResponse(BaseModel):
    """Response for session creation"""

    session_id: str
    status: str


class MessageRequest(BaseModel):
    """Request to send message"""

    session_id: str
    message: str


class MessageResponse(BaseModel):
    """Response to message"""

    session_id: str
    message: str
    status: str
    completeness_score: float
    next_action: Optional[str] = None
    questions: List[str] = []
    result: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """Session information response"""

    session_id: str
    user_id: str
    status: str
    module_id: Optional[str]
    filled_fields: Dict[str, Any]
    completeness_score: float
    message_count: int


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    components: Dict[str, str]


# ============================================
# HEALTH ENDPOINTS
# ============================================


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        version="5.0.0",
        components={
            "conversation_manager": "active",
            "hybrid_ai": "active",
            "analysis_engine": "active",
            "module_registry": "active",
            "order21_module": "registered",
        },
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="5.0.0",
        components={
            "conversation_manager": "active",
            "hybrid_ai": "active",
            "analysis_engine": "active",
            "module_registry": "active",
            "order21_module": "registered",
        },
    )


@app.get("/debug/session/{session_id}")
async def debug_session(session_id: str):
    """
    Debug endpoint - shows complete v6 session state for troubleshooting.

    Shows:
    - Current phase
    - Filled fields
    - Completeness score
    - Message history
    - Validation history
    - Module ID

    This helps diagnose why extraction or flow is failing.
    """
    session = conversation_manager_v6.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "current_phase": session.current_phase.value,
        "module_id": session.module_id,
        "filled_fields": session.filled_fields,
        "completeness_score": session.completeness_score,
        "message_count": len(session.messages),
        "messages": [
            {
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"].isoformat() if hasattr(msg["timestamp"], "isoformat") else str(msg["timestamp"]),
            }
            for msg in session.messages
        ],
        "validation_history_count": len(session.validation_history),
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }


# ============================================
# SESSION ENDPOINTS
# ============================================


@app.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create new conversation session (using v6)"""
    session = conversation_manager_v6.create_session(user_id=request.user_id)

    # Auto-deliver greeting
    greeting_response = await conversation_manager_v6.process_message(
        user_message="",
        session_id=session.session_id
    )

    return CreateSessionResponse(
        session_id=session.session_id, status="active"
    )


@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session information (v6)"""
    session = conversation_manager_v6.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        status="active" if session.current_phase != "complete" else "complete",
        module_id=session.module_id,
        filled_fields=session.filled_fields,
        completeness_score=session.completeness_score,
        message_count=len(session.messages),
    )


@app.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(user_id: Optional[str] = None):
    """List all sessions (v6), optionally filtered by user"""
    sessions = conversation_manager_v6.list_sessions(user_id=user_id)

    return [
        SessionResponse(
            session_id=s.session_id,
            user_id=s.user_id,
            status="active" if s.current_phase != "complete" else "complete",
            module_id=s.module_id,
            filled_fields=s.filled_fields,
            completeness_score=s.completeness_score,
            message_count=len(s.messages),
        )
        for s in sessions
    ]


# ============================================
# CONVERSATION ENDPOINTS
# ============================================


@app.post("/messages", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    """Send message in conversation (using v6 conversational AI)"""
    logger.info(f"📨 Message received: session={request.session_id[:8]}, message='{request.message[:50]}...'")

    # Use v6 conversation manager
    response = await conversation_manager_v6.process_message(
        user_message=request.message, session_id=request.session_id
    )

    logger.info(f"💬 v6 Response sent: phase={response['phase']}, continue={response['continue_conversation']}")

    # Map v6 response to v5 response format for frontend compatibility
    session = conversation_manager_v6.get_session(request.session_id)

    return MessageResponse(
        session_id=request.session_id,
        message=response["response"],
        status="active" if response["continue_conversation"] else "complete",
        completeness_score=response["metadata"].get("information_completeness", 0.0),
        next_action=None,
        questions=[],  # v6 asks one question at a time in the message itself
        result=response["metadata"].get("calculation_result") if not response["continue_conversation"] else None,
    )


# ============================================
# STATISTICS ENDPOINTS
# ============================================


@app.get("/statistics")
async def get_statistics():
    """Get system statistics"""
    return {
        "conversation_manager": conversation_manager.get_statistics(),
        "hybrid_ai": hybrid_ai.get_statistics(),
        "analysis_engine": analysis_engine.get_statistics(),
        "module_registry": module_registry.get_statistics(),
    }


# ============================================
# MODULE ENDPOINTS
# ============================================


@app.get("/modules")
async def list_modules():
    """List available modules"""
    modules = module_registry.list_modules()
    return [
        {
            "module_id": m.metadata.module_id,
            "module_name": m.metadata.module_name,
            "version": m.metadata.version,
            "status": m.metadata.status.value,
            "description": m.metadata.description,
        }
        for m in modules
    ]


@app.get("/modules/{module_id}")
async def get_module_info(module_id: str):
    """Get detailed module information"""
    module = module_registry.get_module(module_id)

    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    metadata = module.metadata
    field_requirements = module.get_field_requirements()

    return {
        "module_id": metadata.module_id,
        "module_name": metadata.module_name,
        "version": metadata.version,
        "status": metadata.status.value,
        "description": metadata.description,
        "field_requirements": [
            {
                "field_name": fr.field_name,
                "field_type": fr.field_type,
                "description": fr.description,
                "required": fr.required,
            }
            for fr in field_requirements
        ],
    }
