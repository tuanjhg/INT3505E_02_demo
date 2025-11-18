"""
Rate Limiter Configuration

This module provides rate limiting functionality using Flask-Limiter.
It's configured to use Redis for distributed rate limiting, with fallback to in-memory storage.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request
import os

def get_request_identifier():
    """
    Custom function to identify requests for rate limiting.
    Uses IP address by default, but can use user ID if authenticated.
    """
    # Check if user is authenticated (has JWT token)
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        # For authenticated users, use token hash as identifier
        # This provides better tracking for logged-in users
        return f"user:{hash(auth_header)}"
    
    # For non-authenticated requests, use IP address
    return f"ip:{get_remote_address()}"

# Initialize limiter (will be configured in app factory)
limiter = None

def init_limiter(app):
    """
    Initialize Flask-Limiter with the Flask app.
    
    Args:
        app: Flask application instance
    
    Returns:
        Limiter instance
    """
    global limiter
    
    # Get storage URI from environment, default to in-memory
    storage_uri = os.getenv('RATE_LIMIT_STORAGE_URI', 'memory://')
    
    limiter = Limiter(
        app=app,
        key_func=get_request_identifier,
        storage_uri=storage_uri,
        default_limits=[
            "1000 per day",  # Global limit
            "200 per hour"   # Global limit
        ],
        # Strategy for how to handle rate limit headers
        strategy="fixed-window",
        # Enable rate limit headers in response
        headers_enabled=True,
        # Retry-After header format
        swallow_errors=True,  # Don't crash if rate limiter fails
        # Custom error message
        default_limits_per_method=False,
        # Application limits can be overridden
        application_limits=[]
    )
    
    return limiter

def rate_limit_error_handler(e):
    """
    Custom error handler for rate limit exceeded errors.
    
    Args:
        e: RateLimitExceeded exception
    
    Returns:
        JSON response with error details
    """
    from utils.response_helpers import error_response
    
    return error_response(
        message="Rate limit exceeded. Too many requests.",
        status_code=429,
        error_code="RATE_LIMIT_EXCEEDED",
        extra_data={
            "retry_after": e.description if hasattr(e, 'description') else None
        }
    )

# Rate limit configurations for different endpoints
RATE_LIMITS = {
    'login': [
        "5 per minute",   # Max 5 login attempts per minute
        "20 per hour"     # Max 20 login attempts per hour
    ],
    'register': [
        "3 per minute",   # Max 3 registrations per minute
        "10 per hour"     # Max 10 registrations per hour
    ],
    'refresh': [
        "10 per minute",  # Max 10 token refreshes per minute
        "100 per hour"    # Max 100 token refreshes per hour
    ],
    'api': [
        "100 per minute", # Max 100 API calls per minute
        "1000 per hour"   # Max 1000 API calls per hour
    ]
}

def get_rate_limit(endpoint_type):
    """
    Get rate limit configuration for a specific endpoint type.
    
    Args:
        endpoint_type: Type of endpoint ('login', 'register', 'refresh', 'api')
    
    Returns:
        List of rate limit strings
    """
    return RATE_LIMITS.get(endpoint_type, RATE_LIMITS['api'])
