"""
Legal MCP Server - Phase 1
Legal Advisory System v6.5

Wraps existing v6 components as MCP resources and tools:
- Logic tree nodes → MCP resources
- Order 21 calculator → MCP tool
- Citation validator → MCP tool
- Pattern extractor → MCP tool
"""

from typing import Any, Dict, List, Optional
from decimal import Decimal
from datetime import datetime
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from pydantic import BaseModel

from backend.common_services.logging_config import get_logger
from backend.common_services import (
    LogicTreeFramework,
    ModuleRegistry,
    SingaporeJurisdiction,
)
from backend.modules.order_21 import Order21Module
from backend.mykraws.response_validator import ResponseValidator
from backend.common_services.pattern_extractor import PatternExtractor

logger = get_logger(__name__)


# ============================================
# DATA MODELS
# ============================================


class LogicTreeNodeResource(BaseModel):
    """Resource model for logic tree nodes"""
    node_id: str
    citation: str
    what: List[Dict[str, Any]]
    which: List[Dict[str, Any]]
    if_then: List[Dict[str, Any]]
    modality: List[Dict[str, Any]]
    given: List[Dict[str, Any]]
    why: List[Dict[str, Any]]


class Order21CalculationResult(BaseModel):
    """Result from Order 21 cost calculation"""
    total_costs: float
    cost_range_min: float
    cost_range_max: float
    calculation_basis: str
    court_level: str
    claim_amount: float
    case_type: str
    # Enhanced audit trail
    calculation_steps: List[str]
    assumptions: List[str]
    rules_applied: List[str]
    confidence: str
    timestamp: str


class CitationValidationResult(BaseModel):
    """Result from citation validation"""
    citation: str
    is_valid: bool
    normalized_citation: Optional[str]
    error_message: Optional[str]


class InformationExtractionResult(BaseModel):
    """Result from pattern extraction"""
    extracted_fields: Dict[str, Any]
    confidence_scores: Dict[str, float]
    raw_input: str


# ============================================
# MCP SERVER INITIALIZATION
# ============================================


# Global state for MCP server components
_server_state = {
    "tree_framework": None,
    "module_registry": None,
    "order21_module": None,
    "response_validator": None,
    "pattern_extractor": None,
    "singapore_jurisdiction": None,
}


@asynccontextmanager
async def lifespan(app: FastMCP):
    """
    Lifecycle manager for MCP server.

    Startup: Initialize all v6 components
    Shutdown: Cleanup resources
    """
    logger.info("🚀 Starting Legal MCP Server...")

    # Initialize v6 components
    tree_framework = LogicTreeFramework()
    module_registry = ModuleRegistry(tree_framework)

    # Register Order 21 module
    order21_module = Order21Module()
    module_registry.register_module(order21_module)

    # Initialize other components
    response_validator = ResponseValidator(module_registry)
    pattern_extractor = PatternExtractor()
    singapore_jurisdiction = SingaporeJurisdiction(module_registry)

    # Store in global state
    _server_state["tree_framework"] = tree_framework
    _server_state["module_registry"] = module_registry
    _server_state["order21_module"] = order21_module
    _server_state["response_validator"] = response_validator
    _server_state["pattern_extractor"] = pattern_extractor
    _server_state["singapore_jurisdiction"] = singapore_jurisdiction

    logger.info("✅ Legal MCP Server initialized")
    logger.info(f"   - Logic tree nodes: {len(tree_framework.get_module_tree('ORDER_21'))}")
    logger.info(f"   - Registered modules: {module_registry.list_modules()}")
    logger.info(f"   - Jurisdictions: Singapore")

    yield

    # Shutdown cleanup
    logger.info("🛑 Shutting down Legal MCP Server...")
    _server_state.clear()


# Create MCP server instance
mcp = FastMCP(
    "Singapore Legal RAG Server",
    lifespan=lifespan
)


# ============================================
# MCP RESOURCES (Read-only data)
# ============================================


