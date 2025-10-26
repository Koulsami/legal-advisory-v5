# Legal Advisory System v6.0 - Implementation Plan
**4-Phase Conversational AI with Validation**
**Date:** 2025-10-26

---

## EXECUTIVE SUMMARY

This document outlines the implementation plan for upgrading from v5.0 (Hybrid AI + Logic Tree) to v6.0 (4-Phase Conversational AI with MyKraws personality and mandatory validation).

### Key Architectural Changes

| Aspect | v5.0 | v6.0 |
|--------|------|------|
| **Conversation Flow** | Hybrid extraction + validation | 4 distinct phases with personality |
| **Question Style** | Logic tree questions, AI enhanced | AI-driven natural interrogation |
| **Personality** | Generic professional | MyKraws - friendly legal neighbor |
| **Validation** | Optional enhancement | MANDATORY before user delivery |
| **Advisory Depth** | Calculation + basic explanation | Comprehensive legal advisory |
| **Greeting** | None | Contextual greeting (Phase 1) |

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                     MyKraws Personality Layer                │
│              (Friendly, Warm, Approachable)                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   4-Phase Conversation Manager               │
├─────────────────────────────────────────────────────────────┤
│  Phase 1: GREETING & INTRODUCTION                            │
│  - Contextual greeting based on time/user history            │
│  - MyKraws introduces itself                                 │
│  - Sets friendly, approachable tone                          │
├─────────────────────────────────────────────────────────────┤
│  Phase 2: UNDERSTANDING USER NEED                            │
│  - Open-ended "How can I help?" question                     │
│  - Intent recognition → Module identification                │
│  - Transition to interrogation                               │
├─────────────────────────────────────────────────────────────┤
│  Phase 3: AI-DRIVEN INFORMATION GATHERING                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. AI Interrogation Engine                             │  │
│  │    - Rules of Court provided as context               │  │
│  │    - Personality guidelines provided                  │  │
│  │    - Generates natural questions                      │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ 2. MANDATORY VALIDATION LAYER (CRITICAL!)             │  │
│  │    - Citation verification                            │  │
│  │    - Requirement verification                         │  │
│  │    - Field verification                               │  │
│  │    - Hallucination detection                          │  │
│  │    - 100% coverage - ZERO unvalidated responses       │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ 3. Information Extraction                             │  │
│  │    - Extract structured data from user responses      │  │
│  │    - Update filled_fields                             │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ 4. Sufficiency Detection                              │  │
│  │    - Check if enough information gathered             │  │
│  │    - Transition to Phase 4 when sufficient           │  │
│  └───────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Phase 4: SPECIALIST ANALYSIS & COMPREHENSIVE ADVISORY       │
│  - Accurate cost calculation (100%)                          │
│  - Applicable rules identification                           │
│  - What you CAN claim                                        │
│  - What you CANNOT claim                                     │
│  - Strategic recommendations                                 │
│  - Risk assessment                                           │
│  - ADR impact analysis                                       │
│  - Settlement offer analysis                                 │
│  - Complexity & urgency analysis                             │
│  - Opponent conduct analysis                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## IMPLEMENTATION COMPONENTS

### Component 1: MyKraws Personality System

**File:** `backend/mykraws/personality_manager.py`

**Responsibilities:**
- Contextual greeting generation (12+ variations)
- Time-based greetings (morning/afternoon/evening/night)
- User history awareness (first-time vs returning)
- Personality guidelines provision to AI
- Consistent tone enforcement

**Data:**
```python
GREETINGS = {
    "early_morning": [
        "Good morning! ☀️ I'm MyKraws, your friendly legal neighbor...",
        "Rise and shine! I'm MyKraws, and I'm here to help...",
        "Early start today? I'm MyKraws, your legal companion..."
    ],
    "morning": [...],
    "afternoon": [...],
    "evening": [...],
    "night": [...]
}

PERSONALITY_GUIDELINES = {
    "tone": "friendly, warm, approachable",
    "style": "like a helpful neighbor, not a lawyer",
    "language": "simple, clear, avoid legalese",
    "emoji_usage": "occasional, not excessive",
    "empathy": "acknowledge stress of legal matters"
}
```

