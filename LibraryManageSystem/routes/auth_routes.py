from flask import Blueprint, request, jsonify, make_response
import jwt
import datetime
from functools import wraps
from os import getenv
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = getenv("SECRET_KEY")

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic auth="Login required"'}), 401

    if auth['username'] == 'admin' and auth['password'] == 'password':
        token = jwt.encode({
            'user': auth['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():

    return jsonify({'message': 'Logged out successfully'})


@auth_bp.route('/set_cookie', methods=['POST'])
def set_cookie():
    """Set refresh token into an HttpOnly cookie. Client should POST {refresh_token: '...'} and use credentials: 'include'."""
    data = request.json or {}
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({'message': 'Refresh token is required'}), 400

    # Build response and set HttpOnly cookie
    resp = make_response(jsonify({'message': 'Refresh token cookie set'}), 200)
    # For local development secure=False. In production, set secure=True and proper domain, sameSite, and max_age.
    resp.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax')
    return resp