@mcp.resource("legal://rules/ORDER_21/{node_id}")
async def get_logic_tree_node(node_id: str) -> str:
    """
    Retrieve a specific logic tree node by ID.

    Returns complete node with all 6 logical dimensions:
    - WHAT: Definitions and concepts
    - WHICH: Categorizations and types
    - IF-THEN: Conditional rules
    - MODALITY: Requirements (must/may/shall)
    - GIVEN: Contextual conditions
    - WHY: Rationale and purpose

    Args:
        node_id: Logic tree node identifier (e.g., "ORDER_21_RULE_1")

    Returns:
        JSON string with complete node data
    """
    tree_framework = _server_state["tree_framework"]

    # Get all nodes for ORDER_21
    nodes = tree_framework.get_module_tree("ORDER_21")

    # Find matching node
    node = next((n for n in nodes if n.node_id == node_id), None)

    if not node:
        raise ValueError(f"Logic tree node '{node_id}' not found")

    # Convert to dict with all dimensions
    node_data = {
        "node_id": node.node_id,
        "citation": node.citation,
        "what": node.what or [],
        "which": node.which or [],
        "if_then": node.if_then or [],
        "modality": node.modality or [],
        "given": node.given or [],
        "why": node.why or [],
    }

    return str(node_data)


@mcp.resource("legal://modules/ORDER_21")
async def get_module_metadata() -> str:
    """
    Retrieve Order 21 module metadata.

    Returns:
        JSON string with module information
    """
    module_registry = _server_state["module_registry"]
    module = module_registry.get_module("ORDER_21")

    if not module:
        raise ValueError("ORDER_21 module not found")

    metadata = {
        "module_id": module.metadata.module_id,
        "module_name": module.metadata.module_name,
        "version": module.metadata.version,
        "status": module.metadata.status.value,
        "description": module.metadata.description,
        "effective_date": module.metadata.effective_date,
        "last_updated": module.metadata.last_updated,
        "field_requirements": [
            {
                "field_name": fr.field_name,
                "field_type": fr.field_type,
                "description": fr.description,
                "required": fr.required,
            }
            for fr in module.get_field_requirements()
        ],
    }

    return str(metadata)


@mcp.resource("legal://jurisdiction/singapore")
async def get_singapore_jurisdiction() -> str:
    """
    Retrieve Singapore jurisdiction configuration.

    Returns:
        JSON string with jurisdiction metadata
    """
    sg_jurisdiction = _server_state["singapore_jurisdiction"]

    jurisdiction_data = {
        "id": sg_jurisdiction.get_id(),
        "name": sg_jurisdiction.get_name(),
        "available_calculators": list(sg_jurisdiction.get_calculators().keys()),
        "citation_format": {
            "rule_pattern": sg_jurisdiction.get_citation_format().rule_pattern,
            "display_format": sg_jurisdiction.get_citation_format().display_format,
        },
        "retrieval_config": {
            "boost_courts": sg_jurisdiction.get_retrieval_config().boost_courts,
            "boost_recent": sg_jurisdiction.get_retrieval_config().boost_recent,
        },
    }

    return str(jurisdiction_data)


# ============================================
# MCP TOOLS (Executable functions)
# ============================================


