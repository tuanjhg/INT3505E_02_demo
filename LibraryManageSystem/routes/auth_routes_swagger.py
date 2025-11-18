from flask import request, make_response
from flask_restx import Namespace, Resource, fields
from services.auth_service import AuthService
from utils.response_helpers import success_response, error_response
from utils.rate_limiter import limiter
from functools import wraps
import jwt
from os import getenv

auth_ns = Namespace('auth', description='Authentication operations')

login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='Username', example='admin'),
    'password': fields.String(required=True, description='Password', example='password123')
})

register_model = auth_ns.model('Register', {
    'username': fields.String(required=True, description='Username', example='johndoe'),
    'email': fields.String(required=True, description='Email', example='john@example.com'),
    'password': fields.String(required=True, description='Password', example='password123'),
    'full_name': fields.String(description='Full Name', example='John Doe')
})

token_response_model = auth_ns.model('TokenResponse', {
    'token': fields.String(description='JWT Token'),
    'user': fields.Raw(description='User information')
})

# Token validation decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return error_response('Token is missing', 401)
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload, error = AuthService.verify_token(token)
        
        if error:
            return error_response(error, 401)
        
        # Pass user info to the route
        return f(payload, *args, **kwargs)
    
    return decorated

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.doc('user_login')
    @auth_ns.expect(login_model, validate=True)
    @auth_ns.response(200, 'Success', token_response_model)
    @auth_ns.response(401, 'Invalid credentials')
    @auth_ns.response(429, 'Rate limit exceeded')
    @limiter.limit("5 per minute")
    @limiter.limit("20 per hour")
    def post(self):
        """Login with username and password - returns access & refresh tokens
        
        Rate Limit: 5 requests per minute, 20 requests per hour
        """
        data = request.json
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return error_response('Username and password are required', 400)
        
        user, error = AuthService.authenticate_user(username, password)
        
        if error:
            return error_response(error, 401)
        
        # Generate both access and refresh tokens
        access_token = AuthService.generate_access_token(user)
        refresh_token = AuthService.generate_refresh_token(user)
        
        # Create response with tokens
        response_data, status_code = success_response(
            data={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': 900,  # 15 minutes in seconds
                'user': user.to_dict()
            },
            message='Login successful'
        )
        
        # Set HttpOnly cookie for refresh token
        resp = make_response(response_data, status_code)
        resp.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax',
            max_age=30*24*60*60  # 30 days
        )
        return resp

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.doc('user_register')
    @auth_ns.expect(register_model, validate=True)
    @auth_ns.response(201, 'User created successfully')
    @auth_ns.response(400, 'Validation error')
    @auth_ns.response(429, 'Rate limit exceeded')
    @limiter.limit("3 per minute")
    @limiter.limit("10 per hour")
    def post(self):
        """Register a new user - returns access & refresh tokens
        
        Rate Limit: 3 requests per minute, 10 requests per hour
        """
        data = request.json
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        
        if not username or not email or not password:
            return error_response('Username, email, and password are required', 400)
        
        user, error = AuthService.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name
        )
        
        if error:
            return error_response(error, 400)
        
        # Generate both access and refresh tokens
        access_token = AuthService.generate_access_token(user)
        refresh_token = AuthService.generate_refresh_token(user)
        
        # Create response with tokens
        response_data, status_code = success_response(
            data={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': 900,  # 15 minutes in seconds
                'user': user.to_dict()
            },
            message='User registered successfully',
            status_code=201
        )
        
        # Set HttpOnly cookie for refresh token
        resp = make_response(response_data, status_code)
        resp.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax',
            max_age=30*24*60*60  # 30 days
        )
        return resp

@auth_ns.route('/me')
class CurrentUser(Resource):
    @auth_ns.doc('get_current_user', security='apikey')
    @auth_ns.response(200, 'Success')
    @auth_ns.response(401, 'Unauthorized')
    @token_required
    def get(self, payload):
        """Get current user information"""
        user = AuthService.get_user_by_id(payload['user_id'])
        
        if not user:
            return error_response('User not found', 404)
        
        return success_response(
            data=user.to_dict(),
            message='User information retrieved successfully'
        )

@auth_ns.route('/logout')
class Logout(Resource):
    @auth_ns.doc('user_logout', security='apikey')
    @auth_ns.response(200, 'Logged out successfully')
    @auth_ns.response(401, 'Unauthorized')
    @token_required
    def post(self, payload):
        """Logout (revoke refresh token and clear cookie)"""
        user = AuthService.get_user_by_id(payload['user_id'])
        if user:
            AuthService.revoke_refresh_token(user)
        
        # Create response and clear the HttpOnly cookie
        response_data, status_code = success_response(
            message='Logged out successfully'
        )
        resp = make_response(response_data, status_code)
        resp.set_cookie('refresh_token', '', expires=0, httponly=True, samesite='Lax')
        return resp

@auth_ns.route('/verify')
class VerifyToken(Resource):
    @auth_ns.doc('verify_token', security='apikey')
    @auth_ns.response(200, 'Token is valid')
    @auth_ns.response(401, 'Token is invalid')
    @token_required
    def get(self, payload):
        """Verify if token is valid"""
        return success_response(
            data={'valid': True, 'user_id': payload['user_id']},
            message='Token is valid'
        )

refresh_token_model = auth_ns.model('RefreshToken', {
    'refresh_token': fields.String(required=True, description='Refresh Token')
})

@auth_ns.route('/refresh')
class RefreshToken(Resource):
    @auth_ns.doc('refresh_token')
    @auth_ns.expect(refresh_token_model, validate=True)
    @auth_ns.response(200, 'Token refreshed successfully')
    @auth_ns.response(401, 'Invalid refresh token')
    def post(self):
        """Refresh access token using refresh token"""
        data = request.json
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return error_response('Refresh token is required', 400)
        
        access_token, error = AuthService.refresh_access_token(refresh_token)
        
        if error:
            return error_response(error, 401)
        
        return success_response(
            data={'access_token': access_token},
            message='Access token refreshed successfully'
        )
