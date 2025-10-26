# Design Documentation Index

This document helps Claude Code quickly find relevant design information.

## 📚 Documentation Structure

```
legal-advisory-v5/
├── PROJECT_IMPLEMENTATION_PLAN.md          ← 40-day development plan
├── CLAUDE.md                               ← Project context for Claude Code
├── README.md                               ← Project overview ⭐
├── PROJECT_STATUS.md                       ← Current project status ⭐
├── USER_GUIDE.md                           ← End-user documentation ⭐ NEW
├── DEMO_GUIDE.md                           ← Presentation & demo guide ⭐ NEW
├── FINAL_TEST_REPORT.md                    ← Complete test analysis
├── SECURITY_REPORT.md                      ← Security audit results
├── PERFORMANCE_REPORT.md                   ← Performance benchmarks
├── KNOWN_ISSUES.md                         ← Issue tracking
├── demo/
│   └── interactive_demo.py                 ← Interactive demonstration ⭐ NEW
├── examples/
│   ├── api_examples.sh                     ← Shell API examples ⭐ NEW
│   └── api_client_example.py               ← Python API client ⭐ NEW
└── docs/
    ├── 02_High_Level_Design_v5_MODULAR.md  ← System architecture ⭐
    ├── INTERFACE_DEFINITIONS.md            ← All ABC specifications ⭐
    ├── legal-logic-tree-spec__1_.md        ← Logic tree structure
    ├── 01_Requirements_Specification_v4_Conversation.md
    ├── 03_Low_Level_Design_v5_Part1.md
    ├── 03_Low_Level_Design_v5_Part2.md
    ├── COMPREHENSIVE_LEGAL_ADVISORY_IMPLEMENTATION.md
    ├── HYBRID_SUPERIORITY_EXAMPLES.md
    ├── ARCHITECTURE_UPDATE_v4_to_v5.md
    └── Rules_of_Court_202113.pdf           ← Singapore legal regulations
```

## 🎯 Quick Reference Guide

### When Implementing Components

**Question:** "What interface should I implement?"
**Read:** `docs/INTERFACE_DEFINITIONS.md`

**Question:** "What's the architecture design?"
**Read:** `docs/02_High_Level_Design_v5_MODULAR.md`

**Question:** "What am I building today?"
**Read:** `PROJECT_IMPLEMENTATION_PLAN.md`

**Question:** "How do logic trees work?"
**Read:** `docs/legal-logic-tree-spec__1_.md`

**Question:** "What are the requirements?"
**Read:** `docs/01_Requirements_Specification_v4_Conversation.md`

### By Topic

#### Architecture & Design
- **High-Level Architecture:** `docs/02_High_Level_Design_v5_MODULAR.md` (sections 1-3)
- **Low-Level Design:** `docs/03_Low_Level_Design_v5_Part1.md` and `Part2.md`
- **Architecture Evolution:** `docs/ARCHITECTURE_UPDATE_v4_to_v5.md`

#### Interfaces & Data Structures
- **All Interface Definitions:** `docs/INTERFACE_DEFINITIONS.md`
- **Core Data Structures:** Section in `INTERFACE_DEFINITIONS.md`
- **Logic Tree Nodes:** `docs/legal-logic-tree-spec__1_.md`

#### Implementation
- **40-Day Roadmap:** `PROJECT_IMPLEMENTATION_PLAN.md`
- **Current Status:** `CLAUDE.md` (updated regularly)
- **Hybrid AI Strategy:** `docs/HYBRID_SUPERIORITY_EXAMPLES.md`

#### Legal Domain
- **Singapore Rules:** `docs/Rules_of_Court_202113.pdf`
- **Requirements:** `docs/01_Requirements_Specification_v4_Conversation.md`

## 📖 Documentation Sections by Phase

### Phase 1-2: Foundation (Days 1-8) ✅ COMPLETE
- **Reference:** `CLAUDE.md` - Current Status section
- **Interfaces:** `docs/INTERFACE_DEFINITIONS.md` - All 8 ABCs
- **Config:** Section 2.3 in High-Level Design

### Phase 3: Common Services (Days 9-13) ✅ COMPLETE
- **Logic Tree Framework:** 
  - Design: Section 3.4.1 in `docs/02_High_Level_Design_v5_MODULAR.md`
  - Spec: `docs/legal-logic-tree-spec__1_.md`
- **Matching Engine:**
  - Design: Section 3.4.2 in High-Level Design
  - Interface: `IMatchingEngine` in INTERFACE_DEFINITIONS.md
- **Module Registry:**
  - Design: Section 3.4.3 in High-Level Design
- **Analysis Engine:**
  - Design: Section 3.4.4 in High-Level Design

