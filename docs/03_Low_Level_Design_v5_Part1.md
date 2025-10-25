# Low Level Design Document v5.0 - Part 1
## Legal Advisory System - Implementation Bible
### Configuration, Debugging, Tracing & Emulators

---

## ðŸŽ¯ DOCUMENT PURPOSE

This is **PART 1** of the complete Low-Level Design - your implementation bible.

**Part 1 Contains:**
1. System Configuration & Toggles
2. Debugging & Tracing Framework  
3. Emulator Framework
4. Layer 3: Hybrid AI Orchestration
5. Layer 4: Common Services (Framework & Matching)

**Part 2 Will Contain:**
- Layer 5: Legal Modules (Order 21 complete implementation)
- Layer 2: Conversation Orchestration
- Database Schemas & Migrations
- API Endpoints Complete Spec
- Testing Framework
- Deployment Configuration

---

## 1. SYSTEM CONFIGURATION & TOGGLES

### 1.1 Configuration Architecture

**Philosophy:** Zero overhead when debugging disabled. All debug checks happen FIRST before any operations.

**File Structure:**
```
/backend/config/
â”œâ”€â”€ __init__.py
â”œâ”€â”€ settings.py          # Main settings class
â”œâ”€â”€ .env.development     # Dev configuration
â”œâ”€â”€ .env.testing         # Test configuration
â”œâ”€â”€ .env.staging         # Staging configuration
â””â”€â”€ .env.production      # Production configuration
```

### 1.2 Settings Implementation

**File: `/backend/config/settings.py`**

