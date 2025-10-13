from flask import jsonify
from functools import wraps

def api_response(success=True, data=None, message=None, status_code=200):
    """Standard API response format"""
    response = {
        "success": success,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code

def success_response(data=None, message="Success", status_code=200):
    """Success response helper"""
    return api_response(success=True, data=data, message=message, status_code=status_code)

def error_response(message="An error occurred", status_code=400, data=None):
    """Error response helper"""
    return api_response(success=False, data=data, message=message, status_code=status_code)

def validate_json(required_fields=None):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            
            if not request.is_json:
                return error_response("Request must be JSON", 400)
            
            data = request.get_json()
            if not data:
                return error_response("No JSON data provided", 400)
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data or not data[field]]
                if missing_fields:
                    return error_response(f"Missing required fields: {', '.join(missing_fields)}", 400)
            
            return f(data, *args, **kwargs)
        return decorated_function
    return decorator

def handle_service_error(f):
    """Decorator to handle service layer errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response("Internal server error", 500)
    return decorated_function