"""
Centralized logging configuration for Library Management System
Provides structured logging with rotation, multiple handlers, and production-ready settings
"""

import logging
import logging.handlers
import os
import sys
import json
from datetime import datetime
from typing import Any, Dict
import traceback


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        if hasattr(record, 'path'):
            log_data['path'] = record.path
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        if hasattr(record, 'response_time_ms'):
            log_data['response_time_ms'] = record.response_time_ms
        if hasattr(record, 'ip_address'):
            log_data['ip_address'] = record.ip_address
        
        # Add exception info if present
        if record.exc_info and len(record.exc_info) >= 3 and record.exc_info[0] is not None:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else 'Unknown',
                'message': str(record.exc_info[1]) if record.exc_info[1] else 'Unknown error',
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """Colored formatter for console output (development)"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            colored_levelname = f"{self.COLORS[levelname]}{levelname:8s}{self.COLORS['RESET']}"
            record.levelname = colored_levelname
        
        return super().format(record)


def setup_logger(
    name: str = 'library_api',
    log_level: str = None,
    log_dir: str = 'logs',
    json_format: bool = False
) -> logging.Logger:
    """
    Setup and configure logger with multiple handlers
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        json_format: Use JSON format for file logs (recommended for production)
    
    Returns:
        Configured logger instance
    """
    
    # Get logger
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Set log level from environment or parameter
    level_name = log_level or os.getenv('LOG_LEVEL', 'INFO')
    level = getattr(logging, level_name.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Console handler (always colored for readability)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if os.getenv('ENVIRONMENT') == 'production':
        # Production: simple format
        console_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Development: colored format
        console_format = ColoredConsoleFormatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
    
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler - Main log (rotating)
    if json_format:
        file_formatter = JSONFormatter()
    else:
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    main_log_file = os.path.join(log_dir, 'app.log')
    file_handler = logging.handlers.RotatingFileHandler(
        main_log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Error log file (only errors and critical)
    error_log_file = os.path.join(log_dir, 'error.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    # Don't propagate to root logger
    logger.propagate = False
    
    logger.info(f"Logger initialized: {name} (level={level_name}, json={json_format})")
    
    return logger


def get_logger(name: str = 'library_api') -> logging.Logger:
    """Get or create logger instance"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Auto-configure if not already done
        json_format = os.getenv('LOG_FORMAT', 'text').lower() == 'json'
        setup_logger(name=name, json_format=json_format)
    return logger


# Convenience functions for logging with extra context
def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **kwargs
) -> None:
    """Log message with extra context fields"""
    extra = {k: v for k, v in kwargs.items() if v is not None}
    logger.log(level, message, extra=extra)


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    response_time_ms: float,
    request_id: str = None,
    user_id: str = None,
    ip_address: str = None
) -> None:
    """Log HTTP request with structured data"""
    log_with_context(
        logger,
        logging.INFO,
        f"{method} {path} - {status_code} ({response_time_ms:.2f}ms)",
        method=method,
        path=path,
        status_code=status_code,
        response_time_ms=response_time_ms,
        request_id=request_id,
        user_id=user_id,
        ip_address=ip_address
    )


def log_error(
    logger: logging.Logger,
    message: str,
    exc_info: bool = True,
    **kwargs
) -> None:
    """Log error with exception details"""
    log_with_context(
        logger,
        logging.ERROR,
        message,
        **kwargs
    )
    if exc_info:
        logger.exception(message)


# Example usage in application
if __name__ == '__main__':
    # Development example
    logger = setup_logger('test', log_level='DEBUG', json_format=False)
    
    logger.debug("Debug message - detailed information")
    logger.info("Info message - normal operation")
    logger.warning("Warning message - something unexpected")
    logger.error("Error message - operation failed")
    
    # With context
    log_request(
        logger,
        method='GET',
        path='/api/books',
        status_code=200,
        response_time_ms=45.3,
        request_id='abc-123',
        user_id='user_456',
        ip_address='192.168.1.1'
    )
    
    # Simulate error
    try:
        result = 1 / 0
    except Exception as e:
        log_error(logger, "Division by zero error", request_id='abc-123')
    
    print("\n✓ Check logs/ directory for output files")