@mcp.tool()
async def search_logic_tree(
    query: str,
    dimension: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search logic tree nodes by query text.

    Performs keyword matching across all logical dimensions or a specific dimension.

    Args:
        query: Search query text
        dimension: Optional filter (what, which, if_then, modality, given, why)
        limit: Maximum number of results to return

    Returns:
        List of matching logic tree nodes with relevance scores
    """
    tree_framework = _server_state["tree_framework"]
    nodes = tree_framework.get_module_tree("ORDER_21")

    query_lower = query.lower()
    results = []

    for node in nodes:
        relevance = 0.0
        matched_dimensions = []

        # Search across dimensions
        dimensions_to_search = [dimension] if dimension else ["what", "which", "if_then", "modality", "given", "why"]

        for dim in dimensions_to_search:
            dim_data = getattr(node, dim, []) or []
            for item in dim_data:
                text = str(item).lower()
                if query_lower in text:
                    relevance += 1.0
                    matched_dimensions.append(dim)

        # Also search citation
        if query_lower in node.citation.lower():
            relevance += 2.0  # Citation match is more important
            matched_dimensions.append("citation")

        if relevance > 0:
            results.append({
                "node_id": node.node_id,
                "citation": node.citation,
                "relevance_score": relevance,
                "matched_dimensions": list(set(matched_dimensions)),
            })

    # Sort by relevance and limit
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:limit]


@mcp.tool()
async def calculate_order21_costs(
    court_level: str,
    case_type: str,
    claim_amount: float,
    trial_days: Optional[int] = None,
    complexity_level: Optional[str] = "moderate"
) -> Order21CalculationResult:
    """
    Calculate Singapore court costs under Order 21 with full audit trail.

    Provides deterministic cost calculation based on Singapore Rules of Court 2021.

    Args:
        court_level: Court level (High Court, District Court, or Magistrates Court)
        case_type: Type of case (default_judgment_liquidated, summary_judgment, etc.)
        claim_amount: Monetary value of claim in SGD
        trial_days: Number of trial days (optional, for contested trials)
        complexity_level: Complexity (simple, moderate, complex, very_complex)

    Returns:
        Calculation result with costs, breakdown, and audit trail
    """
    order21_module = _server_state["order21_module"]

    # Prepare input fields
    filled_fields = {
        "court_level": court_level,
        "case_type": case_type,
        "claim_amount": claim_amount,
        "complexity_level": complexity_level,
    }

    if trial_days is not None:
        filled_fields["trial_days"] = trial_days

    # Calculate
    result = order21_module.calculate(filled_fields)

    # Return as structured model
    return Order21CalculationResult(
        total_costs=result["total_costs"],
        cost_range_min=result["cost_range_min"],
        cost_range_max=result["cost_range_max"],
        calculation_basis=result["calculation_basis"],
        court_level=result["court_level"],
        claim_amount=result["claim_amount"],
        case_type=result["case_type"],
        calculation_steps=result["calculation_steps"],
        assumptions=result["assumptions"],
        rules_applied=result["rules_applied"],
        confidence=result["confidence"],
        timestamp=result["timestamp"],
    )


@mcp.tool()
async def validate_legal_citation(citation: str) -> CitationValidationResult:
    """
    Validate a legal citation against known Rules of Court.

    Checks if citation exists and is properly formatted according to Singapore standards.

    Args:
        citation: Citation text to validate (e.g., "Order 21, Rule 1")

    Returns:
        Validation result with normalized citation and error message if invalid
    """
    response_validator = _server_state["response_validator"]

    # Normalize citation
    normalized = response_validator._normalize_citation(citation)

    # Check if valid
    is_valid = normalized in response_validator.VALID_RULES

    error_message = None
    if not is_valid:
        error_message = f"Citation '{citation}' not found in Singapore Rules of Court 2021"

    return CitationValidationResult(
        citation=citation,
        is_valid=is_valid,
        normalized_citation=normalized if is_valid else None,
        error_message=error_message,
    )


@mcp.tool()
async def extract_case_information(user_input: str) -> InformationExtractionResult:
    """
    Extract structured case information from natural language input.

    Uses pattern matching to identify:
    - Court level (High Court, District Court, etc.)
    - Case type (default judgment, summary judgment, etc.)
    - Claim amount (monetary values)
    - Other relevant legal information

    Args:
        user_input: Natural language input from user

    Returns:
        Extracted fields with confidence scores
    """
    pattern_extractor = _server_state["pattern_extractor"]

    # Extract fields
    extracted = pattern_extractor.extract_all(user_input, context={})

    # Calculate confidence scores (simple heuristic)
    confidence_scores = {}
    for field, value in extracted.items():
        if value:
            confidence_scores[field] = 0.9  # High confidence for pattern-matched fields
        else:
            confidence_scores[field] = 0.0

    return InformationExtractionResult(
        extracted_fields=extracted,
        confidence_scores=confidence_scores,
        raw_input=user_input,
    )


@mcp.tool()
async def get_rule_context(rule_number: str) -> Dict[str, Any]:
    """
    Get complete context for a specific rule number.

    Retrieves all logic tree nodes related to a rule number with full 6-dimensional context.

    Args:
        rule_number: Rule number (e.g., "Rule 1", "Order 21")

    Returns:
        Dict with matching nodes and their complete logical context
    """
    tree_framework = _server_state["tree_framework"]
    nodes = tree_framework.get_module_tree("ORDER_21")

    # Find nodes matching the rule number
    matching_nodes = []
    for node in nodes:
        if rule_number.lower() in node.citation.lower():
            matching_nodes.append({
                "node_id": node.node_id,
                "citation": node.citation,
                "what": node.what or [],
                "which": node.which or [],
                "if_then": node.if_then or [],
                "modality": node.modality or [],
                "given": node.given or [],
                "why": node.why or [],
            })

    return {
        "rule_number": rule_number,
        "matched_nodes": matching_nodes,
        "count": len(matching_nodes),
    }


# ============================================
# MCP PROMPTS (Reusable templates)
# ============================================


@mcp.prompt(title="Cost Calculation Workflow")
def cost_calculation_prompt(case_summary: str) -> str:
    """
    Generate prompt for comprehensive cost calculation workflow.

    Guides Claude through structured analysis of case costs under Order 21.
    """
    return f"""
Analyze the following case and calculate appropriate costs under Singapore Rules of Court Order 21:

CASE SUMMARY:
{case_summary}

WORKFLOW:
1. Extract case information:
   - Use the extract_case_information tool to identify court level, case type, and claim amount

2. Validate your understanding:
   - Summarize extracted information
   - Ask user for clarification if anything is unclear

3. Search relevant rules:
   - Use search_logic_tree to find applicable Order 21 rules
   - Use get_rule_context to understand rule details

4. Calculate costs:
   - Use calculate_order21_costs with extracted parameters
   - Present calculation with full audit trail

5. Provide comprehensive advice:
   - Explain calculation basis
   - Reference specific rules applied
   - Note any assumptions made
   - Advise on cost taxation process

Use the tools available to provide accurate, well-documented cost advice based on Singapore Rules of Court 2021.
"""


@mcp.prompt(title="Rule Analysis Workflow")
def rule_analysis_prompt(rule_query: str) -> str:
    """
    Generate prompt for detailed rule analysis workflow.

    Guides Claude through structured analysis of Rules of Court provisions.
    """
    return f"""
Analyze the following Singapore Rules of Court query:

QUERY:
{rule_query}

WORKFLOW:
1. Search for relevant rules:
   - Use search_logic_tree to find related provisions
   - Search across all logical dimensions (WHAT, WHICH, IF-THEN, MODALITY, GIVEN, WHY)

2. Get complete rule context:
   - Use get_rule_context for detailed rule information
   - Retrieve legal://rules/ORDER_21/{{node_id}} resources for full text

3. Validate citations:
   - Use validate_legal_citation for any cited rules
   - Ensure all references are accurate

4. Provide structured analysis:
   - WHAT: Define key concepts from the rule
   - WHICH: Categorize types and scenarios
   - IF-THEN: Explain conditional requirements
   - MODALITY: Clarify obligations (must/may/shall)
   - GIVEN: Describe applicable conditions
   - WHY: Explain rationale and purpose

5. Give practical guidance:
   - Explain how the rule applies in practice
   - Provide examples where helpful
   - Note any exceptions or special cases

Reference specific rules and logical dimensions throughout your analysis.
"""


# ============================================
# SERVER FACTORY
# ============================================


def create_legal_mcp_server() -> FastMCP:
    """
    Factory function to create and return the Legal MCP server instance.

    Returns:
        Configured FastMCP server ready to run
    """
    return mcp


# ============================================
# MAIN (for standalone execution)
# ============================================


if __name__ == "__main__":
    # Run MCP server
    logger.info("Starting Legal MCP Server in standalone mode...")
    mcp.run(transport="stdio")
