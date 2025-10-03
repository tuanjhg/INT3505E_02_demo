import os
from flask import Flask
from models import db

def create_app(config=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///library.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    if config:
        app.config.update(config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    from models.book import Book
    from models.borrow import BorrowRecord
    
    # Register blueprints
    from routes.book_routes import book_bp
    from routes.borrow_routes import borrow_bp
    from routes.web_routes import web_bp
    
    app.register_blueprint(book_bp)
    app.register_blueprint(borrow_bp)
    app.register_blueprint(web_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

def register_error_handlers(app):
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
    app.run(debug=True)