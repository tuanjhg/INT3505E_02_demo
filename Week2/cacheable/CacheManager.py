"""
RESTful Constraint: Cacheable

This demonstrates how REST APIs should explicitly mark responses as cacheable or non-cacheable.
Proper caching improves performance, reduces bandwidth, and decreases server load.

Key Benefits:
- Improved client-side performance
- Reduced network traffic
- Lower server load
- Better scalability
"""

from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_cache.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Simple in-memory cache for demonstration
# In production, use Redis, Memcached, or HTTP caching
cache_store = {}

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    available = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'available': self.available,
            'last_updated': self.last_updated.isoformat()
        }
    
    def get_etag(self):
        """Generate ETag for cache validation"""
        content = f"{self.id}{self.title}{self.last_updated}"
        return hashlib.md5(content.encode()).hexdigest()


def cacheable(max_age=300):
    """
    Decorator to make responses cacheable
    Adds appropriate Cache-Control headers
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if client sent If-None-Match (ETag validation)
            client_etag = request.headers.get('If-None-Match')
            
            # Generate cache key from request
            cache_key = f"{request.path}?{request.query_string.decode()}"
            
            # Check cache
            if cache_key in cache_store:
                cached_data = cache_store[cache_key]
                server_etag = cached_data['etag']
                
                # If client's ETag matches, return 304 Not Modified
                if client_etag == server_etag:
                    response = make_response('', 304)
                    response.headers['ETag'] = server_etag
                    response.headers['Cache-Control'] = f'public, max-age={max_age}'
                    print(f"[CACHE] 304 Not Modified - {cache_key}")
                    return response
                
                # Check if cache is still fresh
                if datetime.utcnow() < cached_data['expires']:
                    print(f"[CACHE] HIT - {cache_key}")
                    response = make_response(jsonify(cached_data['data']))
                    response.headers['ETag'] = server_etag
                    response.headers['Cache-Control'] = f'public, max-age={max_age}'
                    response.headers['X-Cache'] = 'HIT'
                    response.headers['Age'] = str(int((datetime.utcnow() - cached_data['cached_at']).total_seconds()))
                    return response
            
            # Cache miss - execute function
            print(f"[CACHE] MISS - {cache_key}")
            result = f(*args, **kwargs)
            
            if isinstance(result, tuple):
                response_data, status_code = result
            else:
                response_data = result
                status_code = 200
            
            # Only cache successful responses
            if status_code == 200:
                # Generate ETag
                etag = hashlib.md5(json.dumps(response_data).encode()).hexdigest()
                
                # Store in cache
                cache_store[cache_key] = {
                    'data': response_data,
                    'etag': etag,
                    'cached_at': datetime.utcnow(),
                    'expires': datetime.utcnow() + timedelta(seconds=max_age)
                }
                
                # Create response with cache headers
                response = make_response(jsonify(response_data), status_code)
                response.headers['Cache-Control'] = f'public, max-age={max_age}'
                response.headers['ETag'] = etag
                response.headers['X-Cache'] = 'MISS'
                return response
            
            return jsonify(response_data), status_code
        
        return decorated_function
    return decorator


def no_cache(f):
    """
    Decorator for non-cacheable responses
    Used for dynamic or sensitive data
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        result = f(*args, **kwargs)
        
        if isinstance(result, tuple):
            response_data, status_code = result
        else:
            response_data = result
            status_code = 200
        
        response = make_response(jsonify(response_data), status_code)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    return decorated_function


# CACHEABLE ENDPOINTS

@app.route('/api/books', methods=['GET'])
@cacheable(max_age=300)  # Cache for 5 minutes
def get_books():
    """
    CACHEABLE: Book list doesn't change frequently
    Safe to cache for better performance
    """
    books = Book.query.all()
    
    return {
        'success': True,
        'data': [book.to_dict() for book in books],
        'message': f'Found {len(books)} books',
        'timestamp': datetime.utcnow().isoformat()
    }


@app.route('/api/books/<int:book_id>', methods=['GET'])
@cacheable(max_age=600)  # Cache for 10 minutes
def get_book(book_id):
    """
    CACHEABLE: Individual book details
    Uses ETag for validation
    """
    book = Book.query.get(book_id)
    
    if not book:
        return {
            'success': False,
            'message': 'Book not found'
        }, 404
    
    return {
        'success': True,
        'data': book.to_dict()
    }


