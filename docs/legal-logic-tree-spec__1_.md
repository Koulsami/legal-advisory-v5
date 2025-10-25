# Legal Logic Tree System - Complete Technical Specification v2.0
## Singapore Legal Costs Advisory System

---

# EXECUTIVE SUMMARY

The Legal Logic Tree System transforms unstructured legal documents (statutes, rules, case law) into a **computable network of logical propositions**. Each legal authority becomes a "Tree Node" containing structured answers to logical deduction questions (WHAT, WHICH, IF-THEN, CAN/MUST, GIVEN, WHY). These nodes connect through relationships (interprets, extends, overrules) creating a queryable legal reasoning engine.

**Core Innovation**: Instead of keyword search, the system traverses logical relationships to build reasoning chains that mirror how lawyers think, providing answers with complete authority citations and confidence scores.

---

# PART A: THE TREE LOGIC SYSTEM EXPLAINED

## 1. What is a Legal Logic Tree?

### 1.1 Conceptual Overview

Traditional legal databases store documents. Our Legal Logic Tree stores **legal reasoning** as structured data:

```
Traditional System:
Document â†’ Full Text â†’ Keyword Search â†’ Manual Reading â†’ Extract Principle

Our Tree Logic System:
Document â†’ Logic Extraction â†’ Tree Node â†’ Logical Queries â†’ Instant Answer
```

### 1.2 The Tree Structure

Each legal authority (law/rule/case) is a **node** with **branches** representing logical deductions:

```
           [Order 21 Rule 3 - Costs Entitlement]
                         ROOT NODE
                             |
        â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•¬â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
        â•‘                    â•‘                   â•‘
    WHAT Branch         IF-THEN Branch      MODALITY Branch
        â•‘                    â•‘                   â•‘
"No automatic costs"  "IF party succeeds"   "Court MUST order"
"Court must order"    "THEN gets costs"     "Party CANNOT recover"
"Amendment costs"     "UNLESS exceptional"   "Party MAY apply"
```

### 1.3 Why "Tree"?

1. **Hierarchical Authority**: Statutes (roots) â†’ Rules (trunk) â†’ Cases (branches)
2. **Branching Logic**: Each principle can have multiple interpretations
3. **Growth Over Time**: New cases add branches without changing core structure
4. **Traversable Paths**: Follow logical connections to reach conclusions

---

## 2. The Logical Deduction Framework

### 2.1 Six Core Question Types

Our system answers six fundamental logical questions about every legal principle:

#### WHAT - Facts and Conclusions
```yaml
Question: "What does this law establish?"
Example: 
  Law: "Order 21 Rule 3(2)"
  WHAT: "Court must order costs for successful party"
  
Purpose: Extracts core propositions and holdings
```

#### WHICH - Scope and Application
```yaml
Question: "Which entities/situations does this apply to?"
Example:
  Law: "Order 21 Rule 3(5)"
  WHICH: "Trustees, personal representatives, mortgagees"
  
Purpose: Defines boundaries of application
```

#### IF-THEN - Conditional Logic
```yaml
Question: "If X happens, then what follows?"
Example:
  Law: "Order 21 Rule 3(3)"
  IF: "Party makes amendment without permission"
  THEN: "Must bear costs of amendment"
  
Purpose: Captures cause-effect relationships
```

#### CAN/MUST/MAY - Modal Logic
```yaml
Question: "What is permitted/required/prohibited?"
Example:
  Law: "Order 21 Rule 3(1)"
  CANNOT: "Party cannot recover costs without court order"
  MUST: "Court must order costs for winner"
  MAY: "Court may make different order"
  
Purpose: Distinguishes obligations from discretions
```

#### GIVEN - Assumptions and Context
```yaml
Question: "Given certain conditions, what follows?"
Example:
  Law: "Order 21 Rule 3(5)"
  GIVEN: "Party acts as trustee"
  IMPLIES: "Entitled to costs from trust fund"
  
Purpose: Handles contextual applications
```

#### WHY - Reasoning and Policy
```yaml
Question: "Why does this rule exist?"
Example:
  Law: "Costs follow the event"
  WHY: "Winner shouldn't bear expense of vindicating rights"
  
Purpose: Captures underlying rationale
```

### 2.2 How These Questions Create Intelligence

By answering these six questions for every legal authority, we transform static text into **queryable logic**:

**Query**: "Can a winning party lose costs?"

**System Process**:
1. Finds WHAT: "Court must order costs for successful party"
2. Checks IF-THEN: "IF party acts unreasonably THEN may lose costs"
3. Identifies MODALITY: "Court MAY make different order"
4. Result: "Yes, if acted unreasonably (Order 21 Rule 4)"

---

## 3. Building a Tree Node - Step by Step

### 3.1 Starting with Raw Legal Text

