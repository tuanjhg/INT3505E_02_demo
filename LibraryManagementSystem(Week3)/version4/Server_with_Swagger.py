"""
Version 4: Simple Stateless Server with Swagger Documentation

Enhanced version of Server.py with comprehensive Swagger/OpenAPI documentation.
All original functionality is preserved, with added interactive documentation.
"""

from flask import Flask, jsonify, request, url_for
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_v4_swagger.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

api = Api(
    app,
    version='4.0',
    title='Library Management API with Swagger',
    description='''
    # 📚 Library Management System API v4.0 with Swagger
    
    A comprehensive REST API demonstrating all REST architectural constraints:
    
    ## 🏗️ REST Principles Implemented:
    - **Client-Server**: Clear separation between client and server
    - **Stateless**: No server-side sessions, API key with each request
    - **Cacheable**: HTTP caching headers for GET requests
    - **Uniform Interface**: Standard HTTP methods and resource identification
    - **Layered System**: Modular architecture with separation of concerns
    - **Code on Demand**: Hypermedia links for API navigation (HATEOAS)
    
    ## 🔐 Authentication:
    Most endpoints require an API key. Get one from `/api/auth` endpoint.
    Include it in the Authorization header: `Bearer <api_key>`
    
    ## 🚀 Features:
    - Interactive Swagger documentation
    - Comprehensive request/response validation
    - HTTP caching for performance
    - HATEOAS links for discoverability
    - Real-time statistics
    - Cache management
    ''',
    doc='/swagger/',
    prefix='/api',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'API Key Authorization header using the Bearer scheme. Example: "Bearer {api_key}"'
        }
    },
    security='Bearer'
)

cache = {}

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self, include_links=True):
        data = {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'available': self.available,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_links:
            data['_links'] = {
                'self': {
                    'href': url_for('books_book_detail', book_id=self.id, _external=True),
                    'method': 'GET'
                },
                'update': {
                    'href': url_for('books_book_detail', book_id=self.id, _external=True),
                    'method': 'PUT'
                },
                'delete': {
                    'href': url_for('books_book_detail', book_id=self.id, _external=True),
                    'method': 'DELETE'
                }
            }
        
        return data

def clear_cache():
    """Clear cache (same as previous versions)"""
    cache.clear()
    print("[CACHE] Cleared all cached data")

from swagger_routes import create_swagger_routes
auth_ns, books_ns, admin_ns = create_swagger_routes(api, db, Book, cache, clear_cache)

# Register namespaces
api.add_namespace(auth_ns)
api.add_namespace(books_ns)
api.add_namespace(admin_ns)

# Health Check 
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Library Management Server',
        'version': '4.0 - Simple Stateless with Swagger',
        'features': [
            'Client-Server separation (v1)',
            'Basic HTTP caching (v2)',
            'Standard HTTP methods & HATEOAS (v3)',
            'Stateless authentication (v4)',
            'Interactive Swagger documentation'
        ],
        'swagger_ui': url_for('doc', _external=True),
        'authentication': 'API key required for most endpoints'
    })

# API Root (outside API namespace for backward compatibility)
@app.route('/api')
def api_root():
    """API entry point"""
    return jsonify({
        'message': 'Library Management API',
        'version': '4.0 - Simple Stateless with Swagger',
        'authentication': 'Required for all endpoints except /api/auth',
        'swagger_ui': url_for('doc', _external=True),
        '_links': {
            'swagger': {
                'href': url_for('doc', _external=True),
                'description': 'Interactive API documentation'
            },
            'get_api_key': {
                'href': url_for('auth_authentication', _external=True),
                'method': 'POST',
                'description': 'Get API key for authentication'
            },
            'books': {
                'href': url_for('books_book_list', _external=True),
                'method': 'GET',
                'description': 'Get all books (requires auth)'
            },
            'health': {
                'href': url_for('health_check', _external=True),
                'method': 'GET',
                'description': 'Health check'
            }
        }
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        if Book.query.count() == 0:
            sample_books = [
                Book(title="REST in Practice", author="Jim Webber", isbn="0596805829"),
                Book(title="Building APIs", author="Brenda Jin", isbn="1617295108"),
                Book(title="Clean Code", author="Robert C. Martin", isbn="0132350882"),
                Book(title="API Design Patterns", author="JJ Geewax", isbn="1617295850"),
                Book(title="Microservices Patterns", author="Chris Richardson", isbn="1617294549")
            ]
            db.session.add_all(sample_books)
            db.session.commit()
            print("Sample books added")
    
    print("📚 Swagger UI: http://127.0.0.1:5003/swagger/")
    print("🔗 API Root: http://127.0.0.1:5003/api")
    print("🏥 Health Check: http://127.0.0.1:5003/api/health")
    
    app.run(debug=True, port=5003)