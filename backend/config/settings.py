# ... existing imports ...
from typing import List, Optional
from enum import Enum

class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings - ENHANCED"""
    
    # ... existing fields ...
    
    # Add these new fields:
    
    # Debugging
    DEBUG_MODE: bool = True
    DEBUG_SHOW_SQL: bool = False
    DEBUG_SHOW_TREE_MATCHING: bool = False
    DEBUG_SHOW_AI_PROMPTS: bool = False
    
    # Performance
    MAX_WORKERS: int = 4
    REQUEST_TIMEOUT: int = 30
    CACHE_ENABLED: bool = True
    
    # Legal Module Settings
    DEFAULT_MODULE: str = "ORDER_21"
    MODULE_COMPLETENESS_THRESHOLD: float = 0.70
    
    # Matching Settings
    MATCHING_THRESHOLD: float = 0.60
    MAX_MATCHES: int = 5
    
    # AI Settings
    AI_ENABLED: bool = True
    AI_FALLBACK_TO_EMULATOR: bool = True
    AI_RETRY_ATTEMPTS: int = 3
    AI_RETRY_DELAY: float = 1.0
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing"""
        return self.ENVIRONMENT == "testing"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    def enable_debug(self):
        """Enable all debug flags"""
        self.DEBUG_MODE = True
        self.DEBUG_SHOW_SQL = True
        self.DEBUG_SHOW_TREE_MATCHING = True
        self.DEBUG_SHOW_AI_PROMPTS = True
    
    def disable_debug(self):
        """Disable all debug flags"""
        self.DEBUG_MODE = False
        self.DEBUG_SHOW_SQL = False
        self.DEBUG_SHOW_TREE_MATCHING = False
        self.DEBUG_SHOW_AI_PROMPTS = False


# Keep existing get_settings function