Take Order 21 Rule 3(2):
> "The Court must, subject to this Order, order the costs of any proceedings in favour of a successful party, except when it appears to the Court that in the circumstances of the case some other order should be made..."

### 3.2 Extraction Process

```python
Step 1: Identify Core Elements
- Subject: "Court"
- Action: "order costs"
- Beneficiary: "successful party"
- Modality: "must"
- Exception: "except when circumstances warrant"

Step 2: Answer Logical Questions
WHAT: "Court must order costs for successful party"
WHICH: "All proceedings, all successful parties"
IF-THEN: "IF party succeeds THEN gets costs"
MODALITY: "Court MUST order (with exceptions)"
GIVEN: "Given success in proceedings"
WHY: "Costs follow the event principle"

Step 3: Assign Metadata
- Authority weight: 0.8 (rule)
- Confidence: 0.95 (explicit text)
- Source: "[3(2)]"
```

### 3.3 The Resulting Tree Node Structure

```json
{
  "node_id": "ROC-2021-O21-R3-2",
  "citation": "Order 21 Rule 3(2)",
  "what": [
    {
      "proposition": "Court must order costs for successful party",
      "confidence": 0.95,
      "exceptions": ["circumstances warrant otherwise"]
    }
  ],
  "if_then": [
    {
      "condition": "party succeeds in proceedings",
      "consequence": "entitled to costs order",
      "exceptions": ["exceptional circumstances"],
      "confidence": 0.95
    }
  ],
  "modality": [
    {
      "action": "order costs",
      "modal_type": "MUST",
      "subject": "court",
      "exceptions": ["circumstances warrant otherwise"]
    }
  ]
}
```

---

# PART B: IMPLEMENTATION FOR COSTS SYSTEM

## 4. System Architecture

### 4.1 Component Overview

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                     LEGAL LOGIC TREE SYSTEM                      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚   INGESTION LAYER     â”‚  PROCESSING LAYER â”‚  APPLICATION LAYER â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ â€¢ Document Parser     â”‚ â€¢ Logic Extractor â”‚ â€¢ Query Engine     â”‚
â”‚ â€¢ OCR for PDFs       â”‚ â€¢ NLP Pipeline    â”‚ â€¢ Reasoning Chain  â”‚
â”‚ â€¢ Citation Detector   â”‚ â€¢ Confidence Scorerâ”‚ â€¢ Answer Generatorâ”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚   STORAGE LAYER       â”‚  RELATIONSHIP LAYERâ”‚  API LAYER        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ â€¢ PostgreSQL (nodes)  â”‚ â€¢ Neo4j (graph)   â”‚ â€¢ REST APIs       â”‚
â”‚ â€¢ Redis (cache)       â”‚ â€¢ Relationship    â”‚ â€¢ WebSocket       â”‚
â”‚ â€¢ Elasticsearch       â”‚   Builder         â”‚ â€¢ GraphQL         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 4.2 Data Flow

```mermaid
graph LR
    A[Legal Document] --> B[Parser]
    B --> C[Logic Extractor]
    C --> D[Tree Node]
    D --> E[Storage]
    E --> F[Relationship Builder]
    F --> G[Graph Database]
    
    H[User Query] --> I[Query Engine]
    I --> G
    G --> J[Reasoning Chain]
    J --> K[Answer + Citations]
```

---

## 5. Complete Tree Node Data Model

### 5.1 Core Tree Node Structure

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class SourceType(Enum):
    STATUTE = "statute"          # Primary legislation
    RULE = "rule"                # Rules of Court
    CASE = "case"                # Case law
    PRACTICE_DIRECTION = "pd"    # Practice directions
    APPENDIX = "appendix"        # Fixed scales/schedules

class ModalityType(Enum):
    MUST = "must"                # Mandatory obligation
    SHALL = "shall"              # Mandatory (formal)
    MAY = "may"                  # Discretionary power
    CAN = "can"                  # Permission
    CANNOT = "cannot"            # Prohibition
    MUST_NOT = "must_not"        # Strong prohibition
    SHOULD = "should"            # Recommendation

