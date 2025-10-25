# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Legal Advisory System v5.0 - A hybrid AI legal advisory system for Singapore's Rules of Court. The system demonstrates measurable superiority over generic AI systems (100% calculation accuracy vs ~60%) through specialized legal calculations combined with AI enhancement.

**Current Status:** Phase 1 Complete (Interfaces & Configuration), Phase 2 In Progress (Debugging & Emulators)

## Architecture

Five-layer modular design implementing a plugin-based microkernel architecture:

1. **User Interface Layer** - React frontend (Netlify)
2. **Conversation Orchestration Layer** - Natural language → Structured data
3. **Hybrid AI Orchestration Layer** - AI Enhancement + Validation
4. **Common Services Layer** - Matching Engine, Analysis, Registry
5. **Legal Modules Layer** - Pluggable modules (Order 21, Order 5, Order 19...)

### Key Architectural Principles

- **Interface-Based Design**: All components implement abstract base classes (ABCs) defined in `backend/interfaces/`
- **Plugin Architecture**: Legal modules are pluggable via `ILegalModule` interface
- **Separation of Concerns**: Clear boundaries between layers
- **Emulator System**: Mock implementations for testing without external dependencies
- **Zero-Overhead Debugging**: Debug framework with toggleable features (enabled in dev, disabled in prod)

## Development Commands

### Testing

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run all tests (integration + unit + emulators)
pytest tests/ -v

# Run with coverage report
pytest tests/integration/ -v --cov=backend --cov-report=html

# Run specific test file
pytest tests/integration/test_interface_compliance.py -v

# Run specific test
pytest tests/integration/test_interface_compliance.py::test_mock_legal_module_implements_interface -v
```

### Package Installation

```bash
# Install in editable mode with dev dependencies
pip install -e .

# Install with dev dependencies from pyproject.toml
pip install -e ".[dev]"

# Reinstall after changes to setup.py or pyproject.toml
pip install -e . --force-reinstall
```

### Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Code Structure

### Core Interfaces (`backend/interfaces/`)

All interfaces are abstract base classes that define contracts:

- `legal_module.py` - `ILegalModule` - Legal module plugin interface
- `ai_service.py` - `IAIService` - AI service provider interface
- `matching.py` - `IMatchingEngine` - Matching strategy interface
- `validation.py` - `IValidator` - Validation service interface
- `tree.py` - `ITreeFramework` - Logic tree management interface
- `analysis.py` - `IAnalysisEngine` - Analysis orchestration interface
- `calculator.py` - `ICalculator` - Cost calculation interface
- `data_structures.py` - Shared data structures (LogicTreeNode, MatchResult, etc.)

### Emulator/Mock System (`backend/emulators/`)

Two types of testing implementations:

1. **Mock Implementations** - Basic implementations for interface compliance testing:
   - `mock_legal_module.py`, `mock_ai_service.py`, etc.
   - Used in `tests/integration/test_interface_compliance.py`

2. **Emulator Implementations** - Advanced implementations with realistic behavior:
   - `ai_emulator.py` - Simulates AI responses with deterministic logic
   - `database_emulator.py` - In-memory database simulation
   - `matching_emulator.py` - Predictable matching results
   - `module_emulator.py` - Minimal legal module tree
   - Used for end-to-end testing without external dependencies

### Configuration System (`backend/config/settings.py`)

Environment-based configuration using Pydantic:

- **Environment Types**: Development, Testing, Staging, Production
- **Debug Levels**: None, Error, Warning, Info, Debug, Trace
- **Feature Toggles**: Emulators, debug tracing, metrics, etc.
- **Global Settings**: Access via `get_settings()` singleton

Example:
```python
from backend.config.settings import get_settings, is_debug_enabled

settings = get_settings()
if is_debug_enabled():
    # Debug code only runs when enabled
    pass
