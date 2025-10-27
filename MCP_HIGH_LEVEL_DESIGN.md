# MCP Integration High-Level Design
**Legal Advisory System v6.0 → v7.0 Evolution**

## Executive Summary

This document outlines the phased integration of Model Context Protocol (MCP) into the Legal Advisory System, transforming it from a monolithic v6 architecture to a scalable, standards-based v7 system. Phase 1 wraps existing components with MCP without infrastructure changes (~3 days). Phase 2 adds full RAG capabilities with hybrid retrieval (~6 weeks, when scale demands).

**Key Benefits:**
- ✅ Standardized AI-to-data integration (works with Claude, GPT-4, Gemini)
- ✅ Dynamic tool discovery (no hardcoded function calling)
- ✅ Modular architecture (add jurisdictions without core changes)
- ✅ Future-proof (prepare for multi-jurisdiction, multi-model)

---

## Current State: v6.0 Architecture

### Components
```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │         ConversationManagerV6                   │   │
│  │  ┌───────────┐  ┌──────────────┐              │   │
│  │  │ Phase 1-2 │  │   Phase 3    │              │   │
│  │  │ MyKraws   │  │ AIInterrogator│              │   │
│  │  │Personality│  │  (Questions)  │              │   │
│  │  └───────────┘  └──────────────┘              │   │
│  │  ┌───────────┐  ┌──────────────┐              │   │
│  │  │ Phase 4   │  │  Validation  │              │   │
│  │  │ Analysis  │  │   (100%)     │              │   │
│  │  └───────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │           Common Services Layer                 │   │
│  │  ┌──────────────┐  ┌──────────────┐           │   │
│  │  │ Logic Tree   │  │   Module     │           │   │
│  │  │  Framework   │  │   Registry   │           │   │
│  │  │  (38 nodes)  │  │              │           │   │
│  │  └──────────────┘  └──────────────┘           │   │
│  │  ┌──────────────┐  ┌──────────────┐           │   │
│  │  │   Pattern    │  │   Analysis   │           │   │
│  │  │  Extractor   │  │    Engine    │           │   │
│  │  └──────────────┘  └──────────────┘           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │          Legal Modules Layer                    │   │
│  │  ┌──────────────┐                               │   │
│  │  │  Order 21    │  • calculate()                │   │
│  │  │   Module     │  • Audit trail                │   │
│  │  │              │  • Rules applied              │   │
│  │  └──────────────┘                               │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │           Hybrid AI Layer                       │   │
│  │  ┌──────────────┐                               │   │
│  │  │ ClaudeAI     │  • Anthropic API              │   │
│  │  │  Service     │  • Function calling           │   │
│  │  │              │  • (Traditional)              │   │
│  │  └──────────────┘                               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         ↓
    Railway Deployment
    ~$20/month
```

### Current Capabilities
- ✅ 4-phase conversational flow
- ✅ MyKraws personality system
- ✅ Logic tree with 6 logical dimensions (38 nodes)
- ✅ Order 21 cost calculator
- ✅ Pattern extraction
- ✅ 100% response validation
- ✅ Audit trail for calculations
- ✅ Jurisdiction module structure (Singapore)

### Current Limitations
- ❌ No standardized protocol (custom function calling)
- ❌ Limited to Anthropic Claude API
- ❌ No dynamic tool discovery
- ❌ Hardcoded integration logic
- ❌ Cannot add jurisdictions without code changes
- ❌ No hybrid retrieval (relies on pattern matching)

---

## Phase 1: MCP Wrapper (v6.5) - IMMEDIATE

