"""
Version 2: Simple Cacheable Server

Adds basic caching to Version 1.
Key idea: Cache GET responses, clear cache when data changes.
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_v2.db'
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'available': self.available,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

def clear_cache():
    """Clear cache when data changes"""
    cache.clear()
    print("[CACHE] Cleared all cached data")

# CACHEABLE ENDPOINTS (GET = reading data)
@app.route('/api/books', methods=['GET'])
def get_books():
    """GET books - cacheable because we're just reading data"""
    cache_key = 'all_books'
    
    # Check if we have it in cache
    if cache_key in cache:
        print(f"[CACHE] HIT - returning books from cache")
        response = jsonify(cache[cache_key])
        response.headers['Cache-Control'] = 'max-age=300'
        response.headers['X-Cache-Status'] = 'HIT'
        return response
    
    # Not in cache - get from database
    print(f"[CACHE] MISS - getting books from database")
    books = Book.query.all()
    data = {
        'success': True,
        'data': [book.to_dict() for book in books],
        'message': f'Found {len(books)} books'
    }
    
    # Save to cache for next time
    cache[cache_key] = data
    
    response = jsonify(data)
    response.headers['Cache-Control'] = 'max-age=300'
    response.headers['X-Cache-Status'] = 'MISS'
    return response

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """GET single book - also cacheable"""
    cache_key = f'book_{book_id}'
    
    # Check cache
    if cache_key in cache:
        print(f"[CACHE] HIT - book {book_id} from cache")
        response = jsonify(cache[cache_key])
        response.headers['Cache-Control'] = 'max-age=600'
        response.headers['X-Cache-Status'] = 'HIT'
        return response
    
    # Get from database
    print(f"[CACHE] MISS - getting book {book_id} from database")
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({
            'success': False,
            'message': 'Book not found'
        }), 404
    
    data = {
        'success': True,
        'data': book.to_dict()
    }
    
    # Save to cache
    cache[cache_key] = data
    
    response = jsonify(data)
    response.headers['Cache-Control'] = 'max-age=600' 
    response.headers['X-Cache-Status'] = 'MISS'
    return response

# NON-CACHEABLE ENDPOINTS (POST/PUT = changing data)
@app.route('/api/books', methods=['POST'])
def create_book():
    """POST - NOT cacheable because we're creating new data"""
    data = request.get_json()
    
    if not data or not all(key in data for key in ['title', 'author', 'isbn']):
        return jsonify({
            'success': False,
            'message': 'Missing required fields: title, author, isbn'
        }), 400
    
    # Check if book exists
    existing_book = Book.query.filter_by(isbn=data['isbn']).first()
    if existing_book:
        return jsonify({
            'success': False,
            'message': 'Book with this ISBN already exists'
        }), 400
    
    # Create new book
    book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn']
    )
    
    db.session.add(book)
    db.session.commit()
    
    # Clear cache because data changed
    clear_cache()
    
    response = jsonify({
        'success': True,
        'data': book.to_dict(),
        'message': 'Book created successfully'
    })
    response.headers['Cache-Control'] = 'no-cache'
    return response, 201

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """PUT - NOT cacheable because we're updating data"""
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({
            'success': False,
            'message': 'Book not found'
        }), 404
    
    data = request.get_json()
    
    # Update book fields
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'available' in data:
        book.available = data['available']
    
    db.session.commit()
    
    # Clear cache because data changed
    clear_cache()
    
    response = jsonify({
        'success': True,
        'data': book.to_dict(),
        'message': 'Book updated successfully'
    })
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Real-time stats - NEVER cache (always needs fresh data)"""
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
        'message': 'Real-time statistics (always fresh)'
    })
    response.headers['Cache-Control'] = 'no-store' 
    return response

# Cache management endpoints
@app.route('/api/cache/status', methods=['GET'])
def cache_status():
    """Show what's in the cache"""
    return jsonify({
        'success': True,
        'data': {
            'cached_items': len(cache),
            'cache_keys': list(cache.keys())
        }
    })

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache_endpoint():
    """Manually clear the cache"""
    clear_cache()
    return jsonify({
        'success': True,
        'message': 'Cache cleared successfully'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'Library Management Server',
        'version': '2.0 - Simple Cacheable',
        'new_features': [
            'Basic caching for GET requests',
            'Cache-Control headers',
            'Automatic cache clearing on data changes'
        ]
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if Book.query.count() == 0:
            sample_books = [
                Book(title="Clean Code", author="Robert C. Martin", isbn="0132350882"),
                Book(title="The Pragmatic Programmer", author="Hunt & Thomas", isbn="0135957052"),
                Book(title="Design Patterns", author="Gang of Four", isbn="0201633612"),
            ]
            db.session.add_all(sample_books)
            db.session.commit()
            print("✓ Sample books added")
    
    print("="*60)
    print("VERSION 2: SIMPLE CACHEABLE SERVER")
    print("="*60)
    print("Server running on http://127.0.0.1:5001")
    
    app.run(debug=True, port=5001)