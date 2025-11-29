import os
from flask import Flask
from flask_restx import Api
from dotenv import load_dotenv
from models import db

# Import monitoring and rate limiting
from utils.monitoring_middleware import setup_monitoring
from utils.rate_limiter import setup_rate_limiting
from utils.request_logger_middleware import setup_request_logging

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
    

    from models.book import Book
    from models.borrow import BorrowRecord
    # Add health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': '2025-11-18T10:00:00Z'}
    
    api = Api(
        app,
        version=os.getenv('API_VERSION', '1.0'),
        title=os.getenv('API_TITLE', 'Library Management API'),
        description=os.getenv('API_DESCRIPTION', 'A comprehensive library management system API'),
        doc='/swagger/',  # Swagger UI will be available at /swagger/
        prefix='/api',
        catch_all_404=False,  # Disable catch_all_404 to allow custom routes
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
    
    # Register versioned book routes
    from routes.book_routes_v1 import book_v1_ns
    from routes.book_routes_v2 import book_v2_ns
    
    api.add_namespace(auth_ns)
    api.add_namespace(book_ns)
    api.add_namespace(borrow_ns)
    
    # Add versioned endpoints
    api.add_namespace(book_v1_ns, path='/v1/books')
    api.add_namespace(book_v2_ns, path='/v2/books')
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
    
    # Setup monitoring, rate limiting, and logging
    setup_monitoring(app)
    setup_rate_limiting(app)
    setup_request_logging(app)
    
    # Add Prometheus metrics endpoint (after all setup to avoid conflicts)
    @app.route('/metrics')
    def metrics():
        try:
            from utils.metrics_collector import prometheus_metrics
            return prometheus_metrics.get_metrics_response()
        except Exception as e:
            # Return basic metrics even if there's an error
            return f"# Error collecting metrics: {str(e)}\n# Basic health check\nlibrary_api_up 1\n", 200, {'Content-Type': 'text/plain; charset=utf-8'}
    
    
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

# Create app instance for Gunicorn
app = create_app()