**Timeline:** 3-4 days
**Cost:** $0 infrastructure changes
**Complexity:** Low

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │               MCP HOST (FastAPI)                       │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │          MCP Client Manager                      │ │ │
│  │  │  • Discovers tools from MCP servers             │ │ │
│  │  │  • Orchestrates tool invocations                │ │ │
│  │  │  • Maintains MCP sessions                       │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                       ↓ JSON-RPC 2.0                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              MCP SERVERS (Embedded)                    │ │
│  │                                                        │ │
│  │  ┌──────────────────────────────────────────────┐    │ │
│  │  │  Singapore Legal RAG Server                  │    │ │
│  │  │                                              │    │ │
│  │  │  RESOURCES (Read-only):                     │    │ │
│  │  │  • legal://rules/ORDER_21_{node_id}         │    │ │
│  │  │    → Logic tree nodes (38 nodes)            │    │ │
│  │  │  • legal://modules/ORDER_21                 │    │ │
│  │  │    → Module metadata                        │    │ │
│  │  │  • legal://jurisdiction/singapore           │    │ │
│  │  │    → Jurisdiction config                    │    │ │
│  │  │                                              │    │ │
│  │  │  TOOLS (Executable):                        │    │ │
│  │  │  • search_logic_tree()                      │    │ │
│  │  │    → Pattern-based rule matching            │    │ │
│  │  │  • calculate_order21_costs()                │    │ │
│  │  │    → Cost calculation with audit trail      │    │ │
│  │  │  • validate_legal_citation()                │    │ │
│  │  │    → Citation verification                  │    │ │
│  │  │  • extract_case_information()               │    │ │
│  │  │    → Pattern extraction                     │    │ │
│  │  │  • get_rule_context()                       │    │ │
│  │  │    → Full node with 6 dimensions            │    │ │
│  │  │                                              │    │ │
│  │  │  PROMPTS (Templates):                       │    │ │
│  │  │  • cost_calculation_workflow                │    │ │
│  │  │  • rule_analysis_workflow                   │    │ │
│  │  └──────────────────────────────────────────────┘    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │        Existing v6 Components (Wrapped)                │ │
│  │  • LogicTreeFramework → MCP Resources                 │ │
│  │  • Order21Module → MCP Tools                          │ │
│  │  • ResponseValidator → MCP Tools                      │ │
│  │  • PatternExtractor → MCP Tools                       │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
         ↓
    MCP Protocol (JSON-RPC 2.0)
         ↓
┌──────────────────────────────────────────────────────────────┐
│                      Claude API                              │
│  • Auto-discovers tools via MCP                             │
│  • Invokes tools autonomously                               │
│  • Multi-turn conversations with tool calling               │
└──────────────────────────────────────────────────────────────┘
```

### Implementation Components

#### 1. MCP Server (`backend/mcp/legal_mcp_server.py`)

**Responsibilities:**
- Expose logic tree nodes as MCP resources
- Wrap Order 21 calculator as MCP tool
- Expose validation as MCP tool
- Handle lifecycle (startup/shutdown)

**Key Endpoints:**
```python
# Resources
@mcp.resource("legal://rules/ORDER_21_{node_id}")
async def get_logic_tree_node(node_id: str) -> dict

@mcp.resource("legal://modules/ORDER_21")
async def get_module_metadata() -> dict

# Tools
@mcp.tool()
async def search_logic_tree(query: str, filters: dict) -> list[dict]

@mcp.tool()
async def calculate_order21_costs(
    court_level: str,
    case_type: str,
    claim_amount: float
) -> dict  # Returns audit trail

@mcp.tool()
async def validate_legal_citation(citation: str) -> dict

@mcp.tool()
async def extract_case_information(user_input: str) -> dict

# Prompts
@mcp.prompt(title="Cost Calculation Workflow")
def cost_calculation_prompt(case_summary: str) -> str
```

#### 2. FastAPI Integration (`backend/api/routes_mcp.py`)

**Responsibilities:**
- Mount MCP endpoint on FastAPI
- Initialize MCP client sessions
- Bridge Claude API ↔ MCP tools
- Maintain backward compatibility with v6 API

**New Endpoints:**
```python
POST /api/v7/mcp/query
  → Process query with MCP tool discovery

GET /api/v7/mcp/tools
  → List available MCP tools

GET /api/v7/mcp/resources
  → List available MCP resources
