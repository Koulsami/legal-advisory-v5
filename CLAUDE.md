# Legal Advisory System v5.0 - Claude Code Context

## 🎯 Project Overview

This is a **Legal Advisory System v5.0** for Singapore's Rules of Court Order 21 (legal costs). It's a hybrid AI system combining specialized legal calculations with AI enhancement.

**Architecture:** Modular plugin system with 5 layers
- User Interface (React)
- Conversation Orchestration
- Hybrid AI Orchestration  
- Common Services (Logic Tree Framework, Matching Engine, etc.)
- Legal Modules (Order 21, Order 5, etc.)

## 📍 Current Status

### ✅ Completed
- **Days 1-8:** Foundation complete
  - All 8 core interfaces (ABCs) defined
  - Debug framework implemented
  - All 4 emulators working (24/24 tests passing)
  - Configuration system complete

- **Day 9:** Logic Tree Framework ✅
  - LogicTreeFramework class (537 lines)
  - Data structures (LogicTreeNode, MatchResult, etc.)
  - 40 comprehensive tests (100% passing, 91% coverage)

- **Day 10:** Universal Matching Engine ✅
  - UniversalMatchingEngine class (631 lines)
  - 6-dimension scoring (WHAT, WHICH, IF-THEN, MODALITY, GIVEN, WHY)
  - Weighted scoring with configurable weights
  - Confidence calculation and match explanations
  - 35 comprehensive tests (100% passing, 99% coverage)

- **Day 11:** Module Registry ✅
  - ModuleRegistry class (540 lines)
  - Module registration and lifecycle management
  - Module discovery with status and tag filtering
  - Integration with LogicTreeFramework (auto-registration)
  - Health checking for all modules
  - 39 comprehensive tests (100% passing, 90% coverage)

### 🎯 Current Day
**Update this as you progress:**
- Day: 11
- Task: Module Registry
- Status: Complete ✅

## 🏗️ Architecture Principles

### Critical Principles
1. **Pre-built Trees Only:** Logic trees are PRE-BUILT from legal rules during module initialization, NEVER constructed dynamically during conversation
2. **Hybrid AI Approach:** Specialized logic handles calculations (100% accuracy), AI enhances explanations
3. **Test-Driven Development:** 95%+ coverage required for all components
4. **SOLID Principles:** Clean architecture, interface-based design
5. **One Step at a Time:** Implement incrementally, test thoroughly

### The Six Logical Dimensions
Every LogicTreeNode has these universal dimensions:
- **WHAT:** Facts, propositions, conclusions
- **WHICH:** Scope, entities, classifications  
- **IF-THEN:** Conditional logic, implications
- **MODALITY:** Obligations (MUST, MAY, CAN, CANNOT)
- **GIVEN:** Assumptions, premises, context
- **WHY:** Reasoning, rationale, policy

## 📂 Project Structure

```
legal-advisory-v5/
├── backend/
│   ├── interfaces/              # ABCs and data structures
│   │   ├── data_structures.py   # LogicTreeNode, MatchResult, etc.
│   │   ├── legal_module.py      # ILegalModule ABC
│   │   ├── ai_service.py        # IAIService ABC
│   │   ├── matching.py          # IMatchingEngine ABC
│   │   ├── validation.py        # IValidator ABC
│   │   ├── tree.py              # ITreeFramework ABC
│   │   ├── analysis.py          # IAnalysisEngine ABC
│   │   └── calculator.py        # ICalculator ABC
│   ├── common_services/         # Shared services
│   │   ├── logic_tree_framework.py  # ✅ Day 9
│   │   ├── matching_engine.py       # Days 10-11
│   │   ├── module_registry.py       # Day 12
│   │   └── analysis_engine.py       # Day 13
│   ├── emulators/               # Test emulators
│   │   ├── ai_emulator.py
│   │   ├── database_emulator.py
│   │   ├── matching_emulator.py
│   │   └── module_emulator.py
│   ├── config/
│   │   └── settings.py          # Configuration system
│   └── utils/
│       └── debug.py             # Debug framework
├── tests/                       # All test files
│   ├── interfaces/
│   ├── common_services/
│   └── emulators/
└── docs/                        # Documentation
    ├── PROJECT_IMPLEMENTATION_PLAN.md    # 40-day roadmap
    ├── 02_High_Level_Design_v5_MODULAR.md
    ├── INTERFACE_DEFINITIONS.md
    └── legal-logic-tree-spec__1_.md
```

