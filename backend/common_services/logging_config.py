"""
Logging Configuration
Legal Advisory System v5.0

Centralized logging configuration for debugging and monitoring.
"""

import logging
import sys
from typing import Optional

# Color codes for terminal output
class LogColors:
    """ANSI color codes for terminal logging."""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    FORMATS = {
        logging.DEBUG: LogColors.CYAN + "%(levelname)s" + LogColors.RESET + " [%(name)s] %(message)s",
        logging.INFO: LogColors.GREEN + "%(levelname)s" + LogColors.RESET + " [%(name)s] %(message)s",
        logging.WARNING: LogColors.YELLOW + "%(levelname)s" + LogColors.RESET + " [%(name)s] %(message)s",
        logging.ERROR: LogColors.RED + "%(levelname)s" + LogColors.RESET + " [%(name)s] %(message)s",
        logging.CRITICAL: LogColors.BOLD + LogColors.RED + "%(levelname)s" + LogColors.RESET + " [%(name)s] %(message)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self._fmt)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


def setup_logging(level: str = "INFO", use_colors: bool = True) -> None:
    """
    Configure logging for the entire application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_colors: Whether to use colored output (disable for log files)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Set formatter
    if use_colors:
        console_handler.setFormatter(ColoredFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = []  # Clear existing handlers
    root_logger.addHandler(console_handler)

    # Set specific levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger
    """
    return logging.getLogger(name)


# Convenience logging functions for structured logging
def log_extraction(logger: logging.Logger, text: str, extracted: dict):
    """Log information extraction results."""
    logger.debug(f"Extraction from: '{text[:50]}...'")
    logger.debug(f"Extracted fields: {extracted}")


def log_conversation_flow(logger: logging.Logger, session_id: str, action: str, details: Optional[dict] = None):
    """Log conversation flow for debugging."""
    msg = f"[{session_id[:8]}] {action}"
    if details:
        msg += f" | {details}"
    logger.info(msg)


def log_calculation(logger: logging.Logger, inputs: dict, result: dict):
    """Log calculation inputs and results."""
    logger.info(f"Calculation inputs: {inputs}")
    logger.info(f"Calculation result: Total={result.get('total_costs')}, Basis={result.get('calculation_basis')}")


def log_ai_interaction(logger: logging.Logger, prompt_type: str, response_summary: str):
    """Log AI interactions."""
    logger.debug(f"AI {prompt_type}: {response_summary[:100]}...")


# Initialize default logging
setup_logging(level="INFO")