```

#### 3. Claude Integration (`backend/mcp/claude_mcp_client.py`)

**Responsibilities:**
- Connect to MCP server(s)
- Discover available tools
- Transform MCP tools → Anthropic tool format
- Handle tool invocation flow
- Manage conversation state

**Flow:**
```python
1. User sends query via FastAPI
2. FastAPI initializes MCP client session
3. MCP client discovers tools from server
4. Convert tools to Anthropic format
5. Send to Claude with tools
6. Claude responds with tool_use
7. Invoke MCP tool
8. Return result to Claude
9. Claude generates final response
10. Return to user
```

### Data Structures

#### MCP Resource Schema
```json
{
  "uri": "legal://rules/ORDER_21_RULE_1",
  "mimeType": "application/json",
  "text": {
    "node_id": "ORDER_21_RULE_1",
    "citation": "Order 21, Rule 1",
    "what": [...],  // 6 logical dimensions
    "which": [...],
    "if_then": [...],
    "modality": [...],
    "given": [...],
    "why": [...]
  }
}
```

#### MCP Tool Schema (Order 21 Calculator)
```json
{
  "name": "calculate_order21_costs",
  "description": "Calculate Singapore court costs under Order 21 with full audit trail",
  "inputSchema": {
    "type": "object",
    "properties": {
      "court_level": {
        "type": "string",
        "enum": ["High Court", "District Court", "Magistrates Court"]
      },
      "case_type": {
        "type": "string",
        "enum": ["default_judgment_liquidated", "summary_judgment", ...]
      },
      "claim_amount": {
        "type": "number",
        "minimum": 0
      }
    },
    "required": ["court_level", "case_type", "claim_amount"]
  }
}
```

#### MCP Tool Response (With Audit Trail)
```json
{
  "total_costs": 4000.00,
  "calculation_steps": [
    "1. Identified case type: default_judgment_liquidated",
    "2. Retrieved base costs from Appendix 1...",
    "3. High Court base costs: $4,000.00..."
  ],
  "assumptions": [...],
  "rules_applied": ["ORDER_21_APPENDIX_1", ...],
  "confidence": "high",
  "timestamp": "2025-10-27T..."
}
```

### Benefits of Phase 1

1. **Standardization**
   - Replace custom function calling with MCP
   - Works with Claude, GPT-4, Gemini (future)

2. **Dynamic Discovery**
   - Tools discovered at runtime
   - No hardcoded tool lists

3. **Better Modularity**
   - Logic tree, calculator, validation separate
   - Can add/remove tools independently

4. **Preparation for Phase 2**
   - Architecture ready for RAG components
   - Just add new MCP servers

5. **Improved Debugging**
   - MCP Inspector for visual debugging
   - Standardized error handling

### Implementation Checklist

- [ ] Install MCP dependencies (`mcp`, `fastapi-mcp`)
- [ ] Create MCP server exposing logic tree as resources
- [ ] Wrap Order 21 calculator as MCP tool
- [ ] Wrap validation as MCP tool
- [ ] Wrap pattern extraction as MCP tool
- [ ] Create FastAPI MCP endpoint
- [ ] Update Claude integration to use MCP
- [ ] Test tool discovery
- [ ] Test tool invocation
- [ ] Test multi-turn conversations
- [ ] Update documentation
- [ ] Deploy to Railway

### Migration Strategy

**Backward Compatibility:**
- Keep existing v6 API endpoints (`/api/messages`)
- Add new v7 MCP endpoints (`/api/v7/mcp/query`)
- Frontend can use either (gradual migration)

**Testing:**
- Test v6 API still works
- Test v7 MCP API with same queries
- Compare responses for parity

**Rollout:**
- Week 1: Build MCP server + tools
- Week 2: Integrate with FastAPI
- Week 3: Update Claude integration
- Week 4: Test + deploy

---

## Phase 2: Full RAG + MCP (v7.0) - FUTURE

**Timeline:** 6-8 weeks
**Cost:** ~$150-300/month
**Complexity:** High
**Trigger:** When >1000 users OR retrieval quality bottleneck

### Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (MCP Host)                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │               MCP Client Manager                         │ │
│  │  • Multi-server orchestration                           │ │
│  │  • Session management                                   │ │
│  │  • Load balancing across servers                        │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
         ↓ MCP Protocol (JSON-RPC 2.0)
┌────────────────────────────────────────────────────────────────┐
│                     MCP SERVERS (Microservices)                │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Singapore Document Retrieval Server                     │ │
│  │  ┌────────────────────────────────────────────────────┐ │ │
│  │  │  RESOURCES:                                        │ │ │
│  │  │  • legal://documents/singapore/{doc_id}            │ │ │
│  │  │  • legal://documents/singapore/{doc_id}/para/{id}  │ │ │
│  │  │  • legal://citations/{doc_id}/outbound             │ │ │
│  │  │  • legal://citations/{doc_id}/inbound              │ │ │
│  │  │                                                    │ │ │
│  │  │  TOOLS:                                            │ │ │
│  │  │  • hybrid_search_legal_documents()                 │ │ │
│  │  │    → BM25 (Elasticsearch) + Vector (FAISS) + RRF  │ │ │
│  │  │  • keyword_search_documents()                      │ │ │
│  │  │    → Pure BM25 for exact term matching            │ │ │
│  │  │  • semantic_search_paragraphs()                    │ │ │
│  │  │    → Pure vector search for concepts              │ │ │
│  │  │  • get_document_citations()                        │ │ │
│  │  │    → Citation graph traversal                     │ │ │
│  │  │  • search_case_precedents()                        │ │ │
│  │  │    → Similar cases by facts/holdings              │ │ │
│  │  └────────────────────────────────────────────────────┘ │ │
│  │                                                          │ │
│  │  Data Sources:                                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │Elasticsearch│  │    FAISS    │  │ PostgreSQL  │    │ │
│  │  │  (BM25)     │  │  (Vectors)  │  │ (Metadata)  │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Singapore Calculator Server                             │ │
│  │  ┌────────────────────────────────────────────────────┐ │ │
│  │  │  TOOLS:                                            │ │ │
│  │  │  • calculate_order21_costs()                       │ │ │
│  │  │  • calculate_damages_interest()                    │ │ │
│  │  │  • estimate_litigation_timeline()                  │ │ │
│  │  │  • calculate_disbursements()                       │ │ │
│  │  │                                                    │ │ │
│  │  │  Data Sources:                                     │ │ │
│  │  │  • Logic Tree Framework (deterministic)            │ │ │
│  │  │  • Fee schedules (PostgreSQL)                      │ │ │
│  │  └────────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Validation Server                                       │ │
│  │  ┌────────────────────────────────────────────────────┐ │ │
│  │  │  TOOLS:                                            │ │ │
│  │  │  • validate_legal_citations()                      │ │ │
│  │  │  • check_rule_applicability()                      │ │ │
│  │  │  • verify_quote_accuracy()                         │ │ │
│  │  │  • cross_check_precedents()                        │ │ │
│  │  │                                                    │ │ │
│  │  │  Data Sources:                                     │ │ │
│  │  │  • Citation database (PostgreSQL)                  │ │ │
│  │  │  • Logic tree nodes (for quote verification)       │ │ │
│  │  └────────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  UK Jurisdiction Server (Future)                         │ │
│  │  • UK-specific retrieval                                 │ │
│  │  • UK cost calculations                                  │ │
│  │  • UK citation validation                                │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### New Infrastructure Components

#### 1. Elasticsearch
**Purpose:** BM25 keyword search
**Cost:** ~$50-100/month (AWS OpenSearch/Elastic Cloud)
**Data:** Paragraphs indexed with metadata

**Schema:**
```json
{
  "paragraph_id": "para_001",
  "content": "The court may award costs...",
  "document_id": "doc_ORDER_21",
  "rule_number": "Order 21, Rule 1",
  "jurisdiction": "singapore",
  "doc_type": "rule",
  "effective_date": "2021-04-01",
  "section_title": "Costs in civil proceedings"
}
```

#### 2. FAISS
**Purpose:** Vector similarity search
**Cost:** $0 (library, runs in-process)
**Data:** 768-dim embeddings for semantic search

**Index Structure:**
```python
index = faiss.IndexFlatIP(768)  # Inner product for cosine similarity
index.add(embeddings)  # Add all paragraph embeddings
# Metadata stored in PostgreSQL, linked by paragraph_id
```

#### 3. PostgreSQL
**Purpose:** Structured metadata storage
**Cost:** ~$25/month (Railway/AWS RDS)

**Schema:**
```sql
CREATE TABLE documents (
    document_id VARCHAR PRIMARY KEY,
    title TEXT,
    content TEXT,
    doc_type VARCHAR,  -- statute, rule, case_law
    jurisdiction VARCHAR,  -- singapore, uk
    effective_date DATE,
    amendment_history JSONB,
    related_documents TEXT[]
);

