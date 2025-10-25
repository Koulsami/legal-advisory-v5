"""
Configuration Settings
Legal Advisory System v5.0

Enhanced with debugging capabilities and environment management.
"""

import os
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, Optional


class Environment(str, Enum):
    """Environment types"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings:
    """
    Application Settings

    Loads from environment variables with sensible defaults.
    Supports different environments and debugging capabilities.
    """

    # ============================================
    # INITIALIZATION
    # ============================================

    def __init__(self, **overrides):
        """Initialize settings with optional overrides"""
        # Type cast overrides
        self._overrides = {}
        for key, value in overrides.items():
            if (
                key.endswith("_PORT")
                or key.endswith("_SIZE")
                or key == "MAX_WORKERS"
                or key == "API_WORKERS"
            ):
                self._overrides[key] = int(value) if not isinstance(value, int) else value
            elif key.startswith("DEBUG_") or key in [
                "AI_ENABLED",
                "MODULE_AUTO_LOAD",
                "CACHE_ENABLED",
                "AI_FALLBACK_TO_EMULATOR",
            ]:
                if isinstance(value, bool):
                    self._overrides[key] = value
                else:
                    self._overrides[key] = str(value).lower() in ("true", "1", "yes", "on")
            elif key.endswith("_THRESHOLD") or key.endswith("_DELAY"):
                self._overrides[key] = float(value) if not isinstance(value, float) else value
            else:
                self._overrides[key] = value

    def _get(self, key: str, default: Any = None, type_cast=str) -> Any:
        """Get setting with override support"""
        if key in self._overrides:
            return self._overrides[key]

        value = os.getenv(key, default)

        if value is None:
            return None

        if type_cast == bool:
            return str(value).lower() in ("true", "1", "yes", "on")
        elif type_cast == int:
            return int(value)
        elif type_cast == float:
            return float(value)
        else:
            return value

    # ============================================
    # ENVIRONMENT
    # ============================================

    @property
    def ENVIRONMENT(self) -> str:
        return self._get("ENVIRONMENT", "development")

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == Environment.DEVELOPMENT.value

    @property
    def is_testing(self) -> bool:
        """Check if running in testing"""
        return self.ENVIRONMENT == Environment.TESTING.value

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == Environment.PRODUCTION.value

    # ============================================
    # DEBUG SETTINGS
    # ============================================

    @property
    def DEBUG_MODE(self) -> bool:
        """Master debug switch - disables ALL debugging in production"""
        if self.is_production:
            return False
        return self._get("DEBUG_MODE", True, bool)

    @DEBUG_MODE.setter
    def DEBUG_MODE(self, value: bool):
        """Set debug mode"""
        self._overrides["DEBUG_MODE"] = value

    @property
    def DEBUG_SHOW_SQL(self) -> bool:
        """Show SQL queries"""
        return self.DEBUG_MODE and self._get("DEBUG_SHOW_SQL", False, bool)

    @DEBUG_SHOW_SQL.setter
    def DEBUG_SHOW_SQL(self, value: bool):
        """Set DEBUG_SHOW_SQL"""
        self._overrides["DEBUG_SHOW_SQL"] = value

    @property
    def DEBUG_SHOW_TREE_MATCHING(self) -> bool:
        """Show tree matching process"""
        return self.DEBUG_MODE and self._get("DEBUG_SHOW_TREE_MATCHING", False, bool)

    @DEBUG_SHOW_TREE_MATCHING.setter
    def DEBUG_SHOW_TREE_MATCHING(self, value: bool):
        """Set DEBUG_SHOW_TREE_MATCHING"""
        self._overrides["DEBUG_SHOW_TREE_MATCHING"] = value

    @property
    def DEBUG_SHOW_AI_PROMPTS(self) -> bool:
        """Show AI prompts and responses"""
        return self.DEBUG_MODE and self._get("DEBUG_SHOW_AI_PROMPTS", False, bool)

    @DEBUG_SHOW_AI_PROMPTS.setter
    def DEBUG_SHOW_AI_PROMPTS(self, value: bool):
        """Set DEBUG_SHOW_AI_PROMPTS"""
        self._overrides["DEBUG_SHOW_AI_PROMPTS"] = value

    @property
    def DEBUG_SHOW_VALIDATION(self) -> bool:
        """Show validation process"""
        return self.DEBUG_MODE and self._get("DEBUG_SHOW_VALIDATION", False, bool)

    @DEBUG_SHOW_VALIDATION.setter
    def DEBUG_SHOW_VALIDATION(self, value: bool):
        """Set DEBUG_SHOW_VALIDATION"""
        self._overrides["DEBUG_SHOW_VALIDATION"] = value

    @property
    def debug_enabled(self) -> bool:
        """Check if any debug flag is enabled"""
        return self.DEBUG_MODE

    def enable_debug(self, *flags: str):
        """Enable specific debug flags"""
        if not self.DEBUG_MODE:
            return

        for flag in flags:
            env_var = f"DEBUG_SHOW_{flag.upper()}"
            self._overrides[env_var] = True

    def enable_all_debug(self):
        """Enable all debug flags"""
        self._overrides["DEBUG_MODE"] = True
        self._overrides["DEBUG_SHOW_SQL"] = True
        self._overrides["DEBUG_SHOW_TREE_MATCHING"] = True
        self._overrides["DEBUG_SHOW_AI_PROMPTS"] = True
        self._overrides["DEBUG_SHOW_VALIDATION"] = True

    def disable_debug(self):
        """Disable all debugging (legacy method)"""
        self.disable_all_debug()

    def disable_all_debug(self):
        """Disable all debug flags"""
        self._overrides["DEBUG_MODE"] = False
        self._overrides["DEBUG_SHOW_SQL"] = False
        self._overrides["DEBUG_SHOW_TREE_MATCHING"] = False
        self._overrides["DEBUG_SHOW_AI_PROMPTS"] = False
        self._overrides["DEBUG_SHOW_VALIDATION"] = False

    def get_debug_summary(self) -> dict:
        """Get summary of all debug settings"""
        return {
            "debug_mode": self.DEBUG_MODE,
            "show_sql": self.DEBUG_SHOW_SQL,
            "show_tree_matching": self.DEBUG_SHOW_TREE_MATCHING,
            "show_ai_prompts": self.DEBUG_SHOW_AI_PROMPTS,
            "show_validation": self.DEBUG_SHOW_VALIDATION,
            "any_debug_enabled": self.debug_enabled,
        }

    # ============================================
    # API SETTINGS
    # ============================================

    @property
    def API_HOST(self) -> str:
        return self._get("API_HOST", "0.0.0.0")

    @property
    def API_PORT(self) -> int:
        return self._get("API_PORT", 8765, int)

    @property
    def API_WORKERS(self) -> int:
        return self._get("API_WORKERS", 4, int)

    # ============================================
    # CORS SETTINGS
    # ============================================

    @property
    def CORS_ORIGINS(self) -> str:
        """CORS allowed origins (comma-separated)"""
        return self._get("CORS_ORIGINS", "http://localhost:3000")

    @property
    def cors_origins_list(self) -> list:
        """CORS origins as a list"""
        origins = self.CORS_ORIGINS
        if not origins:
            return []
        return [origin.strip() for origin in origins.split(",")]

    # ============================================
    # LEGAL MODULE SETTINGS
    # ============================================

    @property
    def DEFAULT_MODULE(self) -> str:
        """Default legal module to use"""
        return self._get("DEFAULT_MODULE", "ORDER_21")

    @property
    def MODULE_COMPLETENESS_THRESHOLD(self) -> float:
        """Threshold for considering data collection complete"""
        return self._get("MODULE_COMPLETENESS_THRESHOLD", 0.70, float)

    @property
    def MODULE_AUTO_LOAD(self) -> bool:
        """Auto-load default module on startup"""
        return self._get("MODULE_AUTO_LOAD", True, bool)

    # ============================================
    # MATCHING ENGINE SETTINGS
    # ============================================

    @property
    def MATCHING_THRESHOLD(self) -> float:
        """Minimum confidence for match"""
        return self._get("MATCHING_THRESHOLD", 0.60, float)

    @property
    def MAX_MATCHES(self) -> int:
        """Maximum matches to return"""
        return self._get("MAX_MATCHES", 5, int)

    @property
    def MATCHING_ALGORITHM(self) -> str:
        """Matching algorithm: 'hybrid', 'exact', 'fuzzy'"""
        return self._get("MATCHING_ALGORITHM", "hybrid")

    # ============================================
    # AI SERVICE SETTINGS
    # ============================================

    @property
    def AI_ENABLED(self) -> bool:
        """Enable AI services"""
        return self._get("AI_ENABLED", True, bool)

    @property
    def AI_FALLBACK_TO_EMULATOR(self) -> bool:
        """Fallback to emulator if AI fails"""
        return self._get("AI_FALLBACK_TO_EMULATOR", True, bool)

    @property
    def AI_RETRY_ATTEMPTS(self) -> int:
        """Number of retry attempts for AI calls"""
        return self._get("AI_RETRY_ATTEMPTS", 3, int)

    @property
    def AI_RETRY_DELAY(self) -> float:
        """Delay between retries (seconds)"""
        return self._get("AI_RETRY_DELAY", 1.0, float)

    @property
    def AI_TIMEOUT(self) -> int:
        """AI call timeout (seconds)"""
        return self._get("AI_TIMEOUT", 30, int)

    @property
    def AI_MAX_TOKENS(self) -> int:
        """Maximum tokens for AI response"""
        return self._get("AI_MAX_TOKENS", 4096, int)

    # Anthropic Claude
    @property
    def ANTHROPIC_API_KEY(self) -> Optional[str]:
        return self._get("ANTHROPIC_API_KEY")

    @property
    def ANTHROPIC_MODEL(self) -> str:
        return self._get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    # OpenAI
    @property
    def OPENAI_API_KEY(self) -> Optional[str]:
        return self._get("OPENAI_API_KEY")

    @property
    def OPENAI_MODEL(self) -> str:
        return self._get("OPENAI_MODEL", "gpt-4-turbo-preview")

    # ============================================
    # DATABASE SETTINGS
    # ============================================

    @property
    def DATABASE_URL(self) -> str:
        return self._get("DATABASE_URL", "sqlite:///legal_advisory.db")

    @property
    def DATABASE_POOL_SIZE(self) -> int:
        return self._get("DATABASE_POOL_SIZE", 10, int)

    @property
    def DATABASE_MAX_OVERFLOW(self) -> int:
        return self._get("DATABASE_MAX_OVERFLOW", 20, int)

    # ============================================
    # CACHE SETTINGS
    # ============================================

    @property
    def CACHE_ENABLED(self) -> bool:
        return self._get("CACHE_ENABLED", True, bool)

    @property
    def CACHE_DEFAULT_TTL(self) -> int:
        """Default cache TTL in seconds"""
        return self._get("CACHE_DEFAULT_TTL", 3600, int)

    @property
    def REDIS_URL(self) -> Optional[str]:
        return self._get("REDIS_URL")

    # ============================================
    # PERFORMANCE SETTINGS
    # ============================================

    @property
    def MAX_WORKERS(self) -> int:
        """Max worker threads for async operations"""
        return self._get("MAX_WORKERS", 4, int)

    @property
    def REQUEST_TIMEOUT(self) -> int:
        """Request timeout in seconds"""
        return self._get("REQUEST_TIMEOUT", 30, int)

    @property
    def BATCH_SIZE(self) -> int:
        """Batch size for bulk operations"""
        return self._get("BATCH_SIZE", 100, int)

    # ============================================
    # LOGGING SETTINGS
    # ============================================

    @property
    def LOG_LEVEL(self) -> str:
        if self.is_production:
            return self._get("LOG_LEVEL", "WARNING")
        return self._get("LOG_LEVEL", "INFO")

    @property
    def LOG_FORMAT(self) -> str:
        return "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @property
    def LOG_FILE(self) -> Optional[str]:
        return self._get("LOG_FILE")


@lru_cache()
def get_settings(**overrides) -> Settings:
    """
    Get cached settings instance

    Usage:
        settings = get_settings()
        settings = get_settings(ENVIRONMENT="testing")
    """
    return Settings(**overrides)