## 🛠️ Development Workflow

### Starting a New Day

1. Read the plan: Check `PROJECT_IMPLEMENTATION_PLAN.md` for today's tasks
2. Review interfaces: Understand which ABCs you'll implement
3. Create implementation: Follow the spec exactly
4. Write tests: 95%+ coverage required
5. Run tests: `pytest tests/ -v --cov`
6. Commit: Use format "Day [N]: [Feature] complete"

### Testing Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=term-missing

# Run specific test file
pytest tests/common_services/test_logic_tree_framework.py -v

# Run tests for specific module
pytest tests/common_services/ -v
```

### Common Tasks

```bash
# Install dependencies
pip install pytest pytest-cov --break-system-packages

# Run quick verification
python3 -c "from backend.common_services.logic_tree_framework import LogicTreeFramework; print('✓ Imports work')"

# Check test coverage
coverage report --include="*/logic_tree_framework.py"
```

## 📋 Key Files to Reference

- **Implementation Plan:** `PROJECT_IMPLEMENTATION_PLAN.md` - 40-day detailed plan
- **Architecture:** `02_High_Level_Design_v5_MODULAR.md` - System architecture
- **Interfaces:** `INTERFACE_DEFINITIONS.md` - All ABC specifications
- **Logic Tree Spec:** `legal-logic-tree-spec__1_.md` - Tree structure details

## 🎨 Code Style Guidelines

### Python Style
- Use type hints for all functions
- Comprehensive docstrings with examples
- Follow PEP 8
- Maximum line length: 88 characters (Black default)
- Use dataclasses for data structures

### Testing Style
- Test file: `test_[module_name].py`
- Test function: `test_[feature]_[scenario]()`
- Use fixtures for common setup
- Clear test names describing what's being tested

### Commit Messages
- Format: "Day [N]: [Feature] complete"
- Examples:
  - "Day 9: Logic Tree Framework complete"
  - "Day 10: Universal Matching Engine complete"
  - "Day 18: Order 21 Module implementation started"

## 🚫 What NOT to Do

1. **Never** construct logic trees dynamically during conversation
2. **Never** skip tests or accept <95% coverage
3. **Never** modify interface definitions without updating all implementations
4. **Never** mix AI enhancement with specialized calculations
5. **Never** commit without running tests

## ✅ What TO Do

1. **Always** read the plan for the current day
2. **Always** implement interfaces before concrete classes
3. **Always** write tests alongside implementation
4. **Always** validate tree structures before registration
5. **Always** document with examples in docstrings

## 🔧 Debugging

### Debug Framework Available
```python
from backend.utils.debug import debug_log, DebugContext

# Enable debugging in config/settings.py
DEBUG_ENABLED = True

# Use debug logging
debug_log("message", level="INFO", category="MATCHING")

# Use debug context
with DebugContext("tree_validation"):
    # Your code here
    pass
```

### Common Issues

**Import Errors:**
```bash
# Fix: Add backend to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/legal-advisory-v5"
```

**Test Failures:**
- Check fixtures are properly defined
- Verify imports are correct
- Ensure test data matches expected structure

## 📊 Success Metrics

- **Test Coverage:** 95%+ required
- **Test Pass Rate:** 100% required
- **Code Quality:** All tests passing, no linting errors
- **Documentation:** All functions have docstrings with examples

## 🎯 Next Steps (Update Daily)

**Today's Goal:**
[Update with current day's objective]

**Tomorrow's Goal:**
[Update with next day's objective]

---

*Last Updated: Day 11 - October 26, 2025*
*Current Status: Module Registry complete, ready for Day 12*
