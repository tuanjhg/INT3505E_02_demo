import os
from flask import Flask
from flask_restx import Api
from dotenv import load_dotenv
from models import db

load_dotenv()

def create_app(config=None):
    """Application factory pattern with Swagger support"""
    app = Flask(__name__)
    
    # Configuration from environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///library.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 
    

    app.config['RESTX_MASK_SWAGGER'] = False
    
    if config:
        app.config.update(config)
    

    db.init_app(app)
    
    # Initialize rate limiter
    from utils.rate_limiter import init_limiter, rate_limit_error_handler
    limiter = init_limiter(app)
    
    # Register rate limit error handler
    app.errorhandler(429)(rate_limit_error_handler)
    

    from models.book import Book
    from models.borrow import BorrowRecord
    from models.user import User
    

    api = Api(
        app,
        version=os.getenv('API_VERSION', '1.0'),
        title=os.getenv('API_TITLE', 'Library Management API'),
        description=os.getenv('API_DESCRIPTION', 'A comprehensive library management system API'),
        doc='/swagger/',  # Swagger UI will be available at /swagger/
        prefix='/api',
        authorizations={
            'apikey': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'JWT token format: Bearer <token>'
            }
        },
        security='apikey'
    )
    
    # Register API namespaces
    from routes.book_routes_swagger import book_ns
    from routes.borrow_routes_swagger import borrow_ns
    from routes.auth_routes_swagger import auth_ns
    
    api.add_namespace(auth_ns)
    api.add_namespace(book_ns)
    api.add_namespace(borrow_ns)
    from routes.web_routes import web_bp
    app.register_blueprint(web_bp)
    
    # Register Developer Portal routes
    from routes.portal_routes import portal_bp
    app.register_blueprint(portal_bp)
    
    # Suppress Chrome DevTools 404 log noise
    @app.route('/.well-known/appspecific/com.chrome.devtools.json')
    def chrome_devtools():
        """Silent handler for Chrome DevTools probe - returns 204 No Content"""
        return '', 204
    
    # Register error handlers
    register_error_handlers(app, api)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

def register_error_handlers(app, api):
    """Register global error handlers"""
    from utils.response_helpers import error_response
    
    @app.errorhandler(404)
    def not_found(error):
        return error_response("Resource not found", 404)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response("Method not allowed", 405)
    
    @app.errorhandler(500)
    def internal_error(error):
        return error_response("Internal server error", 500)

if __name__ == '__main__':
    app = create_app()
    
    # Get host and port from environment
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)