```python
"""
System-wide configuration with toggle-able features.
Environment-specific settings loaded from .env files.

CRITICAL: Debug toggles provide ZERO overhead when disabled.
"""

from pydantic import BaseSettings, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from pathlib import Path

class Environment(str, Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class DebugLevel(str, Enum):
    """Debug verbosity levels"""
    NONE = "none"        # Production - no debug output
    ERROR = "error"      # Log errors only
    WARNING = "warning"  # Log warnings and errors
    INFO = "info"        # Log info, warnings, errors
    DEBUG = "debug"      # Log everything
    TRACE = "trace"      # Log everything + method entry/exit

class Settings(BaseSettings):
    """
    System-wide settings with environment overrides.
    
    Loads from environment variables and .env files.
    Supports different configurations per environment.
    """
    
    # ============================================
    # ENVIRONMENT
    # ============================================
    
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        env="ENVIRONMENT",
        description="Current deployment environment"
    )
    
    project_root: Path = Field(
        default=Path(__file__).parent.parent,
        description="Project root directory"
    )
    
    # ============================================
    # DEBUG & TRACING TOGGLES (CRITICAL)
    # ============================================
    
    debug_enabled: bool = Field(
        default=True,
        env="DEBUG_ENABLED",
        description="Master debug toggle. False = ZERO debug overhead"
    )
    
    debug_level: DebugLevel = Field(
        default=DebugLevel.DEBUG,
        env="DEBUG_LEVEL",
        description="Debug verbosity level"
    )
    
    trace_function_calls: bool = Field(
        default=True,
        env="TRACE_FUNCTION_CALLS",
        description="Log function entry/exit with parameters"
    )
    
    trace_ai_calls: bool = Field(
        default=True,
        env="TRACE_AI_CALLS",
        description="Log all AI service calls with prompts/responses"
    )
    
    trace_database_queries: bool = Field(
        default=False,
        env="TRACE_DATABASE_QUERIES",
        description="Log all database queries (verbose!)"
    )
    
    trace_matching_engine: bool = Field(
        default=True,
        env="TRACE_MATCHING_ENGINE",
        description="Log matching engine operations and scores"
    )
    
    trace_validation: bool = Field(
        default=True,
        env="TRACE_VALIDATION",
        description="Log validation checks and failures"
    )
    
    trace_conversation_flow: bool = Field(
        default=True,
        env="TRACE_CONVERSATION_FLOW",
        description="Log conversation state transitions"
    )
    
    log_to_file: bool = Field(
        default=True,
        env="LOG_TO_FILE",
        description="Write logs to files"
    )
    
    log_to_console: bool = Field(
        default=True,
        env="LOG_TO_CONSOLE",
        description="Output logs to console/stdout"
    )
    
    log_file_path: str = Field(
        default="logs/legal_advisory.log",
        env="LOG_FILE_PATH",
        description="Path to log file"
    )
    
    log_rotation_size_mb: int = Field(
        default=10,
        env="LOG_ROTATION_SIZE_MB",
        description="Rotate log files at this size"
    )
    
    log_retention_days: int = Field(
        default=30,
        env="LOG_RETENTION_DAYS",
        description="Keep log files for this many days"
    )
    
    # ============================================
    # EMULATOR TOGGLES
    # ============================================
    
    use_ai_emulator: bool = Field(
        default=False,
        env="USE_AI_EMULATOR",
        description="Use AI emulator instead of real API (saves cost)"
    )
    
    use_database_emulator: bool = Field(
        default=False,
        env="USE_DATABASE_EMULATOR",
        description="Use in-memory database emulator"
    )
    
    use_matching_emulator: bool = Field(
        default=False,
        env="USE_MATCHING_EMULATOR",
        description="Use matching emulator (predictable results)"
    )
    
    use_module_emulator: bool = Field(
        default=False,
        env="USE_MODULE_EMULATOR",
        description="Use module emulator (no real calculations)"
    )
    
    emulator_latency_ms: int = Field(
        default=100,
        env="EMULATOR_LATENCY_MS",
        description="Simulated latency for emulators (milliseconds)"
    )
    
    emulator_enable_randomness: bool = Field(
        default=False,
        env="EMULATOR_ENABLE_RANDOMNESS",
        description="Add random variations to emulator responses"
    )
    
    # ============================================
    # API CONFIGURATION
    # ============================================
    
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8765, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    api_workers: int = Field(default=1, env="API_WORKERS")
    
    api_cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3456"],
        env="API_CORS_ORIGINS"
    )
    
    api_request_timeout_seconds: int = Field(
        default=60,
        env="API_REQUEST_TIMEOUT_SECONDS"
    )
    
    api_max_request_size_mb: int = Field(
        default=10,
        env="API_MAX_REQUEST_SIZE_MB"
    )
    
    # ============================================
    # DATABASE CONFIGURATION
    # ============================================
    
    database_url: str = Field(
        default="postgresql://user:pass@localhost:5432/legal_advisory",
        env="DATABASE_URL"
    )
    
    database_pool_size: int = Field(
        default=5,
        env="DATABASE_POOL_SIZE"
    )
    
    database_max_overflow: int = Field(
        default=10,
        env="DATABASE_MAX_OVERFLOW"
    )
    
    database_pool_timeout_seconds: int = Field(
        default=30,
        env="DATABASE_POOL_TIMEOUT_SECONDS"
    )
    
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    redis_max_connections: int = Field(
        default=10,
        env="REDIS_MAX_CONNECTIONS"
    )
    
    neo4j_url: Optional[str] = Field(
        default=None,
        env="NEO4J_URL",
        description="Optional Neo4j for graph relationships"
    )
    
    # ============================================
    # AI SERVICE CONFIGURATION
    # ============================================
    
    anthropic_api_key: Optional[str] = Field(
        default=None,
        env="ANTHROPIC_API_KEY"
    )
    
    openai_api_key: Optional[str] = Field(
        default=None,
        env="OPENAI_API_KEY"
    )
    
    ai_provider: str = Field(
        default="anthropic",
        env="AI_PROVIDER",
        description="Primary AI provider: anthropic, openai"
    )
    
    ai_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        env="AI_MODEL"
    )
    
    ai_temperature: float = Field(
        default=0.7,
        env="AI_TEMPERATURE",
        description="Temperature for AI generation (0.0-1.0)"
    )
    
    ai_max_tokens: int = Field(
        default=1000,
        env="AI_MAX_TOKENS",
        description="Maximum tokens per AI request"
    )
    
    ai_timeout_seconds: int = Field(
        default=30,
        env="AI_TIMEOUT_SECONDS"
    )
    
    ai_max_retries: int = Field(
        default=3,
        env="AI_MAX_RETRIES"
    )
    
    ai_cache_enabled: bool = Field(
        default=True,
        env="AI_CACHE_ENABLED"
    )
    
    ai_cache_ttl_seconds: int = Field(
        default=3600,
        env="AI_CACHE_TTL_SECONDS",
        description="How long to cache AI responses (1 hour default)"
    )
    
    ai_cost_tracking_enabled: bool = Field(
        default=True,
        env="AI_COST_TRACKING_ENABLED"
    )
    
    # ============================================
    # MATCHING ENGINE CONFIGURATION
    # ============================================
    
    matching_threshold: float = Field(
        default=0.60,
        env="MATCHING_THRESHOLD",
        description="Minimum confidence for node matching (0.0-1.0)"
    )
    
    dimension_weights: Dict[str, float] = Field(
        default={
            "what": 0.25,
            "which": 0.20,
            "if_then": 0.25,
            "modality": 0.15,
            "given": 0.10,
            "why": 0.05
        },
        description="Weights for 6-dimension matching"
    )
    
    matching_algorithm: str = Field(
        default="weighted",
        env="MATCHING_ALGORITHM",
        description="Algorithm: weighted, fuzzy, ml"
    )
    
    # ============================================
    # COMPLETENESS THRESHOLDS
    # ============================================
    
    completeness_threshold_analyze: float = Field(
        default=0.70,
        env="COMPLETENESS_THRESHOLD_ANALYZE",
        description="Completeness required to start analysis (0.0-1.0)"
    )
    
    completeness_threshold_suggest: float = Field(
        default=0.50,
        env="COMPLETENESS_THRESHOLD_SUGGEST",
        description="Start suggesting next steps at this completeness"
    )
    
    # ============================================
    # PERFORMANCE & CACHING
    # ============================================
    
    enable_caching: bool = Field(
        default=True,
        env="ENABLE_CACHING"
    )
    
    cache_ttl_seconds: int = Field(
        default=900,
        env="CACHE_TTL_SECONDS",
        description="Default cache TTL (15 minutes)"
    )
    
    max_workers: int = Field(
        default=4,
        env="MAX_WORKERS",
        description="Number of worker threads"
    )
    
    enable_async: bool = Field(
        default=True,
        env="ENABLE_ASYNC",
        description="Enable async operations"
    )
    
    # ============================================
    # SESSION CONFIGURATION
    # ============================================
    
    session_timeout_minutes: int = Field(
        default=30,
        env="SESSION_TIMEOUT_MINUTES"
    )
    
    session_max_history_size: int = Field(
        default=100,
        env="SESSION_MAX_HISTORY_SIZE",
        description="Maximum conversation turns to keep in memory"
    )
    
    session_persistence_enabled: bool = Field(
        default=True,
        env="SESSION_PERSISTENCE_ENABLED"
    )
    
    # ============================================
    # SECURITY
    # ============================================
    
    secret_key: str = Field(
        default="development-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    
    enable_rate_limiting: bool = Field(
        default=True,
        env="ENABLE_RATE_LIMITING"
    )
    
    rate_limit_per_minute: int = Field(
        default=60,
        env="RATE_LIMIT_PER_MINUTE"
    )
    
    enable_authentication: bool = Field(
        default=False,
        env="ENABLE_AUTHENTICATION",
        description="Enable user authentication"
    )
    
    # ============================================
    # MONITORING & METRICS
    # ============================================
    
    enable_metrics: bool = Field(
        default=True,
        env="ENABLE_METRICS"
    )
    
    metrics_export_interval_seconds: int = Field(
        default=60,
        env="METRICS_EXPORT_INTERVAL_SECONDS"
    )
    
    enable_health_checks: bool = Field(
        default=True,
        env="ENABLE_HEALTH_CHECKS"
    )
    
    health_check_interval_seconds: int = Field(
        default=30,
        env="HEALTH_CHECK_INTERVAL_SECONDS"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# ============================================
# GLOBAL SETTINGS INSTANCE
# ============================================

_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """
    Get global settings instance (singleton pattern).
    
    Returns cached instance after first call for performance.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def reload_settings():
    """Force reload settings from environment"""
    global _settings
    _settings = None
    return get_settings()

# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def is_debug_enabled() -> bool:
    """
    Quick check if ANY debugging is enabled.
    
    This is the FIRST check in all debug decorators.
    Returns False in production for zero overhead.
    """
    settings = get_settings()
    return settings.debug_enabled and settings.debug_level != DebugLevel.NONE

def is_production() -> bool:
    """Check if running in production environment"""
    return get_settings().environment == Environment.PRODUCTION

def is_development() -> bool:
    """Check if running in development environment"""
    return get_settings().environment == Environment.DEVELOPMENT

def is_testing() -> bool:
    """Check if running in testing environment"""
    return get_settings().environment == Environment.TESTING

def get_log_level() -> str:
    """Get appropriate Python logging level"""
    settings = get_settings()
    level_map = {
        DebugLevel.NONE: "CRITICAL",
        DebugLevel.ERROR: "ERROR",
        DebugLevel.WARNING: "WARNING",
        DebugLevel.INFO: "INFO",
        DebugLevel.DEBUG: "DEBUG",
        DebugLevel.TRACE: "DEBUG"
    }
    return level_map.get(settings.debug_level, "INFO")
```

