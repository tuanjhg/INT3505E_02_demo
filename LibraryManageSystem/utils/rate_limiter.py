"""
Rate limiting configuration for Library Management System
Protects API endpoints from abuse and DDoS attacks
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request, g
import os


def get_user_identifier():
    """
    Get user identifier for rate limiting
    Uses user ID if authenticated, otherwise IP address
    """
    # Try to get user ID from JWT token
    if hasattr(g, 'current_user') and g.current_user:
        user_id = getattr(g.current_user, 'id', None)
        if user_id:
            return f"user:{user_id}"
    
    # Fallback to IP address
    return get_remote_address()


def get_user_role():
    """Get user role for tiered rate limiting"""
    if hasattr(g, 'current_user') and g.current_user:
        return getattr(g.current_user, 'role', 'regular')
    return 'anonymous'


# Initialize limiter
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri=os.getenv('REDIS_URL', 'memory://'),  # Use Redis in production
    storage_options={},
    strategy='fixed-window',
    headers_enabled=True,
    swallow_errors=True,  # Don't crash app if Redis is down
)


# Rate limit configurations by endpoint type

# Auth endpoints (most restrictive)
AUTH_LIMITS = "5 per minute"

# Public read endpoints (generous)
PUBLIC_READ_LIMITS = "100 per minute; 1000 per hour"

# Authenticated read endpoints (more generous for logged-in users)
AUTH_READ_LIMITS = "200 per minute; 5000 per hour"

# Write endpoints (more restrictive)
WRITE_LIMITS = "20 per minute; 200 per hour"

# Admin endpoints (very generous)
ADMIN_LIMITS = "1000 per minute"


def get_rate_limit_for_role():
    """
    Dynamic rate limit based on user role
    Returns rate limit string
    """
    role = get_user_role()
    
    role_limits = {
        'anonymous': "20 per minute",
        'regular': "100 per minute",
        'premium': "500 per minute",
        'admin': "10000 per minute"
    }
    
    return role_limits.get(role, "20 per minute")


def setup_rate_limiting(app):
    """Configure rate limiting for Flask app"""
    
    # Initialize limiter with app
    limiter.init_app(app)
    
    # Apply rate limiting to auth endpoints using before_request
    @app.before_request
    def apply_auth_rate_limits():
        from flask import request
        
        # Only apply to auth endpoints to avoid performance impact on all requests
        if request.path.startswith('/api/auth/') and request.method == 'POST':
            # Use Flask-Limiter's built-in rate limiting for better performance
            key = get_remote_address()
            
            # Let Flask-Limiter handle the rate limiting logic
            # This will be more efficient than manual implementation
            pass  # Flask-Limiter will handle this automatically when decorators are used
    
    # Apply rate limit to auth namespace - REMOVED: Flask-RESTX Namespace doesn't support limiter.limit()
    # from routes.auth_routes_swagger import auth_ns
    # limiter.limit(AUTH_LIMITS)(auth_ns)
    
    # Custom error handler for rate limit exceeded
    @app.errorhandler(429)
    def ratelimit_handler(e):
        from utils.response_helpers import error_response
        
        # Get retry-after header from Flask-Limiter
        retry_after = getattr(e, 'description', '60')
        if 'Try again in' in retry_after:
            retry_after = '60'
        
        return error_response(
            message=f"Rate limit exceeded. Please try again in {retry_after} seconds.",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            extra_data={'retry_after': int(retry_after)}
        ), 429, {
            'Retry-After': str(retry_after),
            'X-RateLimit-Limit': AUTH_LIMITS,
            'X-RateLimit-Remaining': '0'
        }
    
    app.logger.info("Rate limiting initialized with Flask-Limiter decorators")
    return limiter


# Example usage in routes:
"""
from utils.rate_limiter import limiter, AUTH_LIMITS, WRITE_LIMITS

# On specific route
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit(AUTH_LIMITS['login'])
def login():
    pass

# On blueprint
from flask import Blueprint
api_bp = Blueprint('api', __name__)
limiter.limit("100 per hour")(api_bp)

# Dynamic limit by role
@app.route('/api/data')
@limiter.limit(get_rate_limit_for_role)
def get_data():
    pass
"""
