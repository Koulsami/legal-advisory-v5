"""
Utility modules for the Legal Advisory System.

This package contains debugging, tracing, and performance monitoring utilities.
"""

from backend.utils.debug import (
    debug_log,
    DebugContext,
    trace_function,
    trace_ai_call,
    trace_matching,
    trace_validation,
    PerformanceTimer,
)

__all__ = [
    'debug_log',
    'DebugContext',
    'trace_function',
    'trace_ai_call',
    'trace_matching',
    'trace_validation',
    'PerformanceTimer',
]
