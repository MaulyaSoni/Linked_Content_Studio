"""
Logger - Structured Logging
===========================
Clean, structured logging configuration for the application.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from pythonjsonlogger import jsonlogger


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format with color
        record.levelname = f"{color}{levelname}{reset}"
        
        # Add timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Custom format
        formatted = f"{timestamp} | {record.levelname:8} | {record.name:15} | {record.getMessage()}"
        
        return formatted


class StructuredLogger:
    """Structured logger with JSON and console output."""
    
    def __init__(self, name: str, level: str = "INFO"):
        """Initialize logger.
        
        Args:
            name: Logger name
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handler()
    
    def _setup_console_handler(self):
        """Setup console handler with colored output."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Use colored formatter for console
        formatter = ColoredFormatter()
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Setup file handler with JSON formatting."""
        try:
            # Create logs directory
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            # Log file with timestamp
            log_file = log_dir / f"linkedin_generator_{datetime.now().strftime('%Y%m%d')}.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Use JSON formatter for files
            json_formatter = jsonlogger.JsonFormatter(
                '%(asctime)s %(name)s %(levelname)s %(message)s %(filename)s %(lineno)d'
            )
            file_handler.setFormatter(json_formatter)
            
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            # If file logging fails, continue with console only
            self.logger.warning(f"Failed to setup file logging: {e}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context."""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context."""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context."""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional context."""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with optional context."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log message with additional context."""
        if kwargs:
            # Add context to message for JSON formatter
            context_str = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            full_message = f"{message} | {context_str}"
            self.logger.log(level, full_message)
        else:
            self.logger.log(level, message)
    
    def log_generation_start(self, mode: str, content_type: str):
        """Log generation start event."""
        self.info(
            "Generation started",
            mode=mode,
            content_type=content_type,
            timestamp=datetime.now().isoformat()
        )
    
    def log_generation_success(self, mode: str, duration: float, tokens: int):
        """Log generation success event."""
        self.info(
            "Generation completed successfully",
            mode=mode,
            duration_seconds=duration,
            tokens_used=tokens,
            timestamp=datetime.now().isoformat()
        )
    
    def log_generation_error(self, mode: str, error: str, duration: float):
        """Log generation error event."""
        self.error(
            "Generation failed",
            mode=mode,
            error=error,
            duration_seconds=duration,
            timestamp=datetime.now().isoformat()
        )
    
    def log_api_call(self, provider: str, endpoint: str, duration: float, success: bool):
        """Log API call event."""
        status = "success" if success else "failed"
        self.info(
            f"API call {status}",
            provider=provider,
            endpoint=endpoint,
            duration_seconds=duration,
            timestamp=datetime.now().isoformat()
        )
    
    def log_user_action(self, action: str, **context):
        """Log user action for analytics."""
        self.info(
            f"User action: {action}",
            action=action,
            timestamp=datetime.now().isoformat(),
            **context
        )


def get_logger(name: str, level: str = "INFO") -> StructuredLogger:
    """Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name, level)


def setup_logging(level: str = "INFO"):
    """Setup global logging configuration.
    
    Args:
        level: Default logging level
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if root_logger.handlers:
        return
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    formatter = ColoredFormatter()
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)


# Convenience functions for common logging patterns
def log_system_info():
    """Log system information for debugging."""
    import platform
    import sys
    
    logger = get_logger(__name__)
    
    logger.info(
        "System information",
        platform=platform.platform(),
        python_version=sys.version,
        architecture=platform.architecture()[0]
    )


def log_dependency_versions():
    """Log key dependency versions."""
    logger = get_logger(__name__)
    
    try:
        import streamlit
        import langchain
        logger.info(
            "Dependency versions",
            streamlit=streamlit.__version__,
            langchain=langchain.__version__
        )
    except ImportError as e:
        logger.warning(f"Could not log dependency versions: {e}")


# Streamlit-specific logging utilities
def log_streamlit_session():
    """Log Streamlit session information."""
    try:
        import streamlit as st
        
        logger = get_logger(__name__)
        
        session_info = {
            'session_id': getattr(st.session_state, 'session_id', 'unknown'),
            'user_agent': st.context.headers.get('user-agent', 'unknown'),
        }
        
        logger.info("Streamlit session started", **session_info)
        
    except Exception as e:
        logger = get_logger(__name__)
        logger.warning(f"Could not log Streamlit session: {e}")


if __name__ == "__main__":
    # Test the logger
    logger = get_logger("test")
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Test structured logging
    logger.log_generation_start("simple", "educational")
    logger.log_generation_success("simple", 2.5, 150)
    
    print("✅ Logger test completed")