@dataclass
class TreeNode:
    """
    Complete Tree Node structure for legal logic
    """
    
    # === IDENTITY ===
    node_id: str                        # Unique identifier
    citation: str                        # Short citation
    full_citation: str                   # Complete citation
    source_type: SourceType             
    
    # === AUTHORITY HIERARCHY ===
    base_weight: float                  # 1.0=statute, 0.8=rule, 0.6-0.7=case
    binding_authority: bool              # Is this binding?
    jurisdiction: str                    # SG, UK, MY, etc.
    court_level: Optional[str]          # APEX, APPELLATE, HIGH, DISTRICT
    
    # === TEMPORAL VALIDITY ===
    effective_date: datetime
    amendment_date: Optional[datetime]
    repealed_date: Optional[datetime]
    is_current: bool
    
    # === SOURCE CONTENT ===
    full_text: str                      # Complete original text
    relevant_excerpts: List[Dict]       # Key portions
    
    # === LOGICAL DEDUCTIONS ===
    
    # WHAT - Core propositions
    what: List[Dict]
    """
    [{
        "proposition": str,              # The fact/conclusion
        "confidence": float,             # 0.0-1.0
        "source_paragraph": str,         # [3(2)]
        "exceptions": List[str],        # When doesn't apply
        "extraction_method": str        # How extracted
    }]
    """
    
    # WHICH - Entities covered
    which: List[Dict]
    """
    [{
        "entity_type": str,              # party, court, solicitor
        "conditions": List[str],         # When applies
        "included": bool,               # In or out of scope
        "exclusions": List[str],        # Specific exclusions
        "source_paragraph": str
    }]
    """
    
    # IF-THEN - Conditional logic
    if_then: List[Dict]
    """
    [{
        "condition": str,                # The IF part
        "consequence": str,              # The THEN part
        "operator": str,                # IMPLIES, UNLESS, etc.
        "exceptions": List[str],
        "confidence": float,
        "source_paragraph": str
    }]
    """
    
    # Modality - CAN/MUST/MAY
    modality: List[Dict]
    """
    [{
        "action": str,                   # What action
        "modal_type": ModalityType,
        "subject": str,                  # Who must/may
        "object": Optional[str],         # To whom/what
        "conditions": List[str],
        "exceptions": List[str],
        "source_paragraph": str
    }]
    """
    
    # GIVEN - Assumptions
    given: List[Dict]
    """
    [{
        "premise": str,                  # The assumption
        "implications": List[str],       # What follows
        "conditions": List[str],
        "source_paragraph": str
    }]
    """
    
    # WHY - Reasoning
    why: List[Dict]
    """
    [{
        "rule": str,                     # What rule
        "reasoning": str,                # Why it exists
        "policy": str,                   # Policy goal
        "source": str                    # Authority
    }]
    """
    
    # === RELATIONSHIPS ===
    relationships: List['NodeRelationship']
    
    # === METADATA ===
    created_at: datetime
    updated_at: datetime
    extraction_confidence: float        # Overall confidence
    manual_review: bool                 # Human verified?
    notes: Optional[str]
```

### 5.2 Relationship Structure

```python
@dataclass
class NodeRelationship:
    """
    Relationships between Tree Nodes
    """
    
    source_node_id: str
    target_node_id: str
    
    relationship_type: str
    """
    Types:
    - INTERPRETS: Case interprets rule
    - APPLIES: Case applies principle
    - OVERRULES: Overturns precedent
    - EXTENDS: Adds to principle
    - NARROWS: Limits application
    - BROADENS: Expands application
    - DISTINGUISHES: Different facts
    - FOLLOWS: Affirms precedent
    """
    
    strength: float                    # 0.0-1.0 relationship strength
    description: str
    
    impact: Dict
    """
    {
        "modifies_what": List[str],     # Changes to WHAT
        "adds_conditions": List[str],   # New IF-THENs
        "changes_modality": List[str],  # MUST becomes MAY
        "provides_examples": List[str]  # Concrete applications
    }
    """
```

---

## 6. Order 21 Implementation Example

### 6.1 Building the Order 21 Tree

```python
# Order 21 has 29 rules forming a tree structure:

ORDER_21_TREE = {
    "root": "O.21 - COSTS",
    "divisions": [
        {
            "name": "Division 1 - General",
            "rules": [
                "Rule 1: Definitions",
                "Rule 2: Powers of Court",
                "Rule 3: Entitlement to costs",
                "Rule 4: Adverse costs - successful party",
                "Rule 5: Adverse costs - non-party",
                "Rule 6: Adverse costs - solicitor"
            ]
        },
        {
            "name": "Division 2 - Procedure",
            "rules": ["Rule 17-21: Assessment procedures"]
        }
    ]
}
```

### 6.2 Order 21 Rule 3 - Complete Tree Node

```python
order_21_rule_3_node = TreeNode(
    # Identity
    node_id="ROC-2021-O21-R3",
    citation="O.21 r.3",
    full_citation="Rules of Court 2021, Order 21, Rule 3",
    source_type=SourceType.RULE,
    
    # Authority
    base_weight=0.8,
    binding_authority=True,
    jurisdiction="SG",
    court_level=None,
    
    # Temporal
    effective_date=datetime(2021, 4, 1),
    is_current=True,
    
    # WHAT - 5 core propositions
    what=[
        {
            "proposition": "No automatic entitlement to costs without court order",
            "confidence": 1.0,
            "source_paragraph": "[3(1)]",
            "exceptions": [],
            "extraction_method": "explicit_rule"
        },
        {
            "proposition": "Court must order costs for successful party",
            "confidence": 0.95,
            "source_paragraph": "[3(2)]",
            "exceptions": ["circumstances warrant otherwise"],
            "extraction_method": "explicit_rule"
        },
        {
            "proposition": "Amendment costs borne by amending party",
            "confidence": 0.95,
            "source_paragraph": "[3(3)]",
            "exceptions": ["court orders otherwise"],
            "extraction_method": "explicit_rule"
        },
        {
            "proposition": "Time extension costs borne by applicant",
            "confidence": 0.95,
            "source_paragraph": "[3(4)]",
            "exceptions": ["court orders otherwise"],
            "extraction_method": "explicit_rule"
        },
        {
            "proposition": "Trustees entitled to costs from fund",
            "confidence": 0.9,
            "source_paragraph": "[3(5)]",
            "exceptions": ["costs recovered from other party"],
            "extraction_method": "explicit_rule"
        }
    ],
    
    # WHICH - Who is covered
    which=[
        {"entity_type": "party", "conditions": ["in proceedings"], "included": True},
        {"entity_type": "successful_party", "conditions": ["wins case"], "included": True},
        {"entity_type": "trustee", "conditions": ["acting as trustee"], "included": True},
        {"entity_type": "personal_representative", "conditions": ["acting as PR"], "included": True},
        {"entity_type": "mortgagee", "conditions": ["acting as mortgagee"], "included": True}
    ],
    
    # IF-THEN - 5 conditional rules
    if_then=[
        {
            "condition": "party wants costs",
            "consequence": "must get court order",
            "operator": "IMPLIES",
            "confidence": 1.0,
            "source_paragraph": "[3(1)]"
        },
        {
            "condition": "party succeeds",
            "consequence": "gets costs order",
            "operator": "IMPLIES",
            "exceptions": ["exceptional circumstances"],
            "confidence": 0.95,
            "source_paragraph": "[3(2)]"
        },
        {
            "condition": "party amends without permission",
            "consequence": "bears amendment costs",
            "operator": "IMPLIES",
            "exceptions": ["court orders otherwise"],
            "confidence": 0.95,
            "source_paragraph": "[3(3)]"
        },
        {
            "condition": "party applies for extension",
            "consequence": "bears application costs",
            "operator": "IMPLIES",
            "exceptions": ["court orders otherwise"],
            "confidence": 0.95,
            "source_paragraph": "[3(4)]"
        },
        {
            "condition": "trustee incurs costs AND not recovered",
            "consequence": "entitled from trust fund",
            "operator": "IMPLIES",
            "confidence": 0.9,
            "source_paragraph": "[3(5)]"
        }
    ],
    
    # MODALITY - What parties MUST/MAY do
    modality=[
        {
            "action": "recover costs",
            "modal_type": ModalityType.CANNOT,
            "subject": "party",
            "conditions": ["without court order"],
            "source_paragraph": "[3(1)]"
        },
        {
            "action": "order costs",
            "modal_type": ModalityType.MUST,
            "subject": "court",
            "object": "successful party",
            "exceptions": ["circumstances warrant otherwise"],
            "source_paragraph": "[3(2)]"
        },
        {
            "action": "bear costs",
            "modal_type": ModalityType.MUST,
            "subject": "amending party",
            "conditions": ["amendment without permission"],
            "source_paragraph": "[3(3)]"
        }
    ]
)
```

---

## 7. Case Law Extraction Engine

### 7.1 The Challenge

A 50-page judgment might contain only 2-3 paragraphs about costs. Our system must:
1. Find those paragraphs (relevance detection)
2. Extract structured logic (pattern matching + NLP)
3. Link to relevant rules (relationship building)

### 7.2 Three-Stage Extraction Process

```python
class CaseLawCostsExtractor:
    
    def extract_from_judgment(self, judgment_text: str) -> TreeNode:
        """
        Converts case judgment into Tree Node
        """
        
        # STAGE 1: Find Costs Sections
        relevant_sections = self.find_costs_sections(judgment_text)
        # Uses relevance scoring (0.0-1.0) based on:
        # - Keyword density (costs, fees, disbursements)
        # - Pattern matching (costs order patterns)
        # - Proximity to "Order 21" mentions
        
        # STAGE 2: Extract Structured Logic
        extracted_logic = {
            'what': self.extract_propositions(relevant_sections),
            'which': self.extract_entities(relevant_sections),
            'if_then': self.extract_conditionals(relevant_sections),
            'modality': self.extract_modalities(relevant_sections),
            'given': self.extract_assumptions(relevant_sections),
            'why': self.extract_reasoning(relevant_sections)
        }
        
        # STAGE 3: Build Tree Node
        return self.build_tree_node(extracted_logic)
