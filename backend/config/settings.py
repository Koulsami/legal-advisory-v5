"""
System-wide configuration with toggle-able features.
Environment-specific settings loaded from .env files.

CRITICAL: Debug toggles provide ZERO overhead when disabled.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
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
        description="Current deployment environment"
    )
    
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent,
        description="Project root directory"
    )
    
    # ============================================
    # DEBUG & TRACING TOGGLES (CRITICAL)
    # ============================================
    
    debug_enabled: bool = Field(
        default=True,
        description="Master debug toggle. False = ZERO debug overhead"
    )
    
    debug_level: DebugLevel = Field(
        default=DebugLevel.DEBUG,
        description="Debug verbosity level"
    )
    
    trace_function_calls: bool = Field(
        default=True,
        description="Log function entry/exit with parameters"
    )
    
    trace_ai_calls: bool = Field(
        default=True,
        description="Log all AI service calls with prompts/responses"
    )
    
    trace_database_queries: bool = Field(
        default=False,
        description="Log all database queries (verbose!)"
    )
    
    trace_matching_engine: bool = Field(
        default=True,
        description="Log matching engine operations"
    )
    
    trace_validation: bool = Field(
        default=True,
        description="Log validation operations"
    )
    
    trace_conversation_flow: bool = Field(
        default=True,
        description="Log conversation flow steps"
    )
    
    # ============================================
    # LOGGING CONFIGURATION
    # ============================================
    
    log_to_console: bool = Field(
        default=True,
        description="Output logs to console"
    )
    
    log_to_file: bool = Field(
        default=True,
        description="Output logs to file"
    )
    
    log_file_path: str = Field(
        default="logs/legal_advisory.log",
        description="Path to log file"
    )
    
    log_rotation_size_mb: int = Field(
        default=10,
        description="Log file rotation size in MB"
    )
    
    log_retention_days: int = Field(
        default=7,
        description="Number of days to retain log files"
    )
    
    # ============================================
    # EMULATOR TOGGLES
    # ============================================
    
    use_ai_emulator: bool = Field(
        default=False,
        description="Use AI emulator instead of real API (saves costs)"
    )
    
    use_database_emulator: bool = Field(
        default=False,
        description="Use in-memory database emulator"
    )
    
    use_matching_emulator: bool = Field(
        default=False,
        description="Use matching emulator with predictable results"
    )
    
    use_module_emulator: bool = Field(
        default=False,
        description="Use module emulator with minimal tree"
    )
    
    emulator_latency_ms: int = Field(
        default=50,
        description="Simulated latency for emulators (milliseconds)"
    )
    
    # ============================================
    # AI SERVICE CONFIGURATION
    # ============================================
    
    claude_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic Claude API key"
    )
    
    claude_model: str = Field(
        default="claude-3-sonnet-20240229",
        description="Claude model to use"
    )
    
    claude_max_tokens: int = Field(
        default=4096,
        description="Maximum tokens for Claude responses"
    )
    
    claude_temperature: float = Field(
        default=0.7,
        description="Claude temperature (0-1)"
    )
    
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    
    openai_model: str = Field(
        default="gpt-4",
        description="OpenAI model to use"
    )
    
    ai_timeout_seconds: int = Field(
        default=30,
        description="Timeout for AI API calls"
    )
    
    ai_max_retries: int = Field(
        default=3,
        description="Maximum retries for failed AI calls"
    )
    
    # ============================================
    # DATABASE CONFIGURATION
    # ============================================
    
    database_url: str = Field(
        default="postgresql://localhost:5432/legal_advisory",
        description="Database connection URL"
    )
    
    database_pool_size: int = Field(
        default=5,
        description="Database connection pool size"
    )
    
    database_max_overflow: int = Field(
        default=10,
        description="Maximum database connection overflow"
    )
    
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching"
    )
    
    cache_ttl_seconds: int = Field(
        default=3600,
        description="Default cache TTL in seconds"
    )
    
    # ============================================
    # API CONFIGURATION
    # ============================================
    
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host"
    )
    
    api_port: int = Field(
        default=8000,
        description="API server port"
    )
    
    api_workers: int = Field(
        default=4,
        description="Number of API workers"
    )
    
    cors_origins: list = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    
    api_prefix: str = Field(
        default="/api/v1",
        description="API route prefix"
    )
    
    # ============================================
    # MATCHING ENGINE CONFIGURATION
    # ============================================
    
    matching_threshold: float = Field(
        default=0.6,
        description="Minimum confidence threshold for matches (0-1)"
    )
    
    matching_max_results: int = Field(
        default=5,
        description="Maximum number of match results to return"
    )
    
    matching_dimension_weights: dict = Field(
        default={
            "WHAT": 0.25,
            "WHICH": 0.20,
            "IF_THEN": 0.20,
            "MODALITY": 0.15,
            "GIVEN": 0.10,
            "WHY": 0.10
        },
        description="Weights for each matching dimension"
    )
    
    # ============================================
    # ANALYSIS ENGINE CONFIGURATION
    # ============================================
    
    analysis_timeout_seconds: int = Field(
        default=60,
        description="Timeout for complete analysis"
    )
    
    analysis_max_iterations: int = Field(
        default=10,
        description="Maximum analysis iterations"
    )
    
    analysis_min_confidence: float = Field(
        default=0.7,
        description="Minimum confidence for analysis results"
    )
    
    # ============================================
    # CONVERSATION CONFIGURATION
    # ============================================
    
    conversation_max_turns: int = Field(
        default=50,
        description="Maximum turns in a conversation"
    )
    
    session_timeout_minutes: int = Field(
        default=30,
        description="Session timeout in minutes"
    )
    
    session_max_history_size: int = Field(
        default=100,
        description="Maximum conversation turns to keep in memory"
    )
    
    session_persistence_enabled: bool = Field(
        default=True,
        description="Enable session persistence to database"
    )
    
    # ============================================
    # SECURITY
    # ============================================
    
    secret_key: str = Field(
        default="development-secret-key-change-in-production",
        description="Secret key for sessions/tokens"
    )
    
    enable_rate_limiting: bool = Field(
        default=True,
        description="Enable API rate limiting"
    )
    
    rate_limit_per_minute: int = Field(
        default=60,
        description="Requests per minute per IP"
    )
    
    enable_authentication: bool = Field(
        default=False,
        description="Enable user authentication"
    )
    
    # ============================================
    # MONITORING & METRICS
    # ============================================
    
    enable_metrics: bool = Field(
        default=True,
        description="Enable metrics collection"
    )
    
    metrics_export_interval_seconds: int = Field(
        default=60,
        description="Metrics export interval"
    )
    
    enable_health_checks: bool = Field(
        default=True,
        description="Enable health check endpoints"
    )
    
    health_check_interval_seconds: int = Field(
        default=30,
        description="Health check interval"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


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