### Component 2: 4-Phase Conversation Manager

**File:** `backend/mykraws/conversation_manager_v6.py`

**Phase State Machine:**
```python
class ConversationPhase(Enum):
    GREETING = "greeting"
    ASK_HELP = "ask_help"
    INTERROGATION = "interrogation"
    ANALYSIS = "analysis"
    COMPLETE = "complete"

class PhaseManager:
    def determine_phase(session) -> ConversationPhase:
        if not session.greeting_delivered:
            return ConversationPhase.GREETING
        if not session.help_requested:
            return ConversationPhase.ASK_HELP
        if not session.sufficient_information:
            return ConversationPhase.INTERROGATION
        if not session.analysis_complete:
            return ConversationPhase.ANALYSIS
        return ConversationPhase.COMPLETE
```

### Component 3: AI Interrogation Engine

**File:** `backend/mykraws/ai_interrogator.py`

**Key Features:**
- Provides Rules of Court as context to AI
- Provides personality guidelines
- Generates ONE question at a time
- Explains WHY information is needed
- References specific rules when explaining

**Prompt Structure:**
```python
INTERROGATION_PROMPT = """
You are MyKraws, a friendly legal neighbor helping with Singapore legal matters.

PERSONALITY GUIDELINES:
{personality_guidelines}

RULES OF COURT CONTEXT:
{rules_of_court}

CONVERSATION HISTORY:
{conversation_history}

INFORMATION GATHERED SO FAR:
{filled_fields}

STILL NEEDED:
{required_fields}

YOUR TASK:
Generate ONE natural question to gather the next piece of information.
- Be friendly and conversational
- Explain WHY you need this information
- Reference the specific Rule of Court that requires it
- Acknowledge the user's previous answer first

Question:
"""
```

### Component 4: Mandatory Validation Layer

**File:** `backend/mykraws/response_validator.py`

**CRITICAL COMPONENT - 100% Coverage Required**

**Validation Checks:**
```python
class ResponseValidator:
    def validate(self, ai_response: str, rules_context: List[Rule]) -> ValidationResult:
        checks = [
            self._verify_citations(ai_response, rules_context),
            self._verify_requirements(ai_response, rules_context),
            self._verify_fields(ai_response, valid_fields),
            self._detect_hallucinations(ai_response, rules_context),
            self._check_consistency(ai_response, conversation_history)
        ]

        if all(check.passed for check in checks):
            return ValidationResult(passed=True, response=ai_response)
        else:
            # Attempt correction
            corrected = self._correct_response(ai_response, checks)
            return self._validate(corrected)  # Re-validate
```

**Validation Rules:**
- ✅ All cited rules (e.g., "Order 21, Rule 10") must exist in provided context
- ✅ All stated requirements must actually exist in cited rules
- ✅ All mentioned fields must be valid module fields
- ✅ No invented legal concepts or rules
- ✅ Consistent with previous validated information

**Failure Handling:**
1. Log original response and issues
2. Generate corrected response
3. Re-validate corrected response
4. Maximum 2 correction attempts
5. Fall back to structured question if correction fails

### Component 5: Comprehensive Advisory Engine

**File:** `backend/mykraws/comprehensive_advisor.py`

**Enhanced Phase 4 Analysis:**