```

### 7.3 Pattern Library for Extraction

```python
EXTRACTION_PATTERNS = {
    # For WHAT extraction
    'holdings': [
        r'(?:court|tribunal)\s+(?:held|found|determined)\s+that\s+(.+)',
        r'(?:principle|rule|test)\s+is\s+(?:that\s+)?(.+)',
        r'it\s+is\s+(?:established|settled)\s+(?:law\s+)?that\s+(.+)'
    ],
    
    # For IF-THEN extraction
    'conditionals': [
        r'if\s+(.+?),?\s+then\s+(.+)',
        r'where\s+(.+?),?\s+(?:the\s+court\s+)?(?:must|should|will)\s+(.+)',
        r'unless\s+(.+?),?\s+(.+)'
    ],
    
    # For MODALITY extraction
    'modals': [
        r'(?:court|party)\s+(must|shall|may|can|cannot|should)\s+(.+)',
        r'(?:is|are)\s+(required|permitted|prohibited)\s+to\s+(.+)'
    ],
    
    # For costs-specific patterns
    'costs_orders': [
        r'costs?\s+(?:shall|should|must|will)\s+follow\s+(?:the\s+)?event',
        r'(?:standard|indemnity)\s+basis',
        r'(?:no\s+)?order\s+as\s+to\s+costs'
    ]
}
```

---

## 8. Query Processing System

### 8.1 How Queries Are Answered

```python
def process_query(query: str) -> Answer:
    """
    Example: "Can winning party lose costs?"
    """
    
    # Step 1: Parse Query Intent
    intent = parse_intent(query)
    # Result: {topic: "costs_deprivation", entity: "winning_party"}
    
    # Step 2: Find Relevant Nodes
    nodes = find_relevant_nodes(intent)
    # Finds: O.21 r.3, O.21 r.4, Bumi Armada case
    
    # Step 3: Build Reasoning Chain
    chain = build_reasoning_chain(nodes)
    """
    1. O.21 r.3: Court must order costs for successful party
    2. O.21 r.4: UNLESS party acted unreasonably
    3. Bumi Armada: Example - 70% costs for failing on issues
    """
    
    # Step 4: Generate Answer
    return generate_answer(chain)
    # "Yes, successful party can lose costs if acted unreasonably
    #  (O.21 r.4) or failed on significant issues (Bumi Armada)"
```

### 8.2 Reasoning Chain Example

```yaml
Query: "What costs for default judgment with 3 defendants in High Court?"

Reasoning Chain:
  Step 1:
    Node: "O.21 Appendix 1 Part 2"
    Logic: "Default judgment HC = $2,300 base"
    
  Step 2:
    Node: "O.21 Appendix 1 Part 2 para 3"
    Logic: "Multiple defendants +$100/$200 each"
    
  Step 3:
    Calculation: "$2,300 + $100 + $200 = $2,600"
    
Answer:
  Amount: "$2,600"
  Breakdown:
    - Base: "$2,300 (default judgment)"
    - 2nd defendant: "+$100 (same solicitor)"
    - 3rd defendant: "+$200 (different solicitor)"
  Authority: "O.21 Appendix 1, Part 2"
```

---

## 9. Implementation Roadmap

### Phase 1: Foundation (Week 1)
```yaml
Day 1-2: Data Structure Setup
  - Implement TreeNode class
  - Create database schemas
  - Set up PostgreSQL + Neo4j
  
Day 3-4: Manual Rule Entry
  - Enter Order 21 (29 rules)
  - Enter Order 5 (3 rules)  
  - Enter Appendix 1 (fixed costs)
  
Day 5: Testing
  - Unit tests for node creation
  - Relationship building tests
```

### Phase 2: Extraction Engine (Week 2)
```yaml
Day 1-2: NLP Pipeline
  - Set up spaCy + transformers
  - Implement relevance scoring
  
Day 3-4: Pattern Extraction
  - Implement extraction methods
  - Test with 5 landmark cases
  
Day 5: Confidence Scoring
  - Implement confidence calculation
  - Manual review interface
```

### Phase 3: Query System (Week 3)
```yaml
Day 1-2: Query Parser
  - Intent classification
  - Entity extraction
  
Day 3-4: Reasoning Engine
  - Chain builder
  - Answer generator
  
Day 5: Testing
  - 50 real lawyer queries
  - Performance optimization
```

### Phase 4: Production (Week 4)
```yaml
Day 1-2: API Development
  - REST endpoints
  - WebSocket real-time
  
Day 3-4: User Interface
  - Query interface
  - Results display
  
Day 5: Deployment
  - Docker containers
  - Production testing