CREATE TABLE paragraphs (
    paragraph_id VARCHAR PRIMARY KEY,
    document_id VARCHAR REFERENCES documents,
    content TEXT,
    section_title TEXT,
    paragraph_number INT,
    rule_number VARCHAR,
    page_number INT,
    embedding_vector_id INT,  -- Index into FAISS
    metadata JSONB
);

CREATE TABLE citations (
    citation_id VARCHAR PRIMARY KEY,
    source_paragraph_id VARCHAR REFERENCES paragraphs,
    target_document_id VARCHAR REFERENCES documents,
    citation_text TEXT,
    citation_type VARCHAR,  -- authoritative, persuasive
    validation_status VARCHAR
);
```

#### 4. Embedding Service
**Purpose:** Generate embeddings for search
**Options:**
- OpenAI text-embedding-3-small (~$0.02 per 1M tokens)
- Sentence Transformers (self-hosted, $0 API costs)

**Implementation:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("Order 21 summary judgment")
```

### Hybrid Search Implementation

#### Server-Side Fusion with RRF

```python
@mcp.tool()
async def hybrid_search_legal_documents(
    query: str,
    jurisdiction: Optional[str] = None,
    doc_type: Optional[str] = None,
    alpha: float = 0.5,  # BM25 weight (1-alpha = vector weight)
    limit: int = 10
) -> List[dict]:
    """
    Hybrid search: BM25 + Vector with Reciprocal Rank Fusion.

    Flow:
    1. BM25 search on Elasticsearch → ranked list A
    2. Vector search on FAISS → ranked list B
    3. Apply RRF: score(doc) = α/(60+rank_A) + (1-α)/(60+rank_B)
    4. Sort by fused score
    5. Re-rank top 20 with cross-encoder
    6. Return top 10
    """
    # 1. BM25 search
    bm25_results = await elasticsearch.search(
        index="legal_paragraphs",
        query={"match": {"content": query}},
        filters={"jurisdiction": jurisdiction, "doc_type": doc_type}
    )

    # 2. Vector search
    query_embedding = generate_embedding(query)
    distances, indices = faiss_index.search(query_embedding, limit*2)
    vector_results = fetch_paragraphs(indices)

    # 3. RRF Fusion
    def rrf_score(rank, k=60):
        return 1.0 / (k + rank)

    scores = {}
    for rank, result in enumerate(bm25_results):
        para_id = result['paragraph_id']
        scores[para_id] = alpha * rrf_score(rank)

    for rank, result in enumerate(vector_results):
        para_id = result['paragraph_id']
        scores[para_id] = scores.get(para_id, 0) + (1-alpha) * rrf_score(rank)

    # 4. Sort and return
    top_ids = sorted(scores, key=scores.get, reverse=True)[:limit]
    return fetch_full_paragraphs(top_ids)
```

