# Appendix G Integration Plan
## Practice Directions Cost Guidelines Integration

### Executive Summary

This document outlines the plan to integrate Appendix G (Practice Directions cost guidelines) with the existing Order 21 (Rules of Court) implementation in the Legal Advisory System.

---

## 1. Current State vs. Target State

### Current Implementation (Order 21 Module)
✅ **Covers:**
- Default judgments (liquidated/unliquidated)
- Summary judgments
- Fixed cost scales by claim amount
- Court level adjustments

❌ **Missing:**
- Interlocutory applications (adjournments, striking out, injunctions, etc.)
- Trial cost breakdowns (pre-trial, trial, post-trial)
- Originating applications (arbitration, insolvency, etc.)
- Appeals costs

### Target State (Order 21 + Appendix G)
✅ **Will Cover:**
- Everything above PLUS
- 19 types of interlocutory applications
- 9 categories of trial costs
- 6 types of originating applications
- 5 levels of appeal costs
- **Total: 80+ distinct cost scenarios**

---

## 2. Data Structure Analysis

### Appendix G Content Breakdown

#### Part II: Summonses
**A. General**
- Uncontested: $1,000 – $5,000
- Contested (< 45 mins): $2,000 – $5,000
- Contested (≥ 45 mins): $4,000 – $11,000
- Complex (3hrs): $9,000 – $22,000

**B. Specific (19 types)**
1. Adjournment: $500 – $2,000
2. Extension of time: $1,000 – $4,000
3. Amendment of pleadings: $1,000 – $7,000
4. Further and better particulars: $2,000 – $9,000
5. Production of documents: $3,000 – $11,000
6. Security for costs: $2,000 – $10,000
7. Interim payments: $2,000 – $10,000
8. Striking out (partial): $3,000 – $12,000
9. Striking out (whole): $6,000 – $20,000
10. Summary judgment (given): $6,000 – $20,000
11. Summary judgment (dismissed): $6,000 – $20,000
12. Setting aside judgment: $2,000 – $19,000
13. Stay (arbitration): $5,000 – $23,000
14. Stay (forum non conveniens): $6,000 – $21,000
15. Stay (pending appeal): $3,000 – $11,000
16. Examination of Enforcement Respondent: $3,000 – $10,000
17. Discharge of solicitor: $1,000 – $4,000
18. Setting aside service: $3,000 – $14,000
19. Permission to appeal: $4,000 – $15,000
20. Division of issues: $3,000 – $12,000
21. Injunction/search order: $10,000 – $35,000
22. Committal order: $4,000 – $16,000
23. Unless order: $2,000 – $10,000

#### Part III: Trials
**Categories (9 types with 3-phase breakdown):**

1. **Motor Accident / Simple Torts**
   - Pre-trial: $15,000 – $45,000
   - Trial (daily): $6,000 – $12,000
   - Post-trial: Up to $15,000

2. **Torts / Commercial**
   - Pre-trial: $25,000 – $70,000
   - Trial (daily): $6,000 – $16,000
   - Post-trial: Up to $30,000

3. **Equity and Trusts**
   - Pre-trial: $25,000 – $90,000
   - Trial (daily): $6,000 – $16,000
   - Post-trial: Up to $35,000

4. **Construction / IP / Admiralty / Medical Negligence**
   - Pre-trial: $30,000 – $90,000
   - Trial (daily): $6,000 – $18,000
   - Post-trial: Up to $35,000

**Settled Before Trial (breakdown by phase):**
- Pleadings: $3,000 – $18,000
- Production of Documents: $6,000 – $35,000
- AEICs: $6,000 – $35,000

#### Part IV: Originating Applications
**General:**
- Uncontested: $5,000 – $13,000
- Contested: $12,000 – $30,000 per day

**Specific (6 types):**
1. Arbitration: $13,000 – $40,000
2. Insolvency: $12,000 – $35,000
3. Judicial review: $14,000 – $35,000
4. Mortgage action: $5,000 – $15,000
5. Order 6, Rule 1(3)(c): $12,000 – $30,000
6. SOPA: $6,000 – $20,000

#### Part V: Appeals
1. General Division: $5,000 – $35,000
2. Appellate Division (interlocutory): $15,000 – $40,000
3. Appellate Division (trial): $30,000 – $150,000
4. Applications (without hearing): $6,000 – $20,000
5. Applications (with hearing): $9,000 – $35,000

---

## 3. Integration Architecture

### Approach: Modular Extension

