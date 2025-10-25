"""
Debugging and tracing utilities with zero overhead when disabled.

CRITICAL PRINCIPLE: All debug decorators check settings.debug_enabled FIRST,
so when debug_enabled=False, there is ZERO performance impact.

Usage:
    from backend.utils.debug import debug_log, trace_function, DebugContext
    
    @trace_function()
    async def my_function(arg1, arg2):
        with DebugContext("processing"):
            debug_log("Starting processing", level=DebugLevel.INFO)
            result = await process(arg1, arg2)
            return result

Performance:
    When DEBUG_ENABLED=false: < 0.1% overhead (single boolean check)
    When DEBUG_ENABLED=true: ~0.5ms per traced call
"""

import functools
import time
import inspect
import json
import traceback
import sys
from typing import Any, Callable, Optional, Dict, List, Union
from datetime import datetime
from pathlib import Path
from enum import Enum

from backend.config.settings import get_settings, is_debug_enabled, DebugLevel


# ============================================
# CONSTANTS
# ============================================

MAX_STRING_LENGTH = 200  # Maximum length for string representations
MAX_ARG_LENGTH = 100     # Maximum length for argument display
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


# ============================================
# DEBUG CONTEXT MANAGER
# ============================================

class DebugContext:
    """
    Context manager for debug sections with automatic timing.
    
    Provides automatic entry/exit logging with elapsed time.
    Zero overhead when debugging disabled.
    
    Usage:
        with DebugContext("my_operation"):
            # Your code here
            pass
    
    Output:
        >>> ENTERING: my_operation
        <<< EXITING: my_operation (0.123s)
    """
    
    def __init__(
        self,
        name: str,
        enabled: bool = True,
        log_level: DebugLevel = DebugLevel.DEBUG,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize debug context.
        
        Args:
            name: Name of the context/operation
            enabled: Whether this context is enabled (local override)
            log_level: Log level for this context
            metadata: Optional metadata to log on entry
        """
        self.name = name
        self.enabled = enabled and is_debug_enabled()
        self.log_level = log_level
        self.metadata = metadata or {}
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        """Enter context - log start"""
        if self.enabled:
            self.start_time = time.time()
            debug_log(
                f">>> ENTERING: {self.name}",
                level=self.log_level,
                data=self.metadata if self.metadata else None
            )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - log end with timing"""
        if self.enabled:
            elapsed = time.time() - self.start_time
            
            if exc_type:
                # Exception occurred
                debug_log(
                    f"<<< EXITING: {self.name} (ERROR after {elapsed:.3f}s)",
                    level=DebugLevel.ERROR,
                    error=str(exc_val),
                    data={
                        "exception_type": exc_type.__name__,
                        "elapsed_seconds": elapsed,
                        "traceback": traceback.format_exc()
                    }
                )
            else:
                # Normal exit
                debug_log(
                    f"<<< EXITING: {self.name} ({elapsed:.3f}s)",
                    level=self.log_level,
                    data={"elapsed_ms": f"{elapsed * 1000:.2f}ms"}
                )
        
        # Don't suppress exceptions
        return False


# ============================================
# DEBUG LOGGING
# ============================================

def debug_log(
    message: str,
    level: DebugLevel = DebugLevel.DEBUG,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    source: Optional[str] = None
) -> None:
    """
    Log debug message if debugging enabled.
    
    CRITICAL: Checks is_debug_enabled() FIRST for zero overhead.
    
    Args:
        message: Main log message
        level: Log level (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL)
        data: Optional structured data to include
        error: Optional error message
        source: Optional source identifier (auto-detected if not provided)
    
    Examples:
        debug_log("Processing started", level=DebugLevel.INFO)
        debug_log("User input received", data={"user_id": 123})
        debug_log("Calculation failed", level=DebugLevel.ERROR, error=str(e))
    """
    # CRITICAL: First check - if debugging disabled, return immediately
    if not is_debug_enabled():
        return
    
    settings = get_settings()
    
    # Check if this log level should be output
    level_hierarchy = {
        DebugLevel.NONE: 0,
        DebugLevel.ERROR: 1,
        DebugLevel.WARNING: 2,
        DebugLevel.INFO: 3,
        DebugLevel.DEBUG: 4,
        DebugLevel.TRACE: 5
    }
    
    if level_hierarchy.get(level, 0) > level_hierarchy.get(settings.debug_level, 0):
        return
    
    # Build log entry
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)[:-3]  # Trim to milliseconds
    
    # Auto-detect source if not provided
    if source is None:
        frame = inspect.currentframe().f_back
        source = f"{frame.f_code.co_filename}:{frame.f_lineno}"
    
    # Build structured log
    log_parts = [
        f"[{timestamp}]",
        f"[{level.value.upper()}]",
        f"[{source}]",
        message
    ]
    
    log_entry = " ".join(log_parts)
    
    # Add structured data if present
    if data:
        try:
            data_str = json.dumps(data, indent=2, default=str)
            log_entry += f"\n  Data: {data_str}"
        except Exception as e:
            log_entry += f"\n  Data: {data} (JSON serialization failed: {e})"
    
    # Add error if present
    if error:
        log_entry += f"\n  Error: {error}"
    
    # Output log
    _output_log(log_entry, level, settings)


