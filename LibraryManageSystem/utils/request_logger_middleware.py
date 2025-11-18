"""
Request logging middleware for Flask
Logs all incoming requests and responses with timing information
"""

import time
import uuid
from flask import request, g
from functools import wraps
from utils.logger import get_logger, log_request

logger = get_logger('request_logger')


def generate_request_id():
    """Generate unique request ID"""
    return str(uuid.uuid4())


def before_request():
    """Called before each request - start timing and generate request ID"""
    g.start_time = time.time()
    g.request_id = request.headers.get('X-Request-ID', generate_request_id())


def after_request(response):
    """Called after each request - log request details"""
    
    # Calculate response time
    if hasattr(g, 'start_time'):
        response_time_ms = (time.time() - g.start_time) * 1000
    else:
        response_time_ms = 0
    
    # Get user ID from JWT if available
    user_id = None
    if hasattr(g, 'current_user') and g.current_user:
        user_id = getattr(g.current_user, 'id', None)
    
    # Get client IP (handle proxies)
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address and ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()
    
    # Add request ID to response headers
    response.headers['X-Request-ID'] = g.request_id
    
    # Skip logging for certain paths (health checks, static files)
    skip_paths = ['/health', '/metrics', '/static', '/favicon.ico', '/.well-known']
    if not any(request.path.startswith(path) for path in skip_paths):
        # Log the request
        log_request(
            logger,
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            response_time_ms=response_time_ms,
            request_id=g.request_id,
            user_id=user_id,
            ip_address=ip_address
        )
        
        # Log slow requests as warnings
        if response_time_ms > 1000:  # > 1 second
            logger.warning(
                f"Slow request: {request.method} {request.path} took {response_time_ms:.2f}ms",
                extra={
                    'request_id': g.request_id,
                    'response_time_ms': response_time_ms,
                    'path': request.path
                }
            )
    
    return response


def log_exception(error):
    """Log unhandled exceptions"""
    logger.error(
        f"Unhandled exception: {str(error)}",
        extra={
            'request_id': getattr(g, 'request_id', 'unknown'),
            'method': request.method,
            'path': request.path,
            'ip_address': request.remote_addr
        },
        exc_info=True
    )


def setup_request_logging(app):
    """Setup request logging for Flask app"""
    app.before_request(before_request)
    app.after_request(after_request)
    app.teardown_request(log_exception)
    
    logger.info("Request logging middleware initialized")


# Decorator for logging function calls
def log_function_call(func):
    """Decorator to log function calls with arguments"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_logger = get_logger(func.__module__)
        func_logger.debug(
            f"Calling {func.__name__}",
            extra={
                'function': func.__name__,
                'args': str(args)[:200],  # Limit length
                'kwargs': str(kwargs)[:200]
            }
        )
        try:
            result = func(*args, **kwargs)
            func_logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            func_logger.error(
                f"{func.__name__} failed: {str(e)}",
                extra={'function': func.__name__},
                exc_info=True
            )
            raise
    return wrapper