```

### Debugging Framework (`backend/utils/debug.py`)

Zero-overhead debugging system:

- `@trace_function()` - Decorator to log function entry/exit with parameters
- `debug_log()` - Conditional logging based on debug level
- `DebugContext` - Context manager for grouped debug output
- **Critical**: All debug checks verify `settings.debug_enabled` first for zero overhead in production

### Common Services (`backend/common_services/`)

Shared services used across all legal modules:

- `logic_tree_framework.py` - Tree navigation and evaluation (currently implemented)
- Additional services planned: matching engine, analysis engine, etc.

## Development Patterns

### Creating a New Legal Module

1. Implement `ILegalModule` interface from `backend/interfaces/legal_module.py`
2. Define your logic tree structure using `LogicTreeNode`
3. Implement all required methods: `get_tree_nodes()`, `calculate()`, `validate_fields()`, etc.
4. Add module metadata with unique `module_id`
5. Register module with the system (registration system TBD in Phase 3)

### Adding a New Interface

1. Create interface file in `backend/interfaces/`
2. Define abstract base class inheriting from `ABC`
3. Use `@abstractmethod` decorator for required methods
4. Create corresponding mock in `backend/emulators/` for testing
5. Add integration test in `tests/integration/test_interface_compliance.py`

### Writing Tests

- **Integration Tests** (`tests/integration/`): Test interface compliance and component integration
- **Unit Tests** (`tests/unit/`): Test individual components in isolation
- **Emulator Tests** (`tests/emulators/`): Test emulator implementations
- All tests must pass before committing (10/10 currently passing)
- Maintain 96%+ code coverage

### Using Emulators

Toggle emulators in configuration:
```python
settings = get_settings()
settings.use_ai_emulator = True  # Use AI emulator instead of real API
settings.use_database_emulator = True  # Use in-memory database
settings.use_matching_emulator = True  # Use predictable matching
```

## Important Notes

### Interface Compliance

- Every component MUST implement its interface fully
- Use `isinstance(component, Interface)` to verify at runtime
- Mock/emulator implementations must pass all interface compliance tests

### Debug System Usage

- ALWAYS check `is_debug_enabled()` before expensive debug operations
- Use appropriate debug levels: ERROR < WARNING < INFO < DEBUG < TRACE
- Set `debug_enabled=False` in production for zero overhead
- Trace toggles: `trace_function_calls`, `trace_ai_calls`, `trace_matching_engine`, etc.

### Data Structures

All shared data structures are defined in `backend/interfaces/data_structures.py`:
- `LogicTreeNode` - Tree structure for legal logic
- `MatchResult` - Result of matching operations
- `FieldRequirement` - Field validation requirements
- `QuestionTemplate` - Conversation question templates
- `ModuleMetadata` - Module identification and versioning
- And more...

### Git Workflow

Recent commits show clear phase-based development:
- Phase 1: Interfaces, Mocks, Configuration (Complete)
- Phase 2: Debugging & Emulators (In Progress - Days 6-8)
- Future: Common Services, Hybrid AI, Legal Modules, Frontend

### Dependencies

Core dependencies (from `pyproject.toml`):
- Python 3.10+ (using 3.12 currently)
- FastAPI - Web framework
- Uvicorn - ASGI server
- Pydantic - Data validation and settings

Dev dependencies:
- pytest - Testing framework
- pytest-asyncio - Async test support
- pytest-cov - Coverage reporting
- pytest-mock - Mocking support

## Phase Roadmap

| Phase | Days | Status | Focus |
|-------|------|--------|-------|
| Phase 0 | 1-2 | ✅ Complete | Setup |
| Phase 1 | 3-5 | ✅ Complete | Interfaces & Configuration |
| Phase 2 | 6-8 | 🔄 Current | Debugging & Emulators |
| Phase 3 | 9-13 | ⏳ Planned | Common Services |
| Phase 4 | 14-17 | ⏳ Planned | Hybrid AI Layer |
| Phase 5 | 18-23 | ⏳ Planned | Order 21 Module |
| Phase 6 | 24-28 | ⏳ Planned | Conversation Layer |
| Phase 7 | 29-33 | ⏳ Planned | Integration & Testing |
| Phase 8 | 34-36 | ⏳ Planned | Demo & Documentation |
| Phase 9 | 37-40 | ⏳ Planned | Deployment |

## Documentation References

- `README.md` - Project overview and quick start
- `docs/phase1/PHASE1_COMPLETE.md` - Phase 1 completion report
- `docs/phase1/INTERFACE_USAGE_EXAMPLES.md` - Interface usage examples
- Project planning docs available in root directory
