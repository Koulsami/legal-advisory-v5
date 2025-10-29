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
from backend.modules.order_21.case_law_manager import get_case_law_manager

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
# For local testing, allow all origins
# In production, set CORS_ORIGINS env var to restrict origins
cors_origins = os.getenv("CORS_ORIGINS", "*")
if cors_origins == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = cors_origins.split(",")

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

# Include v6 routes (this initializes the v6 system)
app.include_router(router_v6)
logger.info("✅ v6 routes mounted at /api/v6/*")

# Import the SAME v6 conversation manager instance from routes_v6
# (Don't create a new instance - sessions would be separate!)
from backend.api.routes_v6 import conversation_manager_v6 as conversation_manager_v6
logger.info("✅ Using shared v6 conversation manager from routes_v6")


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


# ============================================
# DIRECT CALCULATION ENDPOINT (like MCP demo)
# ============================================


class DirectCalculationRequest(BaseModel):
    """Request for direct Order 21 calculation"""
    query: str


class DirectCalculationResponse(BaseModel):
    """Response for direct calculation"""
    total_costs: float
    cost_range_min: float
    cost_range_max: float
    calculation_basis: str
    court_level: str
    claim_amount: float
    case_type: str
    calculation_steps: List[str]
    assumptions: List[str]
    rules_applied: List[str]
    confidence: str
    extracted_info: Dict[str, Any]
    case_law: Optional[List[Dict[str, Any]]] = None  # Case law citations


