"""
Test Configuration System
Phase 1 Day 4 - Configuration Tests
"""

import pytest
from backend.config.settings import Settings, get_settings


def test_settings_load():
    """Test settings can be loaded"""
    settings = get_settings()
    assert settings is not None
    assert isinstance(settings, Settings)


def test_settings_defaults():
    """Test default values"""
    settings = get_settings()
    
    # Basic defaults
    assert settings.API_PORT == 8765
    assert settings.ENVIRONMENT == "development"
    
    # Debug defaults
    assert settings.DEBUG_MODE is True
    
    # Module defaults
    assert settings.DEFAULT_MODULE == "ORDER_21"
    assert settings.MODULE_COMPLETENESS_THRESHOLD == 0.70
    
    # Matching defaults
    assert settings.MATCHING_THRESHOLD == 0.60
    assert settings.MAX_MATCHES == 5
    
    # AI defaults
    assert settings.AI_ENABLED is True
    assert settings.AI_FALLBACK_TO_EMULATOR is True


def test_environment_properties():
    """Test environment detection properties"""
    # Test development
    settings = Settings(ENVIRONMENT="development")
    assert settings.is_development is True
    assert settings.is_testing is False
    assert settings.is_production is False
    
    # Test testing
    settings = Settings(ENVIRONMENT="testing")
    assert settings.is_development is False
    assert settings.is_testing is True
    assert settings.is_production is False
    
    # Test production
    settings = Settings(ENVIRONMENT="production")
    assert settings.is_development is False
    assert settings.is_testing is False
    assert settings.is_production is True


def test_debug_enabled_property():
    """Test debug_enabled property"""
    settings = Settings()
    
    # All debug off
    settings.DEBUG_MODE = False
    settings.DEBUG_SHOW_SQL = False
    settings.DEBUG_SHOW_TREE_MATCHING = False
    settings.DEBUG_SHOW_AI_PROMPTS = False
    settings.DEBUG_SHOW_VALIDATION = False
    assert settings.debug_enabled is False
    
    # One debug on
    settings.DEBUG_MODE = True
    assert settings.debug_enabled is True


def test_enable_all_debug():
    """Test enable_all_debug method"""
    settings = Settings()
    
    # Start with all off
    settings.disable_all_debug()
    assert settings.debug_enabled is False
    
    # Enable all
    settings.enable_all_debug()
    assert settings.DEBUG_MODE is True
    assert settings.DEBUG_SHOW_SQL is True
    assert settings.DEBUG_SHOW_TREE_MATCHING is True
    assert settings.DEBUG_SHOW_AI_PROMPTS is True
    assert settings.DEBUG_SHOW_VALIDATION is True
    assert settings.debug_enabled is True


def test_disable_all_debug():
    """Test disable_all_debug method"""
    settings = Settings()
    
    # Start with all on
    settings.enable_all_debug()
    assert settings.debug_enabled is True
    
    # Disable all
    settings.disable_all_debug()
    assert settings.DEBUG_MODE is False
    assert settings.DEBUG_SHOW_SQL is False
    assert settings.DEBUG_SHOW_TREE_MATCHING is False
    assert settings.DEBUG_SHOW_AI_PROMPTS is False
    assert settings.DEBUG_SHOW_VALIDATION is False
    assert settings.debug_enabled is False


def test_get_debug_summary():
    """Test get_debug_summary method"""
    settings = Settings()
    
    settings.enable_all_debug()
    summary = settings.get_debug_summary()
    
    assert isinstance(summary, dict)
    assert "debug_mode" in summary
    assert "show_sql" in summary
    assert "show_tree_matching" in summary
    assert "show_ai_prompts" in summary
    assert "show_validation" in summary
    assert "any_debug_enabled" in summary
    assert summary["any_debug_enabled"] is True


def test_cors_origins_list():
    """Test CORS origins list property"""
    settings = Settings(CORS_ORIGINS="http://localhost:3000,http://localhost:5173")
    
    origins = settings.cors_origins_list
    assert isinstance(origins, list)
    assert len(origins) == 2
    assert "http://localhost:3000" in origins
    assert "http://localhost:5173" in origins


def test_settings_singleton():
    """Test settings is singleton (cached)"""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_custom_settings_values():
    """Test creating settings with custom values"""
    settings = Settings(
        ENVIRONMENT="testing",
        DEBUG_MODE=False,
        MATCHING_THRESHOLD=0.75,
        MAX_MATCHES=10
    )
    
    assert settings.ENVIRONMENT == "testing"
    assert settings.DEBUG_MODE is False
    assert settings.MATCHING_THRESHOLD == 0.75
    assert settings.MAX_MATCHES == 10


def test_module_settings():
    """Test module-specific settings"""
    settings = Settings()
    
    assert settings.DEFAULT_MODULE == "ORDER_21"
    assert 0.0 <= settings.MODULE_COMPLETENESS_THRESHOLD <= 1.0
    assert settings.MODULE_AUTO_LOAD is True


def test_matching_settings():
    """Test matching engine settings"""
    settings = Settings()
    
    assert 0.0 <= settings.MATCHING_THRESHOLD <= 1.0
    assert settings.MAX_MATCHES > 0
    assert settings.MATCHING_ALGORITHM in ["hybrid", "exact", "fuzzy"]


def test_ai_settings():
    """Test AI service settings"""
    settings = Settings()
    
    assert settings.AI_ENABLED is True
    assert settings.AI_RETRY_ATTEMPTS > 0
    assert settings.AI_RETRY_DELAY > 0
    assert settings.AI_TIMEOUT > 0
    assert settings.AI_MAX_TOKENS > 0


def test_performance_settings():
    """Test performance settings"""
    settings = Settings()
    
    assert settings.MAX_WORKERS > 0
    assert settings.REQUEST_TIMEOUT > 0
    assert settings.CACHE_DEFAULT_TTL > 0
