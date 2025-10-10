"""
Version 4: Simple Stateless Server

Adds stateless authentication to Version 3.
Key idea: No server sessions, use API keys with every request.
"""

from flask import Flask, jsonify, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_v4.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
                    'href': url_for('get_book', book_id=self.id, _external=True),
                    'method': 'GET'
                },
                'update': {
                    'href': url_for('update_book', book_id=self.id, _external=True),
                    'method': 'PUT'
                },
                'delete': {
                    'href': url_for('delete_book', book_id=self.id, _external=True),
                    'method': 'DELETE'
                }
            }
        
        return data

def clear_cache():
    """Clear cache (same as previous versions)"""
    cache.clear()
    print("[CACHE] Cleared all cached data")

# NEW in Version 4: Simple stateless authentication
def get_user_from_token(api_key):
    """Extract user info from API key (no session lookup)"""
    try:
        # Simple demo: API key is base64 encoded email
        email = base64.b64decode(api_key).decode('utf-8')
        if '@' in email:  
            return email
        return None
    except:
        return None

def require_auth(f):
    """NEW: Decorator requiring authentication with each request"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check Authorization header in EVERY request
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_AUTHORIZATION',
                    'message': 'Authorization header required: Bearer <api_key>'
                },
                '_links': {
                    'get_api_key': {
                        'href': url_for('get_api_key', _external=True),
                        'method': 'POST',
                        'description': 'Get API key for authentication'
                    }
                }
            }), 401
        
        api_key = auth_header.replace('Bearer ', '')
        user_email = get_user_from_token(api_key)
        
        if not user_email:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_API_KEY',
                    'message': 'Invalid API key'
                }
            }), 401
        
        kwargs['user_email'] = user_email
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

# NEW: Authentication endpoint (no session creation)
@app.route('/api/auth', methods=['POST'])
def get_api_key():
    """Get API key for stateless authentication"""
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_EMAIL',
                'message': 'Email required to generate API key'
            }
        }), 400
    
    email = data['email']
    
    if '@' not in email:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_EMAIL',
                'message': 'Valid email address required'
            }
        }), 400
    
    # Generate simple API key 
    api_key = base64.b64encode(email.encode('utf-8')).decode('utf-8')
    
    return jsonify({
        'success': True,
        'data': {
            'api_key': api_key,
            'email': email,
            'instructions': 'Include in Authorization header: Bearer <api_key>'
        },
        'message': 'API key generated successfully'
    }), 201

# API root (no auth required)
@app.route('/api', methods=['GET'])
def api_root():
    """API entry point"""
    return jsonify({
        'message': 'Library Management API',
        'version': '4.0 - Simple Stateless',
        'authentication': 'Required for all endpoints except /api/auth',
        '_links': {
            'get_api_key': {
                'href': url_for('get_api_key', _external=True),
                'method': 'POST',
                'description': 'Get API key for authentication'
            },
            'books': {
                'href': url_for('get_books', _external=True),
                'method': 'GET',
                'description': 'Get all books (requires auth)'
            }
        }
    })

# All book endpoints now require authentication
@app.route('/api/books', methods=['GET'])
@require_auth  # NEW: Must include API key with EVERY request
def get_books(user_email):
    """GET books - cacheable, with auth"""
    cache_key = 'all_books'
    
    if cache_key in cache:
        print(f"[CACHE] HIT - returning books from cache for {user_email}")
        response = jsonify(cache[cache_key])
        response.headers['Cache-Control'] = 'max-age=300'
        response.headers['X-Cache-Status'] = 'HIT'
        return response
    
    print(f"[CACHE] MISS - getting books from database for {user_email}")
    books = Book.query.all()
    
    data = {
        'success': True,
        'data': [book.to_dict() for book in books],
        'count': len(books),
        'message': f'Found {len(books)} books',
        'authenticated_user': user_email,
        '_links': {
            'self': {
                'href': url_for('get_books', _external=True),
                'method': 'GET'
            },
            'create': {
                'href': url_for('create_book', _external=True),
                'method': 'POST'
            }
        }
    }
    
    cache[cache_key] = data
    
    response = jsonify(data)
    response.headers['Cache-Control'] = 'max-age=300'
    response.headers['X-Cache-Status'] = 'MISS'
    return response

@app.route('/api/books/<int:book_id>', methods=['GET'])
@require_auth
def get_book(user_email, book_id):
    """GET single book - cacheable, with auth"""
    cache_key = f'book_{book_id}'
    
    if cache_key in cache:
        print(f"[CACHE] HIT - book {book_id} from cache for {user_email}")
        response = jsonify(cache[cache_key])
        response.headers['Cache-Control'] = 'max-age=600'
        response.headers['X-Cache-Status'] = 'HIT'
        return response
    
    print(f"[CACHE] MISS - getting book {book_id} from database for {user_email}")
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({
            'success': False,
            'error': {
                'code': 'BOOK_NOT_FOUND',
                'message': f'Book with ID {book_id} not found'
            },
            '_links': {
                'books': {
                    'href': url_for('get_books', _external=True),
                    'description': 'View all books'
                }
            }
        }), 404
    
    data = {
        'success': True,
        'data': book.to_dict(),
        'authenticated_user': user_email
    }
    
    cache[cache_key] = data
    
    response = jsonify(data)
    response.headers['Cache-Control'] = 'max-age=600'
    response.headers['X-Cache-Status'] = 'MISS'
    return response

@app.route('/api/books', methods=['POST'])
@require_auth
def create_book(user_email):
    """POST - Create book (requires auth)"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_REQUEST',
                'message': 'Request body must be JSON'
            }
        }), 400
    
    required = ['title', 'author', 'isbn']
    missing = [f for f in required if f not in data]
    
    if missing:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_FIELDS',
                'message': f'Missing required fields: {", ".join(missing)}',
                'required_fields': required
            }
        }), 400
    
    existing_book = Book.query.filter_by(isbn=data['isbn']).first()
    if existing_book:
        return jsonify({
            'success': False,
            'error': {
                'code': 'DUPLICATE_ISBN',
                'message': 'Book with this ISBN already exists'
            }
        }), 400
    
    book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn']
    )
    
    db.session.add(book)
    db.session.commit()
    
    clear_cache()
    
    response = jsonify({
        'success': True,
        'data': book.to_dict(),
        'message': 'Book created successfully',
        'created_by': user_email 
    })
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Location'] = url_for('get_book', book_id=book.id, _external=True)
    return response, 201

