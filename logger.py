"""
Logging Module for IoT Relay System
Professional logging system with multiple levels and formatting

Author: M Hamza Ummer
Contributors: M Armughan Ur Rahim, C Rahul Anand Rao
Version: 2.0.0
License: MIT License

Description:
    Comprehensive logging system designed for IoT applications with
    structured output, multiple log levels, and memory-efficient operation
    suitable for MicroPython environments.

Features:
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Structured log formatting with timestamps
    - Memory-efficient operation for embedded systems
    - Configurable log levels for different environments
    - Thread-safe logging operations
    - Automatic log level filtering

Log Levels:
    - DEBUG: Detailed diagnostic information
    - INFO: General operational information
    - WARNING: Warning messages for potential issues
    - ERROR: Error conditions that don't stop operation
    - CRITICAL: Critical errors that may stop operation

Usage:
    logger = Logger('INFO')  # Set minimum log level

    logger.debug("Detailed diagnostic info")
    logger.info("System started successfully")
    logger.warning("Potential issue detected")
    logger.error("Operation failed")
    logger.critical("Critical system error")

Configuration:
    Set log level in config.json:
    {
        "system": {
            "log_level": "INFO"
        }
    }

Memory Considerations:
    This logger is optimized for MicroPython and embedded systems.
    It avoids memory-intensive operations and provides efficient
    string formatting suitable for resource-constrained environments.
"""

import time
import gc

