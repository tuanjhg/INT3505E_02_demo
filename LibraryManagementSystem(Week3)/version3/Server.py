"""
Version 3: Simple Uniform Interface Server

Adds uniform interface to Version 2 (keeps all caching).
Key idea: Standard HTTP methods + HATEOAS links + better errors.
"""

from flask import Flask, jsonify, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_v3.db'
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
        
        # NEW in Version 3: Add HATEOAS links
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
    """Clear cache (same as Version 2)"""
    cache.clear()
    print("[CACHE] Cleared all cached data")

# NEW in Version 3: API root with links
@app.route('/api', methods=['GET'])
def api_root():
    """API entry point - shows available endpoints"""
    return jsonify({
        'message': 'Library Management API',
        'version': '3.0 - Simple Uniform Interface',
        '_links': {
            'books': {
                'href': url_for('get_books', _external=True),
                'method': 'GET',
                'description': 'Get all books'
            },
            'create_book': {
                'href': url_for('create_book', _external=True),
                'method': 'POST',
                'description': 'Create a new book'
            }
        }
    })

# GET - Read data (cacheable, same as Version 2)
@app.route('/api/books', methods=['GET'])
def get_books():
    """GET books - cacheable with HATEOAS links"""
    cache_key = 'all_books'
    
    if cache_key in cache:
        print(f"[CACHE] HIT - returning books from cache")
        response = jsonify(cache[cache_key])
        response.headers['Cache-Control'] = 'max-age=300'
        response.headers['X-Cache-Status'] = 'HIT'
        return response
    
    print(f"[CACHE] MISS - getting books from database")
    books = Book.query.all()
    
    # NEW: Enhanced response with links
    data = {
        'success': True,
        'data': [book.to_dict() for book in books],
        'count': len(books),
        'message': f'Found {len(books)} books',
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
def get_book(book_id):
    """GET single book - cacheable with links"""
    cache_key = f'book_{book_id}'
    
    if cache_key in cache:
        print(f"[CACHE] HIT - book {book_id} from cache")
        response = jsonify(cache[cache_key])
        response.headers['Cache-Control'] = 'max-age=600'
        response.headers['X-Cache-Status'] = 'HIT'
        return response
    
    print(f"[CACHE] MISS - getting book {book_id} from database")
    book = Book.query.get(book_id)
    
    # NEW: Better error with links
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
        'data': book.to_dict()
    }
    
    cache[cache_key] = data
    
    response = jsonify(data)
    response.headers['Cache-Control'] = 'max-age=600'
    response.headers['X-Cache-Status'] = 'MISS'
    return response

# POST - Create data (not cacheable, same as Version 2)
@app.route('/api/books', methods=['POST'])
def create_book():
    """POST - Create new book with better error handling"""
    data = request.get_json()
    
    # NEW: Better error messages
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
    
    # NEW: Enhanced success response
    response = jsonify({
        'success': True,
        'data': book.to_dict(),
        'message': 'Book created successfully'
    })
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Location'] = url_for('get_book', book_id=book.id, _external=True)
    return response, 201 

# NEW in Version 3: PUT - Update data
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """PUT - Update entire book"""
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
    
    # Update fields
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
        'message': 'Book updated successfully'
    })
    response.headers['Cache-Control'] = 'no-cache'
    return response

# NEW in Version 3: DELETE - Remove data
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """DELETE - Remove book"""
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({
            'success': False,
            'error': {
                'code': 'BOOK_NOT_FOUND',
                'message': f'Book with ID {book_id} not found'
            }
        }), 404
    
    db.session.delete(book)
    db.session.commit()
    clear_cache()
    
    return '', 204

# Same as Version 2 but with links
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Real-time stats - never cached"""
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
        '_links': {
            'books': {
                'href': url_for('get_books', _external=True),
                'description': 'View all books'
            }
        }
    })
    response.headers['Cache-Control'] = 'no-store'
    return response

# Cache management (same as Version 2)
@app.route('/api/cache/status', methods=['GET'])
def cache_status():
    """Show cache status"""
    return jsonify({
        'success': True,
        'data': {
            'cached_items': len(cache),
            'cache_keys': list(cache.keys())
        }
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
    """Health check with version info"""
    return jsonify({
        'status': 'healthy',
        'service': 'Library Management Server',
        'version': '3.0 - Simple Uniform Interface',
        'features': [
            'Client-Server separation (v1)',
            'Basic HTTP caching (v2)',
            'Standard HTTP methods (v3)',
            'HATEOAS links (v3)',
            'Better error messages (v3)'
        ]
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        if Book.query.count() == 0:
            sample_books = [
                Book(title="REST API Design", author="Leonard Richardson", isbn="1449358063"),
                Book(title="Clean Code", author="Robert C. Martin", isbn="0132350882"),
                Book(title="Design Patterns", author="Gang of Four", isbn="0201633612"),
            ]
            db.session.add_all(sample_books)
            db.session.commit()
            print(" Sample books added")
    
    print("="*60)
    print("VERSION 3: SIMPLE UNIFORM INTERFACE")
    print("="*60)
    print("Server running on http://127.0.0.1:5001")
    print()
    print("New in Version 3:")
    print("   Standard HTTP methods: GET, POST, PUT, DELETE")
    print("   HATEOAS links show available actions")
    print("   Better error messages with proper status codes")
    print("   Consistent response format")
    print("   All caching features from Version 2")
    
    app.run(debug=True, port=5001)