```
Current:                              Enhanced:

Order21Module                        Order21Module (Core)
└── calculate()                           ├── calculate()  [existing]
    ├── default_judgment                  │   ├── default_judgment
    ├── summary_judgment                  │   ├── summary_judgment
    └── appendix1_scales                  │   └── appendix1_scales
                                          │
                                          └── calculate_appendix_g()  [NEW]
                                              ├── summons_costs()
                                              ├── trial_costs()
                                              ├── originating_app_costs()
                                              └── appeal_costs()
```

### Why This Approach?

1. **Maintains Backward Compatibility**: Existing Order 21 logic unchanged
2. **Clear Separation**: Order 21 (fixed scales) vs Appendix G (guidelines)
3. **Easy Testing**: Can test each section independently
4. **Phased Implementation**: Can roll out incrementally

---

## 4. Logic Tree Extensions

### New Node Types Needed

```python
# Existing nodes (38 nodes)
ORDER_21_ROOT
├── HIGH_COURT
├── DISTRICT_COURT
├── MAGISTRATES_COURT
└── [existing 35 nodes]

# New Appendix G nodes (estimate: 60+ nodes)
APPENDIX_G_ROOT  [NEW]
├── SUMMONSES
│   ├── GENERAL
│   │   ├── UNCONTESTED
│   │   └── CONTESTED
│   │       ├── LESS_THAN_45_MINS
│   │       ├── MORE_THAN_45_MINS
│   │       └── COMPLEX_3HRS
│   └── SPECIFIC
│       ├── ADJOURNMENT
│       ├── EXTENSION_OF_TIME
│       ├── AMENDMENT_PLEADINGS
│       ├── STRIKING_OUT_PARTIAL
│       ├── STRIKING_OUT_WHOLE
│       ├── SUMMARY_JUDGMENT_GIVEN
│       ├── SUMMARY_JUDGMENT_DISMISSED
│       ├── INJUNCTION
│       └── [14 more types]
├── TRIALS
│   ├── MOTOR_ACCIDENT
│   ├── SIMPLE_TORTS
│   ├── TORTS
│   ├── COMMERCIAL
│   ├── EQUITY_TRUSTS
│   ├── CONSTRUCTION
│   ├── IP_IT
│   ├── ADMIRALTY
│   └── MEDICAL_NEGLIGENCE
│       ├── PRE_TRIAL
│       ├── TRIAL_DAILY
│       └── POST_TRIAL
├── ORIGINATING_APPLICATIONS
│   ├── ARBITRATION
│   ├── INSOLVENCY
│   ├── JUDICIAL_REVIEW
│   ├── MORTGAGE_ACTION
│   └── [2 more types]
└── APPEALS
    ├── GENERAL_DIVISION
    ├── APPELLATE_DIVISION_INTERLOCUTORY
    ├── APPELLATE_DIVISION_TRIAL
    └── APPLICATIONS
```

### Total Nodes After Integration: ~100 nodes

---

## 5. Pattern Extraction Updates

### New Fields to Extract

```python
# Current extraction
{
    "court_level": "High Court",
    "case_type": "default_judgment",
    "claim_amount": 50000.0,
    "complexity_level": "moderate"
}

# Enhanced extraction (NEW fields)
{
    # Existing
    "court_level": "High Court",
    "case_type": "default_judgment",
    "claim_amount": 50000.0,
    "complexity_level": "moderate",

    # NEW - Application Type
    "application_type": "striking_out",  # or "injunction", "adjournment", etc.
    "application_contested": True,
    "application_duration_mins": 60,

    # NEW - Trial Phase
    "trial_phase": "pre_trial",  # or "trial", "post_trial", "settled_before_trial"
    "trial_days": 3,
    "case_category": "commercial",  # motor_accident, torts, construction, etc.

    # NEW - Appeal Info
    "appeal_level": "appellate_division",
    "appeal_from": "interlocutory",  # or "trial"

    # NEW - Originating Application
    "originating_app_type": "arbitration"  # or "insolvency", "judicial_review", etc.
}
```

### Pattern Matching Examples

```
User Query: "Calculate costs for striking out application"
→ Extracted: {"application_type": "striking_out", "source": "appendix_g"}

User Query: "What are the costs for a commercial trial that lasted 5 days?"
→ Extracted: {"case_category": "commercial", "trial_phase": "trial", "trial_days": 5, "source": "appendix_g"}

User Query: "Appeal to Appellate Division from summary judgment"
→ Extracted: {"appeal_level": "appellate_division", "appeal_from": "interlocutory", "source": "appendix_g"}

User Query: "High Court default judgment for $50,000"
→ Extracted: {"court_level": "High Court", "case_type": "default_judgment", "claim_amount": 50000, "source": "order_21"}
```

---

## 6. Calculation Logic