```python
class ComprehensiveAdvisor:
    def generate_advisory(self, calculation_result, filled_fields, rules) -> Advisory:
        return Advisory(
            calculation_summary=self._format_calculation(calculation_result),
            applicable_rules=self._identify_applicable_rules(filled_fields, rules),
            can_claim=self._analyze_entitlements(filled_fields, rules),
            cannot_claim=self._analyze_restrictions(filled_fields, rules),
            strategic_recommendations=self._generate_recommendations(filled_fields),
            risk_assessment=self._assess_risks(filled_fields),
            adr_analysis=self._analyze_adr_impact(filled_fields),
            settlement_analysis=self._analyze_settlement_offers(filled_fields),
            complexity_analysis=self._analyze_complexity(filled_fields),
            opponent_conduct=self._analyze_opponent_conduct(filled_fields),
            procedural_requirements=self._identify_procedures(filled_fields),
            action_items=self._generate_action_items(filled_fields)
        )
```

**Advisory Components:**

1. **What You CAN Claim**
   - Specific entitlements under identified rules
   - Conditions for each entitlement
   - Estimated amounts or ranges

2. **What You CANNOT Claim**
   - Limitations under rules
   - What opponent cannot claim (if favorable)
   - Exceptions to be aware of

3. **Strategic Recommendations**
   - Actionable steps (prioritized: High/Medium/Low)
   - Documentation requirements
   - Timing considerations

4. **Risk Assessment**
   - Potential challenges
   - Likelihood of each risk
   - Mitigation strategies

5. **ADR Impact Analysis** (FR-P4-05)
   - If ADR refused by opponent → adverse costs entitlement
   - If ADR refused by user → cost consequences warning
   - Reference Order 5, Rule 1 and Order 21, Rule 4(c)
   - Cite relevant case law

6. **Settlement Offer Analysis** (FR-P4-06)
   - Order 22A analysis
   - Indemnity costs if judgment exceeded offer

7. **Complexity & Urgency** (FR-P4-07)
   - Order 21, Rule 2(2)(b) - complexity
   - Order 21, Rule 2(2)(c) - urgency

8. **Opponent Conduct** (FR-P4-08)
   - Frivolous/vexatious conduct
   - Order 21, Rule 4(c) - indemnity costs

---

## DATA STRUCTURES

### Session State (Extended)

```python
@dataclass
class ConversationSessionV6:
    # Existing v5 fields
    session_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    filled_fields: Dict[str, Any]

    # NEW v6 fields
    current_phase: ConversationPhase
    greeting_delivered: bool = False
    help_requested: bool = False
    sufficient_information: bool = False
    analysis_complete: bool = False

    # User context for personalization
    user_context: Dict[str, Any] = field(default_factory=dict)
    # {
    #   "returning_user": bool,
    #   "user_name": str (optional),
    #   "last_visit": datetime (optional)
    # }

    # Validation tracking
    validation_history: List[ValidationLog] = field(default_factory=list)
```

### Validation Log

```python
@dataclass
class ValidationLog:
    timestamp: datetime
    original_response: str
    validation_result: bool  # True = passed, False = failed
    issues_found: List[str]
    corrected_response: Optional[str]
    correction_attempts: int
    rules_checked_against: List[str]
```

---

## IMPLEMENTATION PHASES

### Phase A: Foundation (Day 1)
- ✅ Create MyKraws personality system
- ✅ Implement greeting generator
- ✅ Update session data structures
- ✅ Create phase state machine

### Phase B: AI Interrogation (Day 2)
- ✅ Build AI interrogation engine
- ✅ Create Rules of Court context provider
- ✅ Implement question generation
- ✅ Test natural conversation flow

### Phase C: Validation Layer (Day 3) **CRITICAL**
- ✅ Build response validator
- ✅ Implement all 5 validation checks
- ✅ Create correction mechanism
- ✅ Test validation coverage (must be 100%)

### Phase D: Comprehensive Advisory (Day 4)
- ✅ Enhance Phase 4 analysis
- ✅ Implement all advisory components
- ✅ Add ADR/settlement/complexity analysis
- ✅ Format comprehensive output

### Phase E: Integration & Testing (Day 5)
- ✅ Integrate all components
- ✅ End-to-end testing
- ✅ Validation coverage testing
- ✅ User acceptance testing