### Multi-Jurisdiction Support

Each jurisdiction gets its own MCP server namespace:

```
Singapore: legal://singapore/documents/{doc_id}
           legal://singapore/rules/{rule_id}
           calculate_singapore_court_fees()

UK:        legal://uk/documents/{doc_id}
           legal://uk/statutes/{statute_id}
           calculate_uk_court_fees()

India:     legal://india/documents/{doc_id}
           legal://india/sections/{section_id}
           calculate_india_court_fees()
```

Claude automatically discovers all jurisdictions via MCP tool listing.

### Document Processing Pipeline

```
┌────────────────────────────────────────────────┐
│  Legal Document Sources                       │
│  • PDF files (Rules of Court)                 │
│  • Case law databases (LawNet)                │
│  • Practice Directions                        │
└────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────┐
│  Document Ingestion Service                   │
│  • Extract text from PDFs                     │
│  • Parse document structure                   │
│  • Identify sections/paragraphs               │
└────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────┐
│  Text Chunking                                │
│  • Rule-aware splitting                       │
│  • 1000 char chunks, 200 char overlap         │
│  • Preserve legal context                     │
└────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────┐
│  Embedding Generation                         │
│  • Generate 768-dim vectors                   │
│  • Store in FAISS index                       │
└────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────┐
│  Storage                                      │
│  • Elasticsearch: Full-text index             │
│  • FAISS: Vector index                        │
│  • PostgreSQL: Metadata + relationships       │
└────────────────────────────────────────────────┘
```

### Performance Optimization

#### 1. Caching Strategy
```python
# Redis cache for frequent queries
cache_key = f"search:{hash(query)}:{jurisdiction}:{doc_type}"
if cached := redis.get(cache_key):
    return cached

results = hybrid_search(query, jurisdiction, doc_type)
redis.setex(cache_key, 3600, results)  # 1 hour TTL
```

#### 2. Pagination
```python
@mcp.tool()
async def get_next_search_results(
    continuation_token: str
) -> List[dict]:
    """Continue paginated search results"""
    # Decode token to get cursor position
    cursor = decode_token(continuation_token)
    return fetch_results(cursor, limit=10)
```

#### 3. Batch Operations
```python
@mcp.tool()
async def batch_validate_citations(
    citations: List[str]
) -> List[dict]:
    """Validate multiple citations in one call"""
    return [validate_citation(c) for c in citations]
```