### 1.3 Environment Configuration Files

**File: `/.env.development`**
```bash
# ===========================================
# DEVELOPMENT ENVIRONMENT CONFIGURATION
# ===========================================

ENVIRONMENT=development

# ===========================================
# DEBUG & TRACING (ALL ENABLED)
# ===========================================
DEBUG_ENABLED=true
DEBUG_LEVEL=trace
TRACE_FUNCTION_CALLS=true
TRACE_AI_CALLS=true
TRACE_DATABASE_QUERIES=true
TRACE_MATCHING_ENGINE=true
TRACE_VALIDATION=true
TRACE_CONVERSATION_FLOW=true

LOG_TO_FILE=true
LOG_TO_CONSOLE=true
LOG_FILE_PATH=logs/legal_advisory_dev.log

# ===========================================
# EMULATORS (ENABLED to save costs)
# ===========================================
USE_AI_EMULATOR=true
USE_DATABASE_EMULATOR=false
USE_MATCHING_EMULATOR=false
USE_MODULE_EMULATOR=false
EMULATOR_LATENCY_MS=50

# ===========================================
# API
# ===========================================
API_HOST=0.0.0.0
API_PORT=8765
API_RELOAD=true
API_WORKERS=1

# ===========================================
# DATABASE
# ===========================================
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/legal_advisory_dev
REDIS_URL=redis://localhost:6379/0
# NEO4J_URL=bolt://localhost:7687

# ===========================================
# AI SERVICES (emulator mode, keys optional)
# ===========================================
ANTHROPIC_API_KEY=your_key_here
AI_PROVIDER=anthropic
AI_MODEL=claude-3-5-sonnet-20241022
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=1000
AI_CACHE_ENABLED=true

# ===========================================
# MATCHING ENGINE
# ===========================================
MATCHING_THRESHOLD=0.60
COMPLETENESS_THRESHOLD_ANALYZE=0.70

# ===========================================
# PERFORMANCE
# ===========================================
ENABLE_CACHING=true
CACHE_TTL_SECONDS=900
MAX_WORKERS=4

# ===========================================
# SECURITY (dev mode)
# ===========================================
SECRET_KEY=dev-secret-key-not-for-production
ENABLE_RATE_LIMITING=false
ENABLE_AUTHENTICATION=false
```