---

## MIGRATION STRATEGY

### Backward Compatibility

**Option 1: Side-by-side deployment**
- Deploy v6 as separate endpoint `/api/v6/conversation`
- Keep v5 running at `/api/conversation`
- Gradual migration of users

**Option 2: Feature flag**
- Single endpoint with feature flag
- `use_v6_conversation: boolean` in request
- A/B testing capability

**Recommended: Option 1** - Safer, allows rollback

### Data Migration

Existing v5 sessions:
- Can continue in v5 mode
- New sessions use v6
- No migration of active sessions needed

---

## TESTING STRATEGY

### Unit Tests

1. **Personality System**
   - Greeting variations (12+ unique)
   - Time-based selection
   - User context handling

2. **Phase Manager**
   - Phase transition logic
   - State persistence
   - Edge cases

3. **AI Interrogation**
   - Question generation quality
   - Rules context provision
   - Personality consistency

4. **Validation Layer** (CRITICAL)
   - Citation verification accuracy
   - Hallucination detection
   - Correction success rate
   - 100% coverage verification

5. **Comprehensive Advisory**
   - All 8 advisory components
   - Accuracy of recommendations
   - Format correctness

### Integration Tests

1. **Complete 4-Phase Flow**
   - Greeting → Ask Help → Interrogation → Analysis
   - Phase transitions
   - Data persistence

2. **Validation Integration**
   - AI responses validated before delivery
   - Failed validations corrected
   - Zero unvalidated responses to users

3. **End-to-End Scenarios**
   - Simple case (default judgment)
   - Complex case (contested trial + ADR + settlement)
   - Error cases (validation failures)

### Acceptance Tests

1. **Legal Accuracy**
   - 100% calculation accuracy
   - Zero hallucinated rules
   - Correct rule citations

2. **User Experience**
   - Conversation naturalness
   - Personality consistency
   - Response quality

3. **Performance**
   - Phase 1: <500ms
   - Phase 3: <3s per question
   - Phase 4: <5s total
   - Validation: <500ms

---

## SUCCESS CRITERIA

### MVP Ready
- ✅ All P0 requirements implemented
- ✅ 4 phases functional
- ✅ Validation catches ≥95% of hallucinations
- ✅ Legal accuracy 100% in testing
- ✅ Zero critical bugs

### Production Ready
- ✅ Validation catches ≥99% of hallucinations
- ✅ Legal accuracy 100% across 100+ test cases
- ✅ User satisfaction ≥90% (beta testing)
- ✅ Performance requirements met
- ✅ Security audit passed

---

## TIMELINE

| Phase | Duration | Status |
|-------|----------|--------|
| Foundation | 1 day | Pending |
| AI Interrogation | 1 day | Pending |
| Validation Layer | 1 day | Pending |
| Comprehensive Advisory | 1 day | Pending |
| Integration & Testing | 1 day | Pending |
| **Total** | **5 days** | **Not Started** |

---

## RISKS & MITIGATION

| Risk | Mitigation |
|------|------------|
| Validation layer too slow | Optimize, cache rule checks |
| AI hallucinations slip through | Multi-layer validation, human review |
| User finds conversation confusing | Clear phase indicators, progress bar |
| Too many questions annoy users | Optimize to 5-7 questions average |

---

## DELIVERABLES

1. **Code:**
   - `backend/mykraws/` - All v6 components
   - Updated conversation manager
   - Updated API routes

2. **Documentation:**
   - V6 Architecture Document
   - API Documentation
   - Validation Rules Reference

3. **Tests:**
   - Unit tests for all components
   - Integration tests
   - Validation coverage tests

4. **Deployment:**
   - Railway deployment (v6 endpoint)
   - Frontend updates
   - Migration guide

---

**Status:** Ready to begin implementation
**Priority:** P0 - Critical
**Owner:** Development Team
**Target Completion:** 5 days from start