@app.route('/api/books/<int:book_id>', methods=['PUT'])
@require_auth
def update_book(user_email, book_id):
    """PUT - Update book (requires auth)"""
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({
            'success': False,
            'error': {
                'code': 'BOOK_NOT_FOUND',
                'message': f'Book with ID {book_id} not found'
            }
        }), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_REQUEST',
                'message': 'Request body must be JSON'
            }
        }), 400
    
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'available' in data:
        book.available = data['available']
    
    db.session.commit()
    clear_cache()
    
    response = jsonify({
        'success': True,
        'data': book.to_dict(),
        'message': 'Book updated successfully',
        'updated_by': user_email
    })
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@require_auth
def delete_book(user_email, book_id):
    """DELETE - Remove book (requires auth)"""
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({
            'success': False,
            'error': {
                'code': 'BOOK_NOT_FOUND',
                'message': f'Book with ID {book_id} not found'
            }
        }), 404
    
    print(f"[DELETE] Book {book_id} deleted by {user_email}")
    db.session.delete(book)
    db.session.commit()
    clear_cache()
    
    return '', 204

@app.route('/api/stats', methods=['GET'])
@require_auth
def get_stats(user_email):
    """Real-time stats (requires auth)"""
    total = Book.query.count()
    available = Book.query.filter_by(available=True).count()
    borrowed = total - available
    
    response = jsonify({
        'success': True,
        'data': {
            'total_books': total,
            'available_books': available,
            'borrowed_books': borrowed,
            'timestamp': datetime.utcnow().isoformat()
        },
        'message': 'Real-time statistics (never cached)',
        'requested_by': user_email,
        '_links': {
            'books': {
                'href': url_for('get_books', _external=True),
                'description': 'View all books'
            }
        }
    })
    response.headers['Cache-Control'] = 'no-store'
    return response

# Cache management (no auth needed for demo)
@app.route('/api/cache/status', methods=['GET'])
def cache_status():
    """Show cache status"""
    return jsonify({
        'success': True,
        'data': {
            'cached_items': len(cache),
            'cache_keys': list(cache.keys())
        },
        'note': 'Cache is shared across all authenticated users'
    })

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache_endpoint():
    """Clear cache"""
    clear_cache()
    return jsonify({
        'success': True,
        'message': 'Cache cleared successfully'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check (no auth required)"""
    return jsonify({
        'status': 'healthy',
        'service': 'Library Management Server',
        'version': '4.0 - Simple Stateless',
        'features': [
            'Client-Server separation (v1)',
            'Basic HTTP caching (v2)',
            'Standard HTTP methods & HATEOAS (v3)',
            'Stateless authentication (v4)'
        ],
        'authentication': 'API key required for most endpoints'
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        if Book.query.count() == 0:
            sample_books = [
                Book(title="REST in Practice", author="Jim Webber", isbn="0596805829"),
                Book(title="Building APIs", author="Brenda Jin", isbn="1617295108"),
                Book(title="Clean Code", author="Robert C. Martin", isbn="0132350882"),
            ]
            db.session.add_all(sample_books)
            db.session.commit()
            print(" Sample books added")
    
    print("="*60)
    print("VERSION 4: SIMPLE STATELESS SERVER")
    print("="*60)
    print("Server running on http://127.0.0.1:5001")
    print()
    print("New in Version 4:")
    print("   No server-side sessions (stateless)")
    print("   API key authentication with every request")
    print("   Each request is self-contained")
    print("   Better scalability (no session storage)")
    print("   All features from Versions 1-3")
    
    app.run(debug=True, port=5001)