@app.post("/calculate", response_model=DirectCalculationResponse)
async def direct_calculate(request: DirectCalculationRequest):
    """
    Direct Order 21 cost calculation (bypasses conversational flow).

    Works like MCP demo - immediate results from query.
    Example: "Calculate costs for a High Court default judgment with $50,000"
    """
    try:
        logger.info(f"Direct calculation request: {request.query}")

        # Extract information from query
        from backend.common_services.pattern_extractor import PatternExtractor
        extractor = PatternExtractor()
        extracted = extractor.extract_all(request.query, context={})

        logger.info(f"Extracted fields: {extracted}")

        # Determine source: Appendix G or Order 21
        source = extracted.get("source", "order_21")

        if source == "appendix_g":
            # Use Appendix G calculations
            logger.info("Routing to Appendix G (Practice Directions)")
            calculation_result = order21_module.calculate_appendix_g(extracted)
            # Set defaults for response (not used in Appendix G)
            court_level = "N/A"
            case_type = "appendix_g"
            claim_amount = 0
        else:
            # Use Order 21 calculations (original)
            logger.info("Routing to Order 21 (Rules of Court)")

            court_level = extracted.get("court_level", "High Court")
            case_type = extracted.get("case_type", "default_judgment_liquidated")
            claim_amount = extracted.get("claim_amount")

            if not claim_amount:
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract claim amount from query. Please specify an amount (e.g., '$50,000')"
                )

            # Call Order 21 module directly (pass fields as dictionary)
            filled_fields = {
                "court_level": court_level,
                "case_type": case_type,
                "claim_amount": float(claim_amount),
            }

            # Add optional fields if present
            if extracted.get("trial_days"):
                filled_fields["trial_days"] = extracted.get("trial_days")
            if extracted.get("complexity_level"):
                filled_fields["complexity_level"] = extracted.get("complexity_level")
            else:
                filled_fields["complexity_level"] = "moderate"

            calculation_result = order21_module.calculate(filled_fields)

        logger.info(f"Calculation result: Total=${calculation_result.get('total_costs', 0)}")

        return DirectCalculationResponse(
            total_costs=calculation_result.get("total_costs", 0),
            cost_range_min=calculation_result.get("cost_range_min", 0),
            cost_range_max=calculation_result.get("cost_range_max", 0),
            calculation_basis=calculation_result.get("calculation_basis", ""),
            court_level=calculation_result.get("court_level", court_level),
            claim_amount=calculation_result.get("claim_amount", claim_amount),
            case_type=case_type,
            calculation_steps=calculation_result.get("calculation_steps", []),
            assumptions=calculation_result.get("assumptions", []),
            rules_applied=calculation_result.get("rules_applied", []),
            confidence=calculation_result.get("confidence", "high"),
            extracted_info=extracted,
            case_law=calculation_result.get("case_law")  # Include case law citations
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Direct calculation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")


class ChatRequest(BaseModel):
    """Request for conversational chat (like Claude Desktop)"""
    query: str


class ChatResponse(BaseModel):
    """Conversational response (like Claude Desktop)"""
    message: str
    calculation_data: Optional[Dict[str, Any]] = None


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Conversational endpoint with AI-enhanced responses (like Claude Desktop).

    Returns natural language explanation of costs, not just data.
    Example: "Calculate costs for a High Court default judgment with $50,000"
    Example: "Calculate costs for a striking out application"
    """
    try:
        logger.info(f"Chat request: {request.query}")

        # Extract information from query
        from backend.common_services.pattern_extractor import PatternExtractor
        extractor = PatternExtractor()
        extracted = extractor.extract_all(request.query, context={})

        logger.info(f"Extracted fields: {extracted}")

        # Determine source: Appendix G or Order 21
        source = extracted.get("source", "order_21")

        if source == "appendix_g":
            # Use Appendix G calculations
            logger.info("Routing chat to Appendix G (Practice Directions)")
            calculation_result = order21_module.calculate_appendix_g(extracted)
            court_level = "N/A"  # Appendix G doesn't always specify court
            case_type = "Practice Directions"
            claim_amount = 0  # May not be relevant for Appendix G
        else:
            # Use Order 21 calculations (original)
            logger.info("Routing chat to Order 21 (Rules of Court)")

            # Get required fields for Order 21 calculation
            court_level = extracted.get("court_level", "High Court")
            case_type = extracted.get("case_type", "default_judgment_liquidated")
            claim_amount = extracted.get("claim_amount")

            if not claim_amount:
                return ChatResponse(
                    message="I need more information to calculate the costs. Please specify the claim amount (e.g., '$50,000').",
                    calculation_data=None
                )

            # Call Order 21 module directly
            filled_fields = {
                "court_level": court_level,
                "case_type": case_type,
                "claim_amount": float(claim_amount),
            }

            if extracted.get("trial_days"):
                filled_fields["trial_days"] = extracted.get("trial_days")
            if extracted.get("complexity_level"):
                filled_fields["complexity_level"] = extracted.get("complexity_level")
            else:
                filled_fields["complexity_level"] = "moderate"

            calculation_result = order21_module.calculate(filled_fields)

        logger.info(f"Calculation result: Total=${calculation_result.get('total_costs', 0)}")

        # Use Claude AI to generate natural, conversational response
        try:
            from backend.interfaces.data_structures import AIRequest, AIServiceType
            import json

            # Prepare calculation data for Claude
            calc_summary = {
                "total_costs": calculation_result.get("total_costs", 0),
                "cost_range": f"${calculation_result.get('cost_range_min', 0):,.0f} - ${calculation_result.get('cost_range_max', 0):,.0f}",
                "source": source,
                "calculation_basis": calculation_result.get("calculation_basis", ""),
                "calculation_steps": calculation_result.get("calculation_steps", []),
                "rules_applied": calculation_result.get("rules_applied", []),
                "assumptions": calculation_result.get("assumptions", []),
                "confidence": calculation_result.get("confidence", "high")
            }

            # Add source-specific fields
            if source == "order_21":
                calc_summary["court_level"] = court_level
                calc_summary["claim_amount"] = f"${claim_amount:,.0f}"
                calc_summary["case_type"] = case_type.replace('_', ' ')
            else:
                # Appendix G - add relevant extracted fields
                if "application_type" in extracted:
                    calc_summary["application_type"] = extracted["application_type"].replace('_', ' ')
                if "trial_category" in extracted:
                    calc_summary["trial_category"] = extracted["trial_category"].replace('_', ' ')
                if "appeal_level" in extracted:
                    calc_summary["appeal_level"] = extracted["appeal_level"].replace('_', ' ')

            # Create a prompt for Claude to format naturally
            source_description = "Singapore Rules of Court 2021, Order 21" if source == "order_21" else "Singapore Practice Directions (Appendix G)"

            # Extract case law from calculation result
            case_law_context = ""
            if calculation_result.get("case_law"):
                case_law_list = calculation_result["case_law"]
                if case_law_list:
                    case_law_context = "\n\n**Relevant Case Law:**\n"
                    for i, case in enumerate(case_law_list, 1):
                        case_law_context += f"\n{i}. **{case.get('short_name')}** {case.get('citation')}\n"
                        case_law_context += f"   - *Principle:* {case.get('principle')}\n"
                        case_law_context += f"   - *Authority Statement:* {case.get('authority_statement')}\n"

            prompt = f"""You are a legal advisory AI assistant helping with Singapore legal cost calculations.

The user asked: "{request.query}"

I've calculated the costs using {source_description}. Here's the calculation data:

{json.dumps(calc_summary, indent=2)}
{case_law_context}

Please present this information in a natural, conversational way similar to how you would explain it to a client. Include:

1. A brief introduction acknowledging their question
2. The total costs prominently displayed
3. The cost range (these are guidelines, not fixed amounts for Appendix G)
4. A clear explanation of the calculation basis
5. The calculation steps in an easy-to-understand format
6. The rules or guidelines applied
7. Important assumptions they should know
8. **IMPORTANT:** If case law is provided above, naturally cite it in your response using phrases like:
   - "In [Case Name] [Citation], the court held that..."
   - "The principle is confirmed in [Case Name]..."
   - Include the case name, citation, and key principle where relevant
9. For Appendix G cases, mention that these are cost guidelines and may vary based on circumstances
10. End with an offer to help further if needed

Use markdown formatting for structure (headers, bold text, etc.). Be friendly and professional. Make it feel like a conversation, not a data dump.
When citing case law, use proper legal citation format and explain how it supports the cost calculation."""

            # Generate response using Claude AI
            ai_request = AIRequest(
                service_type=AIServiceType.ENHANCEMENT,
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7,
                context={}
            )

            ai_response = await hybrid_ai._ai_service.generate(ai_request)
            conversational_message = ai_response.content

            logger.info("✅ Generated conversational response using Claude AI")

        except Exception as e:
            logger.warning(f"Claude AI generation failed, using fallback: {e}")
            # Fallback to formatted response
            total_costs = calculation_result.get("total_costs", 0)
            cost_range_min = calculation_result.get("cost_range_min", 0)
            cost_range_max = calculation_result.get("cost_range_max", 0)
            calc_basis = calculation_result.get("calculation_basis", "")

            # Build query description based on source
            if source == "appendix_g":
                query_desc = "your query about "
                if "application_type" in extracted:
                    query_desc += f"a {extracted['application_type'].replace('_', ' ')} application"
                elif "trial_category" in extracted:
                    trial_cat = extracted['trial_category'].replace('_', ' ')
                    query_desc += f"a {trial_cat} trial"
                elif "appeal_level" in extracted:
                    appeal_lvl = extracted['appeal_level'].replace('_', ' ')
                    query_desc += f"an appeal at {appeal_lvl}"
                else:
                    query_desc += "the costs"

                source_note = "⚖️ These are cost guidelines from the Singapore Practice Directions (Appendix G). Actual costs may vary based on case complexity and specific circumstances."
            else:
                query_desc = f"your query about a {court_level} {case_type.replace('_', ' ')} with a claim amount of ${claim_amount:,.0f}"
                source_note = "⚖️ These costs are calculated based on the Singapore Rules of Court 2021, Order 21. Actual costs may vary depending on case complexity and specific circumstances."

            conversational_message = f"""Based on {query_desc}, here's what I found:

💰 **Cost Calculation**

The estimated legal costs are **${total_costs:,.0f}**, with a typical range of ${cost_range_min:,.0f} to ${cost_range_max:,.0f}.

**Basis for Calculation:**
{calc_basis}

**Key Rules Applied:**
{chr(10).join('• ' + rule for rule in calculation_result.get('rules_applied', []))}

**Calculation Steps:**
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(calculation_result.get('calculation_steps', [])))}