#### 4. Database Optimization
```sql
-- Critical indexes for query performance
CREATE INDEX idx_paragraphs_jurisdiction ON paragraphs(jurisdiction);
CREATE INDEX idx_paragraphs_doc_type ON paragraphs(doc_type);
CREATE INDEX idx_paragraphs_rule_number ON paragraphs(rule_number);
CREATE INDEX idx_documents_effective_date ON documents(effective_date);

-- Full-text search index
CREATE INDEX idx_paragraphs_content_fts ON paragraphs USING gin(to_tsvector('english', content));
```

### Cost Estimation (Phase 2)

| Component | Monthly Cost |
|-----------|-------------|
| Elasticsearch (AWS OpenSearch) | $70 |
| PostgreSQL (Railway Pro) | $25 |
| FAISS (in-memory, no cost) | $0 |
| Embedding API (OpenAI) | $5-10 |
| Railway Compute (2x instances) | $40 |
| Claude API calls | $20-50 |
| **Total** | **~$160-195/month** |

Compare to current: $20/month
Increase: ~8-10x

---

## Migration Path: v6 → v6.5 → v7

### Stage 1: v6.0 (Current)
- ✅ 4-phase conversation
- ✅ Logic tree framework
- ✅ Order 21 calculator
- ✅ Pattern extraction
- ❌ No MCP
- ❌ No hybrid retrieval

### Stage 2: v6.5 (Phase 1 - Week 1-4)
- ✅ Everything from v6.0
- ✅ MCP wrapper for existing components
- ✅ Standardized protocol
- ✅ Dynamic tool discovery
- ❌ Still no hybrid retrieval (not needed yet)

### Stage 3: v7.0 (Phase 2 - Month 3-5)
- ✅ Everything from v6.5
- ✅ Elasticsearch + FAISS + PostgreSQL
- ✅ Hybrid search (BM25 + vector + RRF)
- ✅ Document processing pipeline
- ✅ Multi-jurisdiction architecture
- ✅ Better retrieval quality

---

## Security & Compliance

### Authentication
```python
# JWT-based auth for MCP tools
class JWTTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> dict:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {
            "user_id": payload["user_id"],
            "roles": payload["roles"],
            "jurisdictions": payload["jurisdictions"]
        }
```

### Authorization
```python
# Role-based access control
@mcp.tool()
async def calculate_order21_costs(
    court_level: str,
    case_type: str,
    claim_amount: float,
    context: Context
) -> dict:
    # Check user has access to Singapore jurisdiction
    if "singapore" not in context.user["jurisdictions"]:
        raise PermissionError("No access to Singapore jurisdiction")

    # Check user role allows cost calculations
    if "calculator" not in context.user["roles"]:
        raise PermissionError("User not authorized for calculations")

    return order21_module.calculate(...)
```

### Audit Logging
```python
# Log all tool invocations
@mcp.tool()
async def calculate_order21_costs(...) -> dict:
    audit_log.info({
        "event": "tool_invocation",
        "tool": "calculate_order21_costs",
        "user_id": context.user["user_id"],
        "parameters": {"court_level": court_level, ...},
        "timestamp": datetime.utcnow(),
        "session_id": context.session_id
    })

    result = order21_module.calculate(...)

    audit_log.info({
        "event": "tool_result",
        "tool": "calculate_order21_costs",
        "user_id": context.user["user_id"],
        "result_summary": {"total_costs": result["total_costs"]},
        "timestamp": datetime.utcnow()
    })

    return result
```

### Data Privacy
- ✅ All user queries anonymized in logs
- ✅ PII removed from MCP tool responses
- ✅ Encryption at rest (PostgreSQL, Elasticsearch)
- ✅ Encryption in transit (TLS for all connections)

---

## Monitoring & Observability

### Key Metrics

#### Tool Performance
```python
# Track tool invocation latency
latency_histogram = Histogram(
    'mcp_tool_latency_seconds',
    'Tool invocation latency',
    ['tool_name', 'status']
)

@mcp.tool()
async def calculate_order21_costs(...):
    start_time = time.time()
    try:
        result = order21_module.calculate(...)
        latency_histogram.labels(
            tool_name='calculate_order21_costs',
            status='success'
        ).observe(time.time() - start_time)
        return result
    except Exception as e:
        latency_histogram.labels(
            tool_name='calculate_order21_costs',
            status='error'
        ).observe(time.time() - start_time)
        raise
```

#### Search Quality
```python
# Track search result relevance
relevance_counter = Counter(
    'mcp_search_relevance_feedback',
    'User feedback on search relevance',
    ['query_type', 'rating']
)

# User rates results (1-5 stars)
relevance_counter.labels(
    query_type='hybrid_search',
    rating='5'
).inc()
```