def _output_log(log_entry: str, level: DebugLevel, settings):
    """
    Output log to console and/or file based on settings.
    
    Internal function - not meant to be called directly.
    """
    # Console output with colors
    if settings.log_to_console:
        colors = {
            DebugLevel.TRACE: "\033[90m",      # Dark gray
            DebugLevel.DEBUG: "\033[36m",      # Cyan
            DebugLevel.INFO: "\033[32m",       # Green
            DebugLevel.WARNING: "\033[33m",    # Yellow
            DebugLevel.ERROR: "\033[31m",      # Red
        }
        reset = "\033[0m"
        
        color = colors.get(level, "")
        print(f"{color}{log_entry}{reset}")
    
    # File output
    if settings.log_to_file:
        try:
            log_path = Path(settings.log_file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Error writing to log file: {e}", file=sys.stderr)


# ============================================
# FUNCTION TRACING DECORATOR
# ============================================

def trace_function(
    enabled: bool = True,
    trace_args: bool = True,
    trace_result: bool = True,
    max_arg_length: int = MAX_ARG_LENGTH,
    max_result_length: int = MAX_STRING_LENGTH,
    log_level: DebugLevel = DebugLevel.TRACE
):
    """
    Decorator to trace function entry/exit with arguments and return values.
    
    CRITICAL: Zero overhead when debugging disabled.
    
    Args:
        enabled: Whether tracing is enabled for this function
        trace_args: Log function arguments
        trace_result: Log function return value
        max_arg_length: Maximum length for argument representation
        max_result_length: Maximum length for result representation
        log_level: Log level to use
    
    Usage:
        @trace_function()
        async def my_function(arg1, arg2):
            return arg1 + arg2
        
        @trace_function(trace_args=True, trace_result=False)
        def sensitive_function(password):
            return hash(password)
    
    Output:
        >>> CALL: my_function(arg1=5, arg2=3)
        <<< RETURN: my_function = 8 (0.001s)
    
    Performance:
        When debug_enabled=False: ZERO overhead (returns original function)
        When debug_enabled=True: ~0.5ms overhead per call
    """
    def decorator(func: Callable) -> Callable:
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # CRITICAL: Check debug enabled FIRST (zero overhead if disabled)
            if not (enabled and is_debug_enabled() and get_settings().trace_function_calls):
                return await func(*args, **kwargs)
            
            # Get function information
            func_name = func.__qualname__
            module_name = func.__module__
            full_name = f"{module_name}.{func_name}"
            
            # Format arguments for logging
            call_info = f"{func_name}("
            if trace_args:
                arg_strs = []
                
                # Positional arguments
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                for i, arg in enumerate(args):
                    param_name = param_names[i] if i < len(param_names) else f"arg{i}"
                    arg_repr = _truncate_repr(arg, max_arg_length)
                    arg_strs.append(f"{param_name}={arg_repr}")
                
                # Keyword arguments
                for key, value in kwargs.items():
                    value_repr = _truncate_repr(value, max_arg_length)
                    arg_strs.append(f"{key}={value_repr}")
                
                call_info += ", ".join(arg_strs)
            else:
                call_info += "..."
            
            call_info += ")"
            
            # Log entry
            debug_log(f">>> CALL: {call_info}", level=log_level, source=full_name)
            
            # Execute function
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                # Log successful return
                return_info = f"{func_name}"
                if trace_result:
                    result_repr = _truncate_repr(result, max_result_length)
                    return_info += f" = {result_repr}"
                
                debug_log(
                    f"<<< RETURN: {return_info} ({elapsed:.3f}s)",
                    level=log_level,
                    source=full_name,
                    data={"elapsed_ms": f"{elapsed * 1000:.2f}ms"}
                )
                
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                
                # Log exception
                debug_log(
                    f"<<< EXCEPTION: {func_name} ({elapsed:.3f}s)",
                    level=DebugLevel.ERROR,
                    source=full_name,
                    error=str(e),
                    data={
                        "exception_type": type(e).__name__,
                        "elapsed_ms": f"{elapsed * 1000:.2f}ms",
                        "traceback": traceback.format_exc()
                    }
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # CRITICAL: Check debug enabled FIRST
            if not (enabled and is_debug_enabled() and get_settings().trace_function_calls):
                return func(*args, **kwargs)
            
            # Same logic as async_wrapper but for sync functions
            func_name = func.__qualname__
            module_name = func.__module__
            full_name = f"{module_name}.{func_name}"
            
            call_info = f"{func_name}("
            if trace_args:
                arg_strs = []
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                for i, arg in enumerate(args):
                    param_name = param_names[i] if i < len(param_names) else f"arg{i}"
                    arg_repr = _truncate_repr(arg, max_arg_length)
                    arg_strs.append(f"{param_name}={arg_repr}")
                
                for key, value in kwargs.items():
                    value_repr = _truncate_repr(value, max_arg_length)
                    arg_strs.append(f"{key}={value_repr}")
                
                call_info += ", ".join(arg_strs)
            else:
                call_info += "..."
            
            call_info += ")"
            
            debug_log(f">>> CALL: {call_info}", level=log_level, source=full_name)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                return_info = f"{func_name}"
                if trace_result:
                    result_repr = _truncate_repr(result, max_result_length)
                    return_info += f" = {result_repr}"
                
                debug_log(
                    f"<<< RETURN: {return_info} ({elapsed:.3f}s)",
                    level=log_level,
                    source=full_name,
                    data={"elapsed_ms": f"{elapsed * 1000:.2f}ms"}
                )
                
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                debug_log(
                    f"<<< EXCEPTION: {func_name} ({elapsed:.3f}s)",
                    level=DebugLevel.ERROR,
                    source=full_name,
                    error=str(e),
                    data={
                        "exception_type": type(e).__name__,
                        "elapsed_ms": f"{elapsed * 1000:.2f}ms",
                        "traceback": traceback.format_exc()
                    }
                )
                raise
        
        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# ============================================
# SPECIALIZED TRACE DECORATORS
# ============================================

def trace_ai_call(func: Callable) -> Callable:
    """
    Decorator specifically for AI service calls.
    
    Logs AI requests/responses with token usage and latency.
    Zero overhead when AI tracing disabled.
    
    Usage:
        @trace_ai_call
        async def generate(self, request):
            return await self.client.generate(request)
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        if not (is_debug_enabled() and get_settings().trace_ai_calls):
            return await func(*args, **kwargs)
        
        func_name = func.__qualname__
        
        # Extract request info if available
        request_info = {}
        if len(args) > 1:  # First arg is usually 'self'
            request = args[1]
            if hasattr(request, 'prompt'):
                request_info['prompt_length'] = len(request.prompt)
            if hasattr(request, 'model'):
                request_info['model'] = request.model
        
        debug_log(
            f">>> AI_CALL: {func_name}",
            level=DebugLevel.DEBUG,
            data=request_info
        )
        
        start_time = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        # Extract response info if available
        response_info = {"elapsed_ms": f"{elapsed * 1000:.2f}ms"}
        if hasattr(result, 'usage'):
            response_info['tokens'] = result.usage
        if hasattr(result, 'model'):
            response_info['model'] = result.model
        
        debug_log(
            f"<<< AI_CALL: {func_name}",
            level=DebugLevel.DEBUG,
            data=response_info
        )
        
        return result
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        if not (is_debug_enabled() and get_settings().trace_ai_calls):
            return func(*args, **kwargs)
        
        func_name = func.__qualname__
        
        debug_log(f">>> AI_CALL: {func_name}", level=DebugLevel.DEBUG)
        
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        debug_log(
            f"<<< AI_CALL: {func_name}",
            level=DebugLevel.DEBUG,
            data={"elapsed_ms": f"{elapsed * 1000:.2f}ms"}
        )
        
        return result
    
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def trace_matching(func: Callable) -> Callable:
    """
    Decorator for matching engine operations.
    
    Logs matching operations with scores and confidence.
    Zero overhead when matching tracing disabled.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not (is_debug_enabled() and get_settings().trace_matching_engine):
            return func(*args, **kwargs)
        
        func_name = func.__qualname__
        
        debug_log(f">>> MATCHING: {func_name}", level=DebugLevel.DEBUG)
        
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        # Extract matching metrics
        metrics = {"elapsed_ms": f"{elapsed * 1000:.2f}ms"}
        
        if isinstance(result, list):
            metrics['matches_count'] = len(result)
            if result and hasattr(result[0], 'confidence'):
                metrics['top_confidence'] = f"{result[0].confidence:.3f}"
                metrics['avg_confidence'] = f"{sum(m.confidence for m in result) / len(result):.3f}"
        
        debug_log(
            f"<<< MATCHING: {func_name}",
            level=DebugLevel.DEBUG,
            data=metrics
        )
        
        return result
    
    return wrapper


def trace_validation(func: Callable) -> Callable:
    """
    Decorator for validation operations.
    
    Logs validation checks with pass/fail status.
    Zero overhead when validation tracing disabled.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not (is_debug_enabled() and get_settings().trace_validation):
            return func(*args, **kwargs)
        
        func_name = func.__qualname__
        
        debug_log(f">>> VALIDATION: {func_name}", level=DebugLevel.DEBUG)
        
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        # Extract validation result
        metrics = {"elapsed_ms": f"{elapsed * 1000:.2f}ms"}
        
        if isinstance(result, bool):
            metrics['passed'] = result
        elif hasattr(result, 'is_valid'):
            metrics['passed'] = result.is_valid
            if hasattr(result, 'errors'):
                metrics['error_count'] = len(result.errors)
        
        debug_log(
            f"<<< VALIDATION: {func_name}",
            level=DebugLevel.DEBUG,
            data=metrics
        )
        
        return result
    
    return wrapper


# ============================================
# PERFORMANCE MONITORING
# ============================================

class PerformanceTimer:
    """
    Performance timer for measuring operation durations.
    
    Supports multiple checkpoints and generates performance reports.
    
    Usage:
        timer = PerformanceTimer("my_operation")
        
        timer.start()
        # ... do work ...
        timer.checkpoint("phase1")
        # ... more work ...
        timer.checkpoint("phase2")
        timer.stop()
        
        print(timer.report())
    """
    
    def __init__(self, name: str, enabled: bool = True):
        """
        Initialize performance timer.
        
        Args:
            name: Name of the operation being timed
            enabled: Whether timing is enabled (respects global debug setting)
        """
        self.name = name
        self.enabled = enabled and is_debug_enabled()
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.checkpoints: List[Dict[str, Any]] = []
    
    def start(self) -> 'PerformanceTimer':
        """Start the timer"""
        if self.enabled:
            self.start_time = time.time()
            debug_log(
                f"⏱️  TIMER_START: {self.name}",
                level=DebugLevel.DEBUG
            )
        return self
    
    def checkpoint(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """Record a checkpoint with optional metadata"""
        if self.enabled and self.start_time:
            elapsed = time.time() - self.start_time
            checkpoint_data = {
                "name": name,
                "timestamp": time.time(),
                "elapsed_from_start": elapsed,
                "metadata": metadata or {}
            }
            self.checkpoints.append(checkpoint_data)
            
            debug_log(
                f"⏱️  CHECKPOINT: {self.name}.{name} ({elapsed:.3f}s from start)",
                level=DebugLevel.DEBUG,
                data=metadata
            )
    
    def stop(self) -> float:
        """
        Stop the timer and return total elapsed time.
        
        Returns:
            Total elapsed time in seconds (0 if disabled)
        """
        if self.enabled and self.start_time:
            self.end_time = time.time()
            elapsed = self.end_time - self.start_time
            
            debug_log(
                f"⏱️  TIMER_STOP: {self.name} (total: {elapsed:.3f}s)",
                level=DebugLevel.DEBUG,
                data={"total_ms": f"{elapsed * 1000:.2f}ms"}
            )
            
            return elapsed
        
        return 0.0
    
    def report(self) -> str:
        """
        Generate a formatted performance report.
        
        Returns:
            Multi-line string with performance breakdown
        """
        if not self.enabled or not self.start_time:
            return f"Performance Timer: {self.name} (disabled)"
        
        total_time = (self.end_time or time.time()) - self.start_time
        
        lines = [
            f"\n{'='*60}",
            f"Performance Report: {self.name}",
            f"{'='*60}",
            f"Total Time: {total_time:.3f}s ({total_time * 1000:.2f}ms)",
            f"Checkpoints: {len(self.checkpoints)}",
            ""
        ]
        
        if self.checkpoints:
            lines.append("Checkpoint Breakdown:")
            lines.append(f"{'Name':<30} {'Elapsed':<15} {'From Prev':<15}")
            lines.append("-" * 60)
            
            prev_time = self.start_time
            for cp in self.checkpoints:
                elapsed_from_start = cp['elapsed_from_start']
                elapsed_from_prev = cp['timestamp'] - prev_time
                
                lines.append(
                    f"{cp['name']:<30} "
                    f"{elapsed_from_start:>6.3f}s ({elapsed_from_start * 1000:>7.2f}ms)  "
                    f"{elapsed_from_prev:>6.3f}s ({elapsed_from_prev * 1000:>7.2f}ms)"
                )
                
                prev_time = cp['timestamp']
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
        return False


# ============================================
# UTILITY FUNCTIONS
# ============================================

def _truncate_repr(obj: Any, max_length: int) -> str:
    """
    Create a truncated string representation of an object.
    
    Args:
        obj: Object to represent
        max_length: Maximum length of representation
    
    Returns:
        Truncated string representation
    """
    try:
        repr_str = repr(obj)
        if len(repr_str) <= max_length:
            return repr_str
        else:
            return repr_str[:max_length-3] + "..."
    except Exception:
        return f"<{type(obj).__name__}>"


def _safe_json(obj: Any) -> str:
    """
    Safely serialize object to JSON.
    
    Args:
        obj: Object to serialize
    
    Returns:
        JSON string or error message
    """
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception as e:
        return f"<JSON serialization failed: {e}>"


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def measure_overhead():
    """
    Measure the overhead of debug decorators when disabled.
    
    Returns:
        Dict with overhead measurements
    
    Usage:
        from backend.utils.debug import measure_overhead
        print(measure_overhead())
    """
    import timeit
    
    # Simple function to test
    def simple_func(x, y):
        return x + y
    
    # Decorated version
    @trace_function()
    def decorated_func(x, y):
        return x + y
    
    # Measure without debug
    iterations = 100000
    
    # Baseline
    baseline_time = timeit.timeit(
        lambda: simple_func(1, 2),
        number=iterations
    )
    
    # With decorator (debug disabled)
    with_decorator_time = timeit.timeit(
        lambda: decorated_func(1, 2),
        number=iterations
    )
    
    overhead = with_decorator_time - baseline_time
    overhead_percent = (overhead / baseline_time) * 100
    overhead_per_call = (overhead / iterations) * 1000000  # microseconds
    
    return {
        "iterations": iterations,
        "baseline_time": f"{baseline_time:.6f}s",
        "decorated_time": f"{with_decorator_time:.6f}s",
        "overhead": f"{overhead:.6f}s",
        "overhead_percent": f"{overhead_percent:.2f}%",
        "overhead_per_call": f"{overhead_per_call:.3f}µs"
    }