@app.route('/api/books/available', methods=['GET'])
@cacheable(max_age=60)  # Cache for 1 minute (more dynamic)
def get_available_books():
    """
    CACHEABLE but with shorter TTL
    Availability changes more frequently
    """
    books = Book.query.filter_by(available=True).all()
    
    return {
        'success': True,
        'data': [book.to_dict() for book in books],
        'message': f'Found {len(books)} available books',
        'timestamp': datetime.utcnow().isoformat()
    }


# NON-CACHEABLE ENDPOINTS

@app.route('/api/books', methods=['POST'])
@no_cache
def create_book():
    """
    NON-CACHEABLE: Write operations should not be cached
    Each POST creates a new resource
    """
    data = request.get_json()
    
    if not data or not all(key in data for key in ['title', 'author', 'isbn']):
        return {
            'success': False,
            'message': 'Missing required fields'
        }, 400
    
    book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn']
    )
    
    db.session.add(book)
    db.session.commit()
    
    # Invalidate related caches
    invalidate_book_caches()
    
    return {
        'success': True,
        'data': book.to_dict(),
        'message': 'Book created successfully'
    }, 201


@app.route('/api/books/<int:book_id>', methods=['PUT'])
@no_cache
def update_book(book_id):
    """
    NON-CACHEABLE: Updates modify data
    Must not be cached
    """
    book = Book.query.get(book_id)
    
    if not book:
        return {
            'success': False,
            'message': 'Book not found'
        }, 404
    
    data = request.get_json()
    
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'available' in data:
        book.available = data['available']
    
    book.last_updated = datetime.utcnow()
    db.session.commit()
    
    # Invalidate related caches
    invalidate_book_caches()
    
    return {
        'success': True,
        'data': book.to_dict(),
        'message': 'Book updated successfully'
    }


@app.route('/api/stats/realtime', methods=['GET'])
@no_cache
def get_realtime_stats():
    """
    NON-CACHEABLE: Real-time statistics
    Must be fresh on every request
    """
    total = Book.query.count()
    available = Book.query.filter_by(available=True).count()
    borrowed = total - available
    
    return {
        'success': True,
        'data': {
            'total_books': total,
            'available_books': available,
            'borrowed_books': borrowed,
            'timestamp': datetime.utcnow().isoformat()
        },
        'message': 'Real-time statistics (not cached)'
    }


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear all cached data"""
    cache_store.clear()
    return jsonify({
        'success': True,
        'message': 'Cache cleared'
    })


@app.route('/api/cache/status', methods=['GET'])
def cache_status():
    """Get cache statistics"""
    return jsonify({
        'success': True,
        'data': {
            'cached_entries': len(cache_store),
            'cache_keys': list(cache_store.keys())
        }
    })


def invalidate_book_caches():
    """Invalidate all book-related caches when data changes"""
    keys_to_remove = [key for key in cache_store.keys() if '/api/books' in key]
    for key in keys_to_remove:
        del cache_store[key]
    print(f"[CACHE] Invalidated {len(keys_to_remove)} entries")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add sample data
        if Book.query.count() == 0:
            sample_books = [
                Book(title="Clean Code", author="Robert C. Martin", isbn="0132350882"),
                Book(title="The Pragmatic Programmer", author="Hunt & Thomas", isbn="0135957052"),
                Book(title="Design Patterns", author="Gang of Four", isbn="0201633612"),
                Book(title="Refactoring", author="Martin Fowler", isbn="0201485672"),
            ]
            db.session.add_all(sample_books)
            db.session.commit()
            print("✓ Sample books added")
    
    print("="*70)
    print("CACHEABLE ARCHITECTURE DEMONSTRATION")
    print("="*70)
    print("Server running on http://127.0.0.1:5003")
    print("\nCacheable Endpoints:")
    print("  GET /api/books (5 min cache)")
    print("  GET /api/books/<id> (10 min cache)")
    print("  GET /api/books/available (1 min cache)")
    print("\nNon-Cacheable Endpoints:")
    print("  POST /api/books")
    print("  PUT /api/books/<id>")
    print("  GET /api/stats/realtime")
    print("\nCache Management:")
    print("  POST /api/cache/clear")
    print("  GET /api/cache/status")
    print("\nTry: python CacheClient.py")
    print("="*70)
    
    app.run(debug=True, port=5003)