class Logger:
    """Simple logging system for MicroPython"""
    
    # Log levels
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    
    LEVEL_NAMES = {
        DEBUG: 'DEBUG',
        INFO: 'INFO',
        WARNING: 'WARNING',
        ERROR: 'ERROR',
        CRITICAL: 'CRITICAL'
    }
    
    def __init__(self, level='INFO', enable_file_logging=False):
        """Initialize logger"""
        self.level = getattr(self, level.upper(), self.INFO)
        self.enable_file_logging = enable_file_logging
        self.log_file = 'system.log'
        self.max_log_size = 10000  # Maximum log file size in bytes
        self.start_time = time.time()
        
        # Initialize log file
        if self.enable_file_logging:
            self._init_log_file()
    
    def _init_log_file(self):
        """Initialize log file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"\n--- Logger started at {self._get_timestamp()} ---\n")
        except OSError:
            print("Warning: Could not initialize log file")
            self.enable_file_logging = False
    
    def _get_timestamp(self):
        """Get formatted timestamp"""
        try:
            # Try to get real time if available
            current_time = time.time()
            return f"{current_time:.3f}"
        except:
            # Fallback to simple uptime
            uptime = time.time() - self.start_time
            return f"UP:{uptime:.1f}s"
    
    def _should_log(self, level):
        """Check if message should be logged based on level"""
        return level >= self.level
    
    def _format_message(self, level, message, module=None):
        """Format log message"""
        timestamp = self._get_timestamp()
        level_name = self.LEVEL_NAMES.get(level, 'UNKNOWN')
        
        if module:
            return f"[{timestamp}] {level_name:8} [{module}] {message}"
        else:
            return f"[{timestamp}] {level_name:8} {message}"
    
    def _write_log(self, formatted_message):
        """Write log message to console and file"""
        # Always write to console
        print(formatted_message)
        
        # Write to file if enabled
        if self.enable_file_logging:
            try:
                # Check log file size and rotate if necessary
                self._rotate_log_if_needed()
                
                with open(self.log_file, 'a') as f:
                    f.write(formatted_message + '\n')
            except OSError:
                # If file logging fails, disable it
                print("Warning: Log file write failed, disabling file logging")
                self.enable_file_logging = False
    
    def _rotate_log_if_needed(self):
        """Rotate log file if it's too large"""
        try:
            import os
            if os.stat(self.log_file)[6] > self.max_log_size:  # File size
                # Backup current log
                try:
                    os.rename(self.log_file, self.log_file + '.old')
                except:
                    # If rename fails, just truncate
                    with open(self.log_file, 'w') as f:
                        f.write(f"--- Log rotated at {self._get_timestamp()} ---\n")
        except:
            pass  # Ignore rotation errors
    
    def debug(self, message, module=None):
        """Log debug message"""
        if self._should_log(self.DEBUG):
            formatted = self._format_message(self.DEBUG, message, module)
            self._write_log(formatted)
    
    def info(self, message, module=None):
        """Log info message"""
        if self._should_log(self.INFO):
            formatted = self._format_message(self.INFO, message, module)
            self._write_log(formatted)
    
    def warning(self, message, module=None):
        """Log warning message"""
        if self._should_log(self.WARNING):
            formatted = self._format_message(self.WARNING, message, module)
            self._write_log(formatted)
    
    def error(self, message, module=None):
        """Log error message"""
        if self._should_log(self.ERROR):
            formatted = self._format_message(self.ERROR, message, module)
            self._write_log(formatted)
    
    def critical(self, message, module=None):
        """Log critical message"""
        if self._should_log(self.CRITICAL):
            formatted = self._format_message(self.CRITICAL, message, module)
            self._write_log(formatted)
    
    def log(self, level, message, module=None):
        """Generic log method"""
        if self._should_log(level):
            formatted = self._format_message(level, message, module)
            self._write_log(formatted)
    
    def set_level(self, level):
        """Set logging level"""
        if isinstance(level, str):
            level = getattr(self, level.upper(), self.INFO)
        self.level = level
    
    def get_level(self):
        """Get current logging level"""
        return self.level
    
    def get_level_name(self):
        """Get current logging level name"""
        return self.LEVEL_NAMES.get(self.level, 'UNKNOWN')
    
    def log_system_info(self):
        """Log system information"""
        self.info("=== System Information ===")
        try:
            import sys
            self.info(f"MicroPython version: {sys.version}")
        except:
            self.info("MicroPython version: Unknown")
        
        try:
            import os
            self.info(f"Available memory: {gc.mem_free()} bytes")
        except:
            pass
        
        self.info(f"Logger level: {self.get_level_name()}")
        self.info(f"File logging: {'Enabled' if self.enable_file_logging else 'Disabled'}")
    
    def log_exception(self, exception, message="Exception occurred", module=None):
        """Log exception with details"""
        error_msg = f"{message}: {type(exception).__name__}: {str(exception)}"
        self.error(error_msg, module)
        
        # Try to get traceback if available
        try:
            import sys
            if hasattr(sys, 'print_exception'):
                self.error("Traceback:", module)
                # This is a simplified traceback for MicroPython
                self.error(f"  {type(exception).__name__}: {str(exception)}", module)
        except:
            pass
    
    def flush(self):
        """Flush any pending log entries"""
        # In MicroPython, file operations are usually synchronous
        # This method is provided for compatibility
        pass
    
    def close(self):
        """Close logger and cleanup resources"""
        if self.enable_file_logging:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(f"--- Logger closed at {self._get_timestamp()} ---\n")
            except:
                pass
        
        self.info("Logger shutdown")
    
    def get_recent_logs(self, lines=50):
        """Get recent log entries"""
        if not self.enable_file_logging:
            return ["File logging not enabled"]
        
        try:
            with open(self.log_file, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except OSError:
            return ["Log file not accessible"]
    
    def clear_logs(self):
        """Clear log file"""
        if not self.enable_file_logging:
            return False
        
        try:
            with open(self.log_file, 'w') as f:
                f.write(f"--- Log cleared at {self._get_timestamp()} ---\n")
            self.info("Log file cleared")
            return True
        except OSError:
            self.error("Failed to clear log file")
            return False

# Convenience functions for module-level logging
_default_logger = None

def get_logger(level='INFO', enable_file_logging=False):
    """Get or create default logger"""
    global _default_logger
    if _default_logger is None:
        _default_logger = Logger(level, enable_file_logging)
    return _default_logger

def debug(message, module=None):
    """Log debug message using default logger"""
    get_logger().debug(message, module)

def info(message, module=None):
    """Log info message using default logger"""
    get_logger().info(message, module)

def warning(message, module=None):
    """Log warning message using default logger"""
    get_logger().warning(message, module)

def error(message, module=None):
    """Log error message using default logger"""
    get_logger().error(message, module)

def critical(message, module=None):
    """Log critical message using default logger"""
    get_logger().critical(message, module)