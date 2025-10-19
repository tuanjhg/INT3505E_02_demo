"""
Authentication middleware for protecting routes
"""
from flask import session, redirect, url_for, request, jsonify
from functools import wraps
from services.auth_service import AuthService

def login_required(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in via session
        if 'user_id' not in session:
            # Redirect to login page
            return redirect(url_for('web.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def api_token_required(f):
    """Decorator to require valid JWT token for API routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload, error = AuthService.verify_token(token, token_type='access')
        
        if error:
            return jsonify({'success': False, 'message': error}), 401
        
        # Add user info to request context
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('web.login', next=request.url))
        
        if not session.get('is_admin', False):
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function