#### Token Usage
```python
# Track Claude API token consumption
token_counter = Counter(
    'claude_api_tokens',
    'Claude API token usage',
    ['type']  # cached, uncached
)

# After each API call
token_counter.labels(type='cached').inc(response.usage.cache_read_input_tokens)
token_counter.labels(type='uncached').inc(response.usage.input_tokens)
```

### Alerts

```yaml
# Prometheus alert rules
groups:
  - name: mcp_tools
    rules:
      - alert: HighToolLatency
        expr: histogram_quantile(0.95, mcp_tool_latency_seconds) > 10
        for: 5m
        annotations:
          summary: "Tool latency p95 > 10s"

      - alert: HighToolErrorRate
        expr: rate(mcp_tool_errors_total[5m]) > 0.01
        for: 5m
        annotations:
          summary: "Tool error rate > 1%"

      - alert: HighTokenCosts
        expr: rate(claude_api_tokens[1h]) > 1000000
        for: 1h
        annotations:
          summary: "Token usage > 1M/hour (check costs)"
```

---

## Testing Strategy

### Phase 1 Testing

#### Unit Tests
```python
# Test MCP tool wrapping
async def test_calculate_order21_costs_tool():
    result = await mcp_server.calculate_order21_costs(
        court_level="High Court",
        case_type="default_judgment_liquidated",
        claim_amount=50000
    )

    assert result["total_costs"] == 4000.00
    assert "calculation_steps" in result
    assert "audit_trail" in result
```

#### Integration Tests
```python
# Test MCP client → server → calculator flow
async def test_mcp_end_to_end():
    async with mcp_client_session() as session:
        # Discover tools
        tools = await session.list_tools()
        assert "calculate_order21_costs" in [t.name for t in tools]

        # Invoke tool
        result = await session.call_tool(
            "calculate_order21_costs",
            arguments={"court_level": "High Court", ...}
        )

        assert result["total_costs"] == 4000.00
```

#### Claude Integration Tests
```python
# Test Claude with MCP tools
async def test_claude_with_mcp_tools():
    response = await claude_api.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{
            "role": "user",
            "content": "Calculate costs for $50k High Court default judgment"
        }],
        tools=mcp_tools
    )

    # Verify Claude invokes the tool
    assert any(block.type == "tool_use" for block in response.content)

    # Verify tool name
    tool_block = next(b for b in response.content if b.type == "tool_use")
    assert tool_block.name == "calculate_order21_costs"
```

### Phase 2 Testing

#### Retrieval Quality Tests
```python
# Test hybrid search relevance
async def test_hybrid_search_relevance():
    results = await hybrid_search_legal_documents(
        query="summary judgment order 14",
        jurisdiction="singapore"
    )

    # Top result should be Order 14
    assert "Order 14" in results[0]["rule_number"]
    assert results[0]["relevance_score"] > 0.8
```

#### Load Tests
```python
# Test concurrent searches
async def test_concurrent_searches():
    queries = [f"query_{i}" for i in range(100)]

    start = time.time()
    results = await asyncio.gather(*[
        hybrid_search(q) for q in queries
    ])
    duration = time.time() - start

    # Should handle 100 concurrent searches in <5s
    assert duration < 5.0
    assert all(len(r) > 0 for r in results)
```

---

## Deployment

### Phase 1 Deployment (Railway)

```yaml
# railway.toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "uvicorn backend.api.routes:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[env]
ANTHROPIC_API_KEY = "${ANTHROPIC_API_KEY}"
DATABASE_URL = "${DATABASE_URL}"
MCP_ENABLED = "true"
```

### Phase 2 Deployment (Multi-Service)

```yaml
# docker-compose.yml
version: '3.8'

services:
  fastapi:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY
      - DATABASE_URL
      - ELASTICSEARCH_URL
      - REDIS_URL
    depends_on:
      - postgres
      - elasticsearch
      - redis
      - mcp-retrieval-server
      - mcp-calculator-server

  mcp-retrieval-server:
    build: ./backend/mcp/servers/retrieval
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL
      - ELASTICSEARCH_URL
    depends_on:
      - postgres
      - elasticsearch

  mcp-calculator-server:
    build: ./backend/mcp/servers/calculator
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=legal_db
      - POSTGRES_USER=legal_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - es_data:/usr/share/elasticsearch/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  es_data:
  redis_data:
```

---

## Decision Points

