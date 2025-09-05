"""
Structured logging configuration.

Sets up structured logging with JSON formatting for production and human-readable
formatting for development.
"""

import logging
import logging.config
import sys
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory

from app.config import settings


def setup_logging() -> None:
    """
    Configure structured logging for the application.
    
    Sets up different log formats for development and production environments.
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )
    
    # Configure structlog processors
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add JSON formatting for production
    if settings.environment == "production":
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Human-readable formatting for development
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (defaults to calling module)
        
    Returns:
        structlog.BoundLogger: Configured logger instance
    """
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


def log_function_call(func_name: str, **kwargs) -> Dict[str, Any]:
    """
    Create a log entry for function calls.
    
    Args:
        func_name: Name of the function being called
        **kwargs: Additional context to log
        
    Returns:
        dict: Log entry data
    """
    return {
        "event": "function_call",
        "function": func_name,
        **kwargs
    }


def log_api_call(method: str, path: str, **kwargs) -> Dict[str, Any]:
    """
    Create a log entry for API calls.
    
    Args:
        method: HTTP method
        path: API path
        **kwargs: Additional context to log
        
    Returns:
        dict: Log entry data
    """
    return {
        "event": "api_call",
        "method": method,
        "path": path,
        **kwargs
    }


def log_database_operation(operation: str, table: str, **kwargs) -> Dict[str, Any]:
    """
    Create a log entry for database operations.
    
    Args:
        operation: Database operation (SELECT, INSERT, UPDATE, DELETE)
        table: Database table name
        **kwargs: Additional context to log
        
    Returns:
        dict: Log entry data
    """
    return {
        "event": "database_operation",
        "operation": operation,
        "table": table,
        **kwargs
    }


def log_security_event(event_type: str, **kwargs) -> Dict[str, Any]:
    """
    Create a log entry for security events.
    
    Args:
        event_type: Type of security event
        **kwargs: Additional context to log
        
    Returns:
        dict: Log entry data
    """
    return {
        "event": "security_event",
        "event_type": event_type,
        **kwargs
    }