```

---

## 10. Key Algorithms

### 10.1 Relevance Scoring Algorithm

```python
def calculate_relevance(text: str) -> float:
    """
    Scores text relevance to costs (0.0-1.0)
    """
    score = 0.0
    
    # Keyword scoring (0.0-0.4)
    costs_keywords = ['costs', 'fees', 'disbursements', 'expenses']
    for keyword in costs_keywords:
        if keyword in text.lower():
            score += 0.1
    
    # Pattern scoring (0.0-0.3)
    if re.search(r'costs?\s+order', text, re.I):
        score += 0.15
    if re.search(r'party\s+and\s+party', text, re.I):
        score += 0.15
        
    # Authority proximity (0.0-0.3)
    if 'Order 21' in text or 'O.21' in text:
        score += 0.3
        
    return min(score, 1.0)
```

### 10.2 Confidence Calculation

```python
def calculate_confidence(extraction_method: str, text_clarity: float) -> float:
    """
    Calculates extraction confidence
    """
    base_confidence = {
        'explicit_rule': 0.95,      # Clear statutory text
        'pattern_match': 0.80,      # Pattern extraction
        'nlp_inference': 0.65,      # NLP-based
        'ml_prediction': 0.60       # ML model
    }
    
    confidence = base_confidence.get(extraction_method, 0.5)
    confidence *= text_clarity  # Adjust for text quality
    
    return confidence
```

### 10.3 Relationship Strength

```python
def calculate_relationship_strength(
    source: TreeNode, 
    target: TreeNode
) -> float:
    """
    Calculates how strongly source affects target
    """
    strength = 0.0
    
    # Authority differential
    if source.base_weight > target.base_weight:
        strength += 0.3  # Higher authority interpreting lower
    
    # Temporal proximity
    years_apart = abs(source.effective_date.year - target.effective_date.year)
    if years_apart < 2:
        strength += 0.2
    
    # Content overlap
    overlap = calculate_semantic_similarity(source.what, target.what)
    strength += overlap * 0.5
    
    return min(strength, 1.0)
```

---

## 11. Database Design

### 11.1 PostgreSQL Schema

```sql
-- Main nodes table
CREATE TABLE tree_nodes (
    node_id VARCHAR(50) PRIMARY KEY,
    citation VARCHAR(255) NOT NULL,
    full_citation TEXT NOT NULL,
    source_type VARCHAR(20) NOT NULL,
    base_weight DECIMAL(3,2) NOT NULL,
    binding_authority BOOLEAN NOT NULL,
    jurisdiction VARCHAR(10) NOT NULL,
    court_level VARCHAR(20),
    
    -- Temporal fields
    effective_date TIMESTAMP NOT NULL,
    amendment_date TIMESTAMP,
    repealed_date TIMESTAMP,
    is_current BOOLEAN DEFAULT true,
    
    -- Content
    full_text TEXT NOT NULL,
    relevant_excerpts JSONB,
    
    -- Logical deductions as JSONB
    what_deductions JSONB,
    which_deductions JSONB,
    if_then_deductions JSONB,
    modality_deductions JSONB,
    given_deductions JSONB,
    why_deductions JSONB,
    
    -- Metadata
    extraction_confidence DECIMAL(3,2),
    manual_review BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_citation (citation),
    INDEX idx_source_type (source_type),
    INDEX idx_jurisdiction (jurisdiction),
    INDEX idx_current (is_current)
);

-- Relationships table
CREATE TABLE node_relationships (
    relationship_id SERIAL PRIMARY KEY,
    source_node_id VARCHAR(50) REFERENCES tree_nodes(node_id),
    target_node_id VARCHAR(50) REFERENCES tree_nodes(node_id),
    relationship_type VARCHAR(50) NOT NULL,
    strength DECIMAL(3,2),
    description TEXT,
    impact JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(source_node_id, target_node_id, relationship_type)
);

