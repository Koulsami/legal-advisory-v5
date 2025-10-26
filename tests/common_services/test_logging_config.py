"""
Test Logging Configuration
Legal Advisory System v5.0

Tests for the logging configuration system.
"""

import pytest
import logging
import io
from backend.common_services.logging_config import (
    setup_logging,
    get_logger,
    log_extraction,
    log_conversation_flow,
    log_ai_call,
    log_validation,
    ColoredFormatter,
)


class TestLoggingConfig:
    """Test logging configuration."""

    def test_setup_logging_info_level(self):
        """Test setting up logging at INFO level."""
        setup_logging(level="INFO")
        logger = get_logger("test")
        assert logger.level == logging.INFO

    def test_setup_logging_debug_level(self):
        """Test setting up logging at DEBUG level."""
        setup_logging(level="DEBUG")
        logger = get_logger("test")
        assert logger.level == logging.DEBUG

    def test_setup_logging_warning_level(self):
        """Test setting up logging at WARNING level."""
        setup_logging(level="WARNING")
        logger = get_logger("test")
        assert logger.level == logging.WARNING

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test_module")
        assert logger.name == "test_module"
        assert isinstance(logger, logging.Logger)

    def test_colored_formatter(self):
        """Test ColoredFormatter formats messages correctly."""
        formatter = ColoredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        assert "Test message" in formatted
        assert "test" in formatted


class TestLoggingHelpers:
    """Test logging helper functions."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a logger with a string stream to capture output
        self.logger = logging.getLogger("test_helpers")
        self.logger.handlers = []  # Clear any existing handlers
        self.stream = io.StringIO()
        handler = logging.StreamHandler(self.stream)
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def test_log_extraction(self):
        """Test log_extraction helper."""
        text = "High Court case for $50,000"
        extracted = {"court_level": "High Court", "claim_amount": 50000.0}

        log_extraction(self.logger, text, extracted)

        output = self.stream.getvalue()
        assert "High Court case" in output
        assert "court_level" in output or "Court" in output

    def test_log_conversation_flow(self):
        """Test log_conversation_flow helper."""
        session_id = "test-session-12345"
        action = "pattern_extraction"
        details = {"extracted": {"amount": 50000}}

        log_conversation_flow(self.logger, session_id, action, details)

        output = self.stream.getvalue()
        assert "test-session" in output  # First 8 chars of session ID
        assert "pattern_extraction" in output

    def test_log_ai_call(self):
        """Test log_ai_call helper."""
        prompt = "What is the court level?"
        response = "High Court"
        tokens = 150

        log_ai_call(self.logger, prompt, response, tokens)

        output = self.stream.getvalue()
        assert "150" in output or "tokens" in output.lower()

    def test_log_validation(self):
        """Test log_validation helper."""
        field = "claim_amount"
        value = 50000.0
        is_valid = True
        reason = "Within acceptable range"

        log_validation(self.logger, field, value, is_valid, reason)

        output = self.stream.getvalue()
        assert "claim_amount" in output
        assert "50000" in output or "valid" in output.lower()

    def test_log_extraction_with_empty_dict(self):
        """Test log_extraction with no extracted fields."""
        text = "some random text"
        extracted = {}

        log_extraction(self.logger, text, extracted)

        output = self.stream.getvalue()
        # Should still log something
        assert len(output) > 0

    def test_log_conversation_flow_without_details(self):
        """Test log_conversation_flow without details."""
        session_id = "test-session"
        action = "session_created"

        log_conversation_flow(self.logger, session_id, action, None)

        output = self.stream.getvalue()
        assert "session_created" in output


class TestLoggingIntegration:
    """Test logging integration scenarios."""

    def test_multiple_loggers_isolated(self):
        """Test that multiple loggers are isolated."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1 is not logger2
        assert logger1.name == "module1"
        assert logger2.name == "module2"

    def test_logging_levels_hierarchy(self):
        """Test that logging level hierarchy works correctly."""
        setup_logging(level="WARNING")
        logger = get_logger("test_hierarchy")

        # Create handler to capture logs
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        logger.addHandler(handler)

        logger.debug("Debug message")  # Should not appear
        logger.info("Info message")  # Should not appear
        logger.warning("Warning message")  # Should appear

        output = stream.getvalue()
        assert "Debug message" not in output
        assert "Info message" not in output
        assert "Warning message" in output

    def test_logger_reuse(self):
        """Test that getting the same logger returns the same instance."""
        logger1 = get_logger("reuse_test")
        logger2 = get_logger("reuse_test")

        assert logger1 is logger2