### Decision Tree

```
User Query
    │
    ├─→ Pattern Extraction
    │
    ├─→ Source Determination
    │   ├─→ Order 21? (default/summary judgment with claim amount)
    │   │   └─→ Use existing Order21Module.calculate()
    │   │
    │   └─→ Appendix G? (applications, trials, appeals)
    │       └─→ Use new Order21Module.calculate_appendix_g()
    │           │
    │           ├─→ Is it a summons?
    │           │   ├─→ Check specific types (Part IIB)
    │           │   └─→ Fallback to general (Part IIA)
    │           │
    │           ├─→ Is it a trial?
    │           │   ├─→ Identify category (commercial, torts, etc.)
    │           │   ├─→ Identify phase (pre-trial, trial, post-trial)
    │           │   └─→ Calculate per phase
    │           │
    │           ├─→ Is it an originating application?
    │           │   └─→ Match specific type or use general
    │           │
    │           └─→ Is it an appeal?
    │               └─→ Determine level and type
```

### Example Calculations

**Example 1: Striking Out Application**
```python
Input: {"application_type": "striking_out_whole", "contested": True}
Output: {
    "total_costs": 13000,  # midpoint
    "cost_range_min": 6000,
    "cost_range_max": 20000,
    "source": "Appendix G, Part II.B.8",
    "notes": [
        "Costs for application itself only",
        "Separate costs for action may be sought if successful"
    ]
}
```

**Example 2: Commercial Trial (5 days)**
```python
Input: {
    "case_category": "commercial",
    "trial_phase": "all",  # pre + trial + post
    "trial_days": 5
}
Output: {
    "pre_trial_costs": 57500,  # midpoint of $25k-$90k
    "trial_costs": 55000,  # 5 days × $11k/day (midpoint $6k-$16k)
    "post_trial_costs": 17500,  # midpoint of up to $30k
    "total_costs": 130000,
    "breakdown": {
        "pre_trial": {"min": 25000, "max": 90000},
        "trial_daily": {"min": 6000, "max": 16000, "days": 5},
        "post_trial": {"min": 0, "max": 30000}
    },
    "source": "Appendix G, Part III.A(i).4"
}
```

---

## 7. Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Create `appendix_g_data.py` with all cost data
- [ ] Design new data structures for Appendix G nodes
- [ ] Update `LogicTreeNode` dimensions for new types

### Phase 2: Pattern Extraction (Week 1-2)
- [ ] Extend `PatternExtractor` for new field types
- [ ] Add application type detection
- [ ] Add trial phase/category detection
- [ ] Add appeal level detection
- [ ] Add originating application detection

### Phase 3: Calculation Logic (Week 2)
- [ ] Implement `calculate_appendix_g()` method
- [ ] Implement `calculate_summons_costs()`
- [ ] Implement `calculate_trial_costs()`
- [ ] Implement `calculate_originating_app_costs()`
- [ ] Implement `calculate_appeal_costs()`

### Phase 4: Logic Tree Integration (Week 2-3)
- [ ] Build 60+ new Appendix G nodes
- [ ] Register nodes in tree framework
- [ ] Update matching engine weights for new node types
- [ ] Test tree traversal

### Phase 5: Testing & Validation (Week 3)
- [ ] Unit tests for each Appendix G section
- [ ] Integration tests with Order 21
- [ ] End-to-end tests with real queries
- [ ] Validation against actual court awards

### Phase 6: UI/API Updates (Week 3)
- [ ] Update `/chat` endpoint to handle new types
- [ ] Update response formatting for complex breakdowns
- [ ] Update test pages with new example queries
- [ ] Update documentation

---

## 8. Example Queries After Integration

```
1. "Calculate costs for a striking out application"
   → Appendix G Part II.B.8: $6,000 - $20,000

2. "What are trial costs for a commercial case lasting 3 days?"
   → Appendix G Part III.A(i).4:
      Pre-trial: $25,000 - $90,000
      Trial: 3 × ($6,000 - $16,000) = $18,000 - $48,000
      Post-trial: Up to $30,000

3. "Appeal to Court of Appeal from trial judgment"
   → Appendix G Part V: $30,000 - $150,000

4. "Costs for injunction application"
   → Appendix G Part II.B.17: $10,000 - $35,000

5. "Default judgment High Court $50,000"  [EXISTING]
   → Order 21 Appendix 1: $5,000 (range $3,000 - $7,000)
```

---

## 9. Data File Structure

### New File: `backend/modules/appendix_g_data.py`