-- Query logs for learning
CREATE TABLE query_logs (
    query_id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    intent JSONB,
    nodes_accessed JSONB,
    answer_generated TEXT,
    user_feedback INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 11.2 Neo4j Graph Schema

```cypher
// Create node
CREATE (n:LegalNode {
    node_id: 'ROC-2021-O21-R3',
    citation: 'O.21 r.3',
    source_type: 'RULE',
    weight: 0.8
})

// Create relationship
MATCH (a:LegalNode {node_id: 'CASE-2019-SGCA-15'})
MATCH (b:LegalNode {node_id: 'ROC-2021-O21-R3'})
CREATE (a)-[r:INTERPRETS {
    strength: 0.85,
    impact: 'adds issue-based costs'
}]->(b)

// Query for reasoning chain
MATCH path = (query:LegalNode {node_id: $start_node})
  -[:INTERPRETS|APPLIES|EXTENDS*1..3]-
  (target:LegalNode)
WHERE target.source_type = 'RULE'
RETURN path
ORDER BY reduce(s = 0, r IN relationships(path) | s + r.strength) DESC
LIMIT 5
```

---

## 12. Performance Specifications

### 12.1 Response Time Requirements

```yaml
Operation Targets:
  Node Creation: < 500ms
  Relationship Creation: < 200ms
  Case Extraction: < 5s per judgment
  Simple Query: < 1s
  Complex Query (5+ nodes): < 2s
  Reasoning Chain (10 steps): < 3s
```

### 12.2 Accuracy Targets

```yaml
Extraction Accuracy:
  Rule Extraction: 95%+ (explicit text)
  Case Holdings: 85%+ (pattern matching)
  Conditionals: 80%+ (if-then logic)
  Modalities: 85%+ (must/may/cannot)
  
Query Accuracy:
  Fixed Costs: 100% (deterministic)
  Discretionary Guidance: 90%+
  Authority Citations: 95%+
```

### 12.3 Scale Requirements

```yaml
System Capacity:
  Total Nodes: 10,000+
  Relationships: 50,000+
  Concurrent Users: 100
  Queries per second: 10
  Case extractions per day: 100
```

---

## 13. Testing Strategy

### 13.1 Unit Tests

```python
def test_tree_node_creation():
    """Test TreeNode creation with all fields"""
    node = TreeNode(
        node_id="TEST-001",
        citation="Test Rule 1",
        source_type=SourceType.RULE,
        what=[{"proposition": "Test rule", "confidence": 0.9}]
    )
    assert node.node_id == "TEST-001"
    assert len(node.what) == 1
    assert node.what[0]['confidence'] == 0.9

def test_extraction_patterns():
    """Test pattern extraction accuracy"""
    text = "The court held that costs must follow the event"
    extractor = CaseLawCostsExtractor()
    holdings = extractor.extract_holdings(text)
    assert "costs must follow the event" in holdings[0]

def test_reasoning_chain():
    """Test reasoning chain builder"""
    engine = QueryEngine()
    chain = engine.build_chain("Can winner lose costs?")
    assert len(chain) >= 2  # At least rule + case
    assert chain[0]['type'] == 'rule'
```

### 13.2 Integration Tests

```python
def test_end_to_end_query():
    """Test complete query processing"""
    
    # Setup
    system = CostsAdvisorySystem()
    
    # Query
    result = system.query("Default judgment costs in High Court?")
    
    # Assertions
    assert result['answer'] is not None
    assert '$2,300' in result['answer']
    assert 'O.21 Appendix 1' in result['authorities']
    assert result['confidence'] > 0.8
```

### 13.3 Validation Dataset

```yaml
Test Corpus:
  Rules: Order 21 (all 29 rules)
  Cases: 20 landmark costs cases
  Queries: 100 real lawyer queries
  
  Validation Set:
    - 50 costs calculation queries
    - 30 discretionary costs queries
    - 20 procedural queries
  
  Expected Accuracy:
    - Fixed costs: 100%
    - Case principles: 90%+
    - Complex reasoning: 85%+
```

---

## 14. User Interface Specifications

### 14.1 Query Interface

```typescript
interface QueryRequest {
  query: string;               // Natural language query
  context?: {
    court_level?: string;      // HC, DC, MC
    case_type?: string;        // default, summary, trial
    amount?: number;           // Claim amount
  };
  include_reasoning?: boolean; // Show reasoning chain
}

interface QueryResponse {
  answer: string;              // Natural language answer
  confidence: number;          // 0.0-1.0
  
  authorities: Citation[];     // Legal authorities
  
  reasoning_chain?: Step[];   // Optional reasoning steps
  
  breakdown?: {               // For costs calculations
    base: number;
    additional: number;
    disbursements: number;
    total: number;
  };
  
  warnings?: string[];        // Risk factors
}
```

### 14.2 Sample UI Flow

```
User: "What costs if I lose summary judgment in District Court?"

System:
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Answer:                                          â”‚
â”‚                                                  â”‚
â”‚ If you lose a summary judgment application in   â”‚
â”‚ District Court, you will likely pay:            â”‚
â”‚                                                  â”‚
â”‚ â€¢ Costs: $3,000 - $10,000                      â”‚
â”‚ â€¢ Basis: Standard basis (reasonable costs)      â”‚
â”‚ â€¢ Timeline: Payment within 14 days              â”‚
â”‚                                                  â”‚
â”‚ Authorities:                                    â”‚
â”‚ â€¢ O.21 Appendix 1, Part 2(c)                   â”‚
â”‚ â€¢ O.21 r.3(2) - Costs follow event             â”‚
â”‚                                                  â”‚
â”‚ âš ï¸ Warning: Failure to comply with Order 5     â”‚
â”‚ (ADR) may increase costs liability              â”‚
â”‚                                                  â”‚
â”‚ [Show Reasoning] [Save] [New Query]            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## 15. Deployment Architecture

### 15.1 Docker Compose Configuration

```yaml
version: '3.8'

services:
  # Database Layer
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: legal_tree
      POSTGRES_USER: legal_admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
      - ./sql/seed.sql:/docker-entrypoint-initdb.d/02-seed.sql
  
  neo4j:
    image: neo4j:5.0
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
    ports:
      - "7474:7474"  # Browser
      - "7687:7687"  # Bolt
    volumes:
      - neo4j_data:/data
  
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
  
  # Application Layer
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    environment:
      DATABASE_URL: postgresql://legal_admin:${DB_PASSWORD}@postgres:5432/legal_tree
      NEO4J_URL: bolt://neo4j:7687
      REDIS_URL: redis://redis:6379
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - neo4j
      - redis
  
  # ML/NLP Services
  extractor:
    build:
      context: .
      dockerfile: Dockerfile.extractor
    environment:
      MODEL_PATH: /models
      SPACY_MODEL: en_core_web_lg
    volumes:
      - ./models:/models
    depends_on:
      - postgres
  
  # Frontend
  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://api:8000
    depends_on:
      - api

volumes:
  postgres_data:
  neo4j_data:
  redis_data:
```

### 15.2 Production Considerations

```yaml
Security:
  - JWT authentication
  - Role-based access (lawyer, clerk, admin)
  - Audit logging for all queries
  - Encrypted data at rest
  - HTTPS only

Scalability:
  - Horizontal scaling for API servers
  - Read replicas for PostgreSQL
  - Redis cluster for caching
  - CDN for static assets

Monitoring:
  - Prometheus metrics
  - Grafana dashboards
  - ELK stack for logs
  - Sentry for error tracking

Backup:
  - Daily PostgreSQL backups
  - Neo4j graph exports
  - Point-in-time recovery
  - Disaster recovery plan
```

---

## 16. Business Value & ROI

### 16.1 Time Savings

```yaml
Traditional Process:
  - Find relevant rule: 5 minutes
  - Find relevant cases: 10 minutes
  - Extract principles: 10 minutes
  - Calculate costs: 5 minutes
  Total: 30 minutes per query

With Tree Logic System:
  - Enter query: 30 seconds
  - Get answer: 2 seconds
  Total: < 1 minute

Savings: 29 minutes per query
Daily queries per lawyer: 10
Daily savings: 290 minutes (4.8 hours)
```

### 16.2 Error Reduction

```yaml
Common Errors Prevented:
  - Wrong cost scales: $10,000+ mistakes
  - Missing Order 5 duties: Adverse costs
  - Outdated case law: Professional liability
  - Calculation errors: Client disputes

Error Rate:
  Traditional: 5-10% of costs advice
  With System: <1% (only edge cases)
```

### 16.3 Competitive Advantage

```yaml
Market Position:
  - First legal logic system in Southeast Asia
  - Patent-pending technology
  - 6-12 month lead over competitors
  - Scalable to other legal domains

Revenue Opportunities:
  - SaaS for law firms: $500-2000/month
  - API licensing: $0.10 per query
  - Custom implementations: $50,000+
  - Training and consulting: $5,000/day
```

---

## APPENDIX A: Glossary

```yaml
Tree Node: A structured representation of a legal authority
Logic Branch: A category of logical deduction (WHAT, IF-THEN, etc.)
Extraction Confidence: Probability that extraction is accurate (0.0-1.0)
Reasoning Chain: Sequence of logical steps to reach conclusion
Authority Weight: Hierarchical importance (statute=1.0, case=0.6-0.7)
Modal Logic: Study of necessity and possibility (MUST vs MAY)
Relationship: How one legal authority affects another
Traversal: Following connections through the graph
```

---

## APPENDIX B: Sample Queries & Answers

```yaml
Query 1: "Default judgment 3 defendants High Court"
Answer: "$2,600 (base $2,300 + $300 additional defendants)"

Query 2: "Can winner be ordered to pay costs?"
Answer: "Yes, if failed to comply with Order 5 ADR duty or acted unreasonably"

Query 3: "Motor accident $8,000 settled after defence"
Answer: "$1,200-$1,500 standard costs"

Query 4: "Interest rate on costs?"
Answer: "5.33% per annum from assessment date"

Query 5: "Time to pay costs after order?"
Answer: "14 days unless court extends"
```

---

## Document Version

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0 | 2024-12-19 | System Architecture Team | Complete rewrite with full Tree Logic explanation |
| 1.0 | 2024-12-19 | Initial Team | Original specification |

---

**END OF SPECIFICATION v2.0**