**File: `/.env.production`**
```bash
# ===========================================
# PRODUCTION ENVIRONMENT CONFIGURATION
# ===========================================

ENVIRONMENT=production

# ===========================================
# DEBUG & TRACING (ALL DISABLED for zero overhead)
# ===========================================
DEBUG_ENABLED=false
DEBUG_LEVEL=none
TRACE_FUNCTION_CALLS=false
TRACE_AI_CALLS=false
TRACE_DATABASE_QUERIES=false
TRACE_MATCHING_ENGINE=false
TRACE_VALIDATION=false
TRACE_CONVERSATION_FLOW=false

LOG_TO_FILE=true
LOG_TO_CONSOLE=false
LOG_FILE_PATH=/var/log/legal_advisory/app.log
LOG_ROTATION_SIZE_MB=50
LOG_RETENTION_DAYS=90

# ===========================================
# EMULATORS (ALL DISABLED - use real services)
# ===========================================
USE_AI_EMULATOR=false
USE_DATABASE_EMULATOR=false
USE_MATCHING_EMULATOR=false
USE_MODULE_EMULATOR=false

# ===========================================
# API
# ===========================================
API_HOST=0.0.0.0
API_PORT=8765
API_RELOAD=false
API_WORKERS=4

# ===========================================
# DATABASE (production URLs from secrets)
# ===========================================
DATABASE_URL=${DATABASE_URL}
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

REDIS_URL=${REDIS_URL}
REDIS_MAX_CONNECTIONS=50

NEO4J_URL=${NEO4J_URL}

# ===========================================
# AI SERVICES (real API keys from secrets)
# ===========================================
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
AI_PROVIDER=anthropic
AI_MODEL=claude-3-5-sonnet-20241022
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=1000
AI_TIMEOUT_SECONDS=30
AI_MAX_RETRIES=3
AI_CACHE_ENABLED=true
AI_CACHE_TTL_SECONDS=3600

# ===========================================
# MATCHING ENGINE
# ===========================================
MATCHING_THRESHOLD=0.60
MATCHING_ALGORITHM=weighted
COMPLETENESS_THRESHOLD_ANALYZE=0.70

# ===========================================
# PERFORMANCE
# ===========================================
ENABLE_CACHING=true
CACHE_TTL_SECONDS=900
MAX_WORKERS=8
ENABLE_ASYNC=true

# ===========================================
# SECURITY
# ===========================================
SECRET_KEY=${SECRET_KEY}
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=60
ENABLE_AUTHENTICATION=true

# ===========================================
# MONITORING
# ===========================================
ENABLE_METRICS=true
METRICS_EXPORT_INTERVAL_SECONDS=60
ENABLE_HEALTH_CHECKS=true
HEALTH_CHECK_INTERVAL_SECONDS=30
```