```python
"""
Appendix G Cost Guidelines Data
Practice Directions - Supreme Court of Singapore
"""

APPENDIX_G_DATA = {
    "summonses": {
        "general": {
            "uncontested": {"min": 1000, "max": 5000},
            "contested_less_45": {"min": 2000, "max": 5000},
            "contested_45_plus": {"min": 4000, "max": 11000},
            "complex_3hrs": {"min": 9000, "max": 22000}
        },
        "specific": {
            "adjournment": {"min": 500, "max": 2000},
            "extension_of_time": {"min": 1000, "max": 4000},
            "amendment_pleadings": {"min": 1000, "max": 7000, "notes": ["Application only", "Separate costs for amendments may be sought"]},
            "striking_out_partial": {"min": 3000, "max": 12000},
            "striking_out_whole": {"min": 6000, "max": 20000, "notes": ["Application only", "Separate costs for action may be sought"]},
            "summary_judgment_given": {"min": 6000, "max": 20000, "notes": ["Application only", "Separate costs for action may be sought"]},
            "summary_judgment_dismissed": {"min": 6000, "max": 20000},
            # ... more types
        }
    },
    "trials": {
        "motor_accident": {"pre_trial": {"min": 15000, "max": 45000}, "trial_daily": {"min": 6000, "max": 12000}, "post_trial": {"max": 15000}},
        "simple_torts": {"pre_trial": {"min": 15000, "max": 45000}, "trial_daily": {"min": 6000, "max": 12000}, "post_trial": {"max": 15000}},
        "torts": {"pre_trial": {"min": 25000, "max": 70000}, "trial_daily": {"min": 6000, "max": 16000}, "post_trial": {"max": 30000}},
        # ... more categories
    },
    # ... more sections
}
```

---

## 10. Benefits of Integration

### For Users:
1. **Comprehensive Coverage**: 80+ cost scenarios vs current 10-15
2. **More Accurate Estimates**: Specific guidelines for their exact situation
3. **Better Breakdown**: See pre-trial, trial, post-trial costs separately
4. **Informed Decisions**: Understand cost implications of different procedural steps

### For System:
1. **Industry Standard**: Aligns with actual practice
2. **Authority**: Based on approved Supreme Court guidelines
3. **Completeness**: Covers full litigation lifecycle
4. **Flexibility**: Can handle complex multi-phase cases

---

## 11. Risks & Mitigation

### Risk 1: Complexity
**Issue**: 100 nodes, complex branching logic
**Mitigation**:
- Phased implementation
- Comprehensive testing at each phase
- Clear documentation

### Risk 2: Pattern Matching Accuracy
**Issue**: May misclassify application types
**Mitigation**:
- Use Claude AI to help classify ambiguous queries
- Provide users with classification for confirmation
- Allow manual override

### Risk 3: Maintaining Two Systems
**Issue**: Order 21 + Appendix G could diverge
**Mitigation**:
- Clear separation in code
- Document relationship explicitly
- Unified testing framework

---

## 12. Success Metrics

### Implementation Success:
- [ ] 100+ nodes in logic tree
- [ ] 95%+ test coverage for new code
- [ ] All 6 implementation phases complete

### User Success:
- [ ] Can handle 80+ cost scenarios
- [ ] Accurate cost estimates (±10% of actual awards)
- [ ] Natural language understanding of application types
- [ ] Clear breakdown of cost components

---

## 13. Timeline

**Total Estimated Time: 3 weeks (15 working days)**

| Phase | Days | Milestone |
|-------|------|-----------|
| Phase 1: Foundation | 2 | Data structures ready |
| Phase 2: Pattern Extraction | 3 | Can classify all query types |
| Phase 3: Calculation Logic | 3 | All calculations working |
| Phase 4: Logic Tree | 3 | 100 nodes registered |
| Phase 5: Testing | 2 | 95%+ coverage |
| Phase 6: UI/API | 2 | Production ready |

---

## 14. Next Steps

**Immediate Actions:**

1. **Review and Approve** this plan
2. **Create data file** with all Appendix G costs
3. **Start Phase 1** - Foundation work
4. **Test incrementally** as we build

**Questions for User:**

1. Should we prioritize any specific sections? (e.g., summonses first?)
2. Do you want me to start with Phase 1 immediately?
3. Are there any other Practice Directions we should consider?

---

## Appendix: Reference Documents

- **Order 21, Rules of Court 2021** (already implemented)
- **Appendix 1, Order 21** (fixed cost scales - already implemented)
- **Appendix G, Practice Directions** (this document - to be implemented)
- **Practice Directions Para. 138(1)** (cross-reference for Appendix G)

---

**Document Version**: 1.0
**Last Updated**: October 30, 2025
**Author**: Legal Advisory System v5.0 Team