**Important Assumptions:**
{chr(10).join('• ' + assumption for assumption in calculation_result.get('assumptions', []))}

{source_note}"""

        return ChatResponse(
            message=conversational_message,
            calculation_data=calculation_result
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return ChatResponse(
            message=f"I encountered an error while processing your request: {str(e)}. Please try rephrasing your question or ensure you've included the court level, case type, and claim amount.",
            calculation_data=None
        )


# ============================================
# CASE LAW ENDPOINTS
# ============================================


class CaseLawSearchRequest(BaseModel):
    """Request for case law search"""
    query: str
    max_results: int = 5


class CaseLawSearchResponse(BaseModel):
    """Response for case law search"""
    query: str
    results: List[Dict[str, Any]]
    total_found: int


@app.post("/case-law/search", response_model=CaseLawSearchResponse)
async def search_case_law(request: CaseLawSearchRequest):
    """
    Search case law by query.

    Searches across case names, principles, provisions, keywords, and interpretations.

    Example: "indemnity costs", "costs follow event", "Order 21 r 2"
    """
    try:
        manager = get_case_law_manager()
        matches = manager.search(request.query, request.max_results)

        return CaseLawSearchResponse(
            query=request.query,
            results=manager.format_matches_for_display(matches),
            total_found=len(matches)
        )
    except Exception as e:
        logger.error(f"Case law search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/case-law/provision/{provision}")
async def get_cases_by_provision(provision: str):
    """
    Get all cases interpreting a specific Order 21 provision.

    Example: /case-law/provision/Order 21 r 2(1)
    Example: /case-law/provision/r 2(2)
    """
    try:
        manager = get_case_law_manager()
        cases = manager.search_by_provision(provision)

        return {
            "provision": provision,
            "cases": [manager.format_case_for_display(c) for c in cases],
            "count": len(cases)
        }
    except Exception as e:
        logger.error(f"Case law provision search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/case-law/categories")
async def get_case_law_categories():
    """
    Get all case law categories and database statistics.

    Returns list of categories, statistics, and provisions covered.
    """
    try:
        manager = get_case_law_manager()

        return {
            "categories": manager.get_all_categories(),
            "provisions": manager.get_all_provisions(),
            "keywords": manager.get_all_keywords(),
            "statistics": manager.get_statistics()
        }
    except Exception as e:
        logger.error(f"Case law categories error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")


@app.get("/case-law/category/{category}")
async def get_cases_by_category(category: str):
    """
    Get all cases in a specific category.

    Categories: stay_appeals, courts_discretion, discretion_factors,
    costs_follow_event, indemnity_assessment, conduct_indemnity,
    non_party_costs, solicitor_costs, litigant_in_person, bill_of_costs
    """
    try:
        manager = get_case_law_manager()
        cases = manager.get_cases_by_category(category)

        if not cases:
            raise HTTPException(status_code=404, detail=f"Category '{category}' not found")

        return {
            "category": category,
            "cases": [manager.format_case_for_display(c) for c in cases],
            "count": len(cases)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Case law category error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