**File: `/.env.testing`**
```bash
# ===========================================
# TESTING ENVIRONMENT CONFIGURATION
# ===========================================

ENVIRONMENT=testing

# ===========================================
# DEBUG & TRACING (INFO level for test output)
# ===========================================
DEBUG_ENABLED=true
DEBUG_LEVEL=info
TRACE_FUNCTION_CALLS=false
TRACE_AI_CALLS=true
TRACE_DATABASE_QUERIES=false
TRACE_MATCHING_ENGINE=false
TRACE_VALIDATION=true
TRACE_CONVERSATION_FLOW=false

LOG_TO_FILE=true
LOG_TO_CONSOLE=true
LOG_FILE_PATH=logs/tests.log

# ===========================================
# EMULATORS (ALL ENABLED for fast, isolated tests)
# ===========================================
USE_AI_EMULATOR=true
USE_DATABASE_EMULATOR=true
USE_MATCHING_EMULATOR=false
USE_MODULE_EMULATOR=false
EMULATOR_LATENCY_MS=10

# ===========================================
# API
# ===========================================
API_PORT=8766
API_RELOAD=false
API_WORKERS=1

# ===========================================
# DATABASE (test database)
# ===========================================
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/legal_advisory_test
REDIS_URL=redis://localhost:6379/1

# ===========================================
# AI (emulated)
# ===========================================
AI_PROVIDER=emulator
AI_CACHE_ENABLED=false

# ===========================================
# PERFORMANCE (test optimized)
# ===========================================
ENABLE_CACHING=false
MAX_WORKERS=2

# ===========================================
# SECURITY (test mode)
# ===========================================
SECRET_KEY=test-secret-key
ENABLE_RATE_LIMITING=false
ENABLE_AUTHENTICATION=false
```

---

*Due to message length, this is Part 1. The complete document continues with:*

- **Part 2**: Debugging Framework, Emulators, Hybrid AI Layer
- **Part 3**: Common Services (Matching Engine, Analysis Engine)
- **Part 4**: Legal Modules (Order 21 complete)
- **Part 5**: Database Schemas, API Endpoints, Testing, Deployment

**Shall I continue with Part 2?**