### Phase 4: Hybrid AI Layer (Days 14-17) 🎯 NEXT
- **Hybrid Strategy:** `docs/HYBRID_SUPERIORITY_EXAMPLES.md`
- **Architecture:** Section 3.3 in `docs/02_High_Level_Design_v5_MODULAR.md`
- **AI Orchestrator:** Section 3.3.1
- **AI Service:** Section 3.3.2
- **Validator:** Section 3.3.3

### Phase 5: Legal Modules (Days 18-22)
- **Module Structure:** Section 3.5 in High-Level Design
- **Order 21:** Section 3.5.1
- **Legal Rules:** `docs/Rules_of_Court_202113.pdf`

### Phase 6: Conversation Layer (Days 23-28)
- **Design:** Section 3.2 in High-Level Design
- **Session Management:** Section 3.2.2
- **Conversation Flow:** Section 3.2.3

### Phase 7: Integration, Performance & Security (Days 29-33) ✅ COMPLETE
- **Integration Testing:** `tests/integration/test_complete_system_flow.py`
- **Performance Report:** `PERFORMANCE_REPORT.md`
- **Security Audit:** `SECURITY_REPORT.md`
- **Final Test Report:** `FINAL_TEST_REPORT.md`
- **Known Issues:** `KNOWN_ISSUES.md`

### Phase 8: Demo & Documentation (Days 34-36) ✅ COMPLETE
- **User Guide:** `USER_GUIDE.md` - Complete end-user documentation
- **Demo Guide:** `DEMO_GUIDE.md` - Presentation and demonstration guide
- **Interactive Demo:** `demo/interactive_demo.py` - 6 demo scenarios
- **API Examples (Shell):** `examples/api_examples.sh` - curl examples
- **API Examples (Python):** `examples/api_client_example.py` - Python client
- **Quick Start:** `README.md` sections 3-4

### Phase 9: Deployment (Days 37-40)
- **Deployment Guide:** `README.md` section on deployment
- **Docker Support:** (To be added)
- **Production Checklist:** `KNOWN_ISSUES.md` production section

## 🔍 Search Tips for Claude Code

### Finding Specific Information

**To find interface specifications:**
```
Read INTERFACE_DEFINITIONS.md and show me the [InterfaceName] definition
```

**To understand a component's design:**
```
Read section [X.Y] from 02_High_Level_Design_v5_MODULAR.md
```

**To see today's tasks:**
```
Read PROJECT_IMPLEMENTATION_PLAN.md for Day [N] tasks
```

**To understand requirements:**
```
Read 01_Requirements_Specification_v4_Conversation.md section on [topic]
```

### Common Queries

**"How should the matching engine work?"**
→ Read: `docs/02_High_Level_Design_v5_MODULAR.md` section 3.4.2

**"What methods does ILegalModule require?"**
→ Read: `docs/INTERFACE_DEFINITIONS.md` - ILegalModule section

**"How is the hybrid AI strategy implemented?"**
→ Read: `docs/HYBRID_SUPERIORITY_EXAMPLES.md`

**"What's the logic tree structure?"**
→ Read: `docs/legal-logic-tree-spec__1_.md`

**"What are Order 21 regulations?"**
→ Read: `docs/Rules_of_Court_202113.pdf`

**"How do I use the system?"** ⭐ NEW
→ Read: `USER_GUIDE.md`

**"How do I demo the system?"** ⭐ NEW
→ Read: `DEMO_GUIDE.md`

**"How do I run examples?"** ⭐ NEW
→ Run: `python3 demo/interactive_demo.py` or `python3 examples/api_client_example.py`

## 📝 Notes for Claude Code

### Critical Files (Always Reference)
1. `PROJECT_IMPLEMENTATION_PLAN.md` - What to build
2. `docs/INTERFACE_DEFINITIONS.md` - How to build it
3. `docs/02_High_Level_Design_v5_MODULAR.md` - Architecture
4. `CLAUDE.md` - Current status

### When Starting New Day
1. Read PROJECT_IMPLEMENTATION_PLAN.md for day's tasks
2. Read relevant section in High-Level Design
3. Read interface definitions for components being built
4. Check CLAUDE.md for current status

### When Implementing
1. Always reference the interface definition first
2. Follow the design specification exactly
3. Verify against success criteria in plan
4. Update CLAUDE.md when complete

## 🔄 Keeping Documents Updated

### CLAUDE.md (Updated Frequently)
- Update after each day completion
- Reflects current status
- Lists completed days

### Other Documents (Static)
- Design documents are reference material
- Should not be modified during implementation
- If design changes needed, discuss first

## 📚 Document Versions

All documents in this repository are:
- **Version:** v5.0 (modular architecture)
- **Last Updated:** Varies by document
- **Status:** Official design specifications

For questions about design decisions, reference the appropriate document sections above.

---

**This index is maintained for Claude Code's reference. Keep it updated as documentation evolves.**