### When to Trigger Phase 2 (RAG)?

**Trigger Conditions (Any One):**
1. ✅ User base > 1000 active users/month
2. ✅ Search quality complaints > 10%
3. ✅ Pattern extraction accuracy < 80%
4. ✅ Need to support 3+ jurisdictions
5. ✅ Budget allows $150-300/month infrastructure

**Current Status:**
- Users: ~50/month → Wait
- Search quality: Not measured yet → Wait
- Pattern accuracy: ~85% → Acceptable
- Jurisdictions: 1 (Singapore) → Wait
- Budget: $20/month → Wait

**Recommendation:** Implement Phase 1 now, reassess Phase 2 in 6 months.

---

## Success Metrics

### Phase 1 Success Criteria
- ✅ All v6 tools wrapped as MCP tools
- ✅ Claude successfully discovers tools
- ✅ Tool invocation working (>95% success rate)
- ✅ Backward compatible with v6 API
- ✅ Deployed to Railway without issues
- ✅ Response quality equal to v6

### Phase 2 Success Criteria
- ✅ Hybrid search implemented (BM25 + vector + RRF)
- ✅ Search relevance > 85% (user feedback)
- ✅ p95 latency < 3 seconds (searches)
- ✅ p95 latency < 10 seconds (calculations)
- ✅ Support 100 concurrent users
- ✅ Infrastructure costs < $200/month
- ✅ Multi-jurisdiction support (2+ jurisdictions)

---

## Appendix A: MCP Protocol Primer

### JSON-RPC 2.0 Message Format

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "calculate_order21_costs",
        "description": "Calculate Singapore court costs",
        "inputSchema": {...}
      }
    ]
  }
}
```

### Three Core Primitives

1. **Resources** (Read-only data)
   - URI-addressable: `legal://rules/ORDER_21_RULE_1`
   - Application-controlled
   - Used for context, not execution

2. **Tools** (Executable functions)
   - LLM-invoked autonomously
   - Have input schemas (JSON Schema)
   - Return structured results

3. **Prompts** (Reusable templates)
   - User-triggered workflows
   - Guide LLM through complex tasks
   - Return formatted prompts

### Lifecycle

```
1. Initialize → Capability negotiation
2. List Resources → Discover available resources
3. List Tools → Discover available tools
4. Call Tool → Execute with parameters
5. Get Result → Receive structured response
6. Shutdown → Cleanup
```

---

## Appendix B: Code Organization

```
legal-advisory-v5/
├── backend/
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── servers/
│   │   │   ├── legal_mcp_server.py       # Phase 1: Main MCP server
│   │   │   ├── retrieval_server.py       # Phase 2: Hybrid search
│   │   │   ├── calculator_server.py      # Phase 2: Calculators
│   │   │   └── validation_server.py      # Phase 2: Validation
│   │   ├── clients/
│   │   │   ├── claude_mcp_client.py      # Claude integration
│   │   │   └── mcp_client_manager.py     # Multi-server orchestration
│   │   ├── schemas/
│   │   │   ├── resources.py              # Resource schemas
│   │   │   └── tools.py                  # Tool schemas
│   │   └── utils/
│   │       ├── rrf_fusion.py             # Reciprocal Rank Fusion
│   │       └── embeddings.py             # Embedding generation
│   ├── api/
│   │   ├── routes.py                     # Existing v6 routes
│   │   ├── routes_mcp.py                 # New MCP endpoints
│   │   └── routes_v6.py                  # v6 backward compat
│   └── ...
├── requirements.txt                       # Add MCP dependencies
├── MCP_HIGH_LEVEL_DESIGN.md              # This document
└── README.md
```

---

## Appendix C: References

### MCP Resources
- **Official Docs:** https://modelcontextprotocol.io/
- **Python SDK:** https://github.com/modelcontextprotocol/python-sdk
- **FastMCP:** https://github.com/jlowin/fastmcp
- **MCP Inspector:** https://github.com/modelcontextprotocol/inspector

### RAG Resources
- **Elasticsearch Docs:** https://www.elastic.co/guide/
- **FAISS Wiki:** https://github.com/facebookresearch/faiss/wiki
- **Sentence Transformers:** https://www.sbert.net/
- **RRF Paper:** "Rank Fusion for Effective Information Retrieval"

### Legal Tech
- **Singapore Rules of Court 2021**
- **LawNet Singapore**
- **Supreme Court Practice Directions**

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-27 | Claude Code | Initial design document |

---

**End of Document**
