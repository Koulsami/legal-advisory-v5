"""
Test Configuration System
"""

import pytest
from backend.config.settings import get_settings, Settings


def test_settings_load():
    """Test settings can be loaded"""
    settings = get_settings()
    assert settings is not None
    assert isinstance(settings, Settings)


def test_settings_defaults():
    """Test default values"""
    settings = get_settings()
    assert settings.API_PORT == 8765
    assert settings.DEBUG_MODE is True
    assert settings.MATCHING_THRESHOLD == 0.60
    assert settings.MODULE_COMPLETENESS_THRESHOLD == 0.70


def test_settings_properties():
    """Test settings properties"""
    settings = get_settings()
    assert hasattr(settings, 'is_development')
    assert hasattr(settings, 'is_testing')
    assert hasattr(settings, 'is_production')


def test_debug_toggle():
    """Test debug enable/disable"""
    settings = Settings(ENVIRONMENT="development")
    
    settings.enable_debug()
    assert settings.DEBUG_MODE is True
    assert settings.DEBUG_SHOW_SQL is True
    
    settings.disable_debug()
    assert settings.DEBUG_MODE is False
    assert settings.DEBUG_SHOW_SQL is False


def test_settings_singleton():
    """Test settings is singleton"""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
