import jwt
import datetime
import secrets
from os import getenv
from models import db
from models.user import User
from werkzeug.security import check_password_hash

class AuthService:
    """Service for handling authentication operations"""
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user with username and password"""
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return None, "User not found"
        
        if not user.is_active:
            return None, "User account is deactivated"
        
        if not user.check_password(password):
            return None, "Invalid password"
        
        # Update last login
        user.last_login = datetime.datetime.utcnow()
        db.session.commit()
        
        return user, None
    
    @staticmethod
    def generate_access_token(user, expires_in_minutes=15):
        """Generate JWT access token for authenticated user (short-lived)"""
        secret_key = getenv('SECRET_KEY')
        
        payload = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'token_type': 'access',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in_minutes),
            'iat': datetime.datetime.utcnow()
        }
        
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token
    
    @staticmethod
    def generate_refresh_token(user, expires_in_days=30):
        """Generate JWT refresh token for authenticated user (long-lived)"""
        secret_key = getenv('SECRET_KEY')
        
        # Generate a unique token identifier
        jti = secrets.token_urlsafe(32)
        
        payload = {
            'user_id': user.id,
            'token_type': 'refresh',
            'jti': jti,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=expires_in_days),
            'iat': datetime.datetime.utcnow()
        }
        
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        # Store refresh token in database
        user.refresh_token = jti
        user.refresh_token_expires = datetime.datetime.utcnow() + datetime.timedelta(days=expires_in_days)
        db.session.commit()
        
        return token
    
    @staticmethod
    def generate_token(user, expires_in_hours=24):
        """Generate JWT token for authenticated user (legacy support)"""
        return AuthService.generate_access_token(user, expires_in_minutes=expires_in_hours*60)
    
    @staticmethod
    def verify_token(token, token_type='access'):
        """Verify and decode JWT token"""
        try:
            secret_key = getenv('SECRET_KEY')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Verify token type
            if payload.get('token_type') != token_type:
                return None, f"Invalid token type. Expected {token_type}"
            
            # For refresh tokens, verify against database
            if token_type == 'refresh':
                user = User.query.get(payload['user_id'])
                if not user or user.refresh_token != payload.get('jti'):
                    return None, "Refresh token has been revoked"
                if user.refresh_token_expires and user.refresh_token_expires < datetime.datetime.utcnow():
                    return None, "Refresh token has expired"
            
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """Generate new access token using refresh token"""
        payload, error = AuthService.verify_token(refresh_token, token_type='refresh')
        
        if error:
            return None, error
        
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return None, "User not found or inactive"
        
        # Generate new access token
        access_token = AuthService.generate_access_token(user)
        return access_token, None
    
    @staticmethod
    def revoke_refresh_token(user):
        """Revoke user's refresh token (logout)"""
        user.refresh_token = None
        user.refresh_token_expires = None
        db.session.commit()
    
    @staticmethod
    def create_user(username, email, password, full_name=None, is_admin=False):
        """Create a new user"""
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return None, "Username already exists"
        
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            is_admin=is_admin
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user, None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        return User.query.filter_by(username=username).first()
