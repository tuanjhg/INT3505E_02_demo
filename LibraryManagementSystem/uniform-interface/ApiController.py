"""
RESTful Constraint: Uniform Interface

This demonstrates the uniform interface constraint - the fundamental feature
that distinguishes REST from other network architectural styles.

The uniform interface has four sub-constraints:
1. Identification of resources
2. Manipulation of resources through representations
3. Self-descriptive messages
4. Hypermedia as the engine of application state (HATEOAS)

Key Benefits:
- Simplified architecture
- Improved visibility of interactions
- Independent evolution of client and server
- Standard methods for all resources
"""

from flask import Flask, jsonify, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_uniform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self, include_links=True):
        """
        SUB-CONSTRAINT 2: Representation
        Resource represented in a standard format (JSON)
        """
        data = {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'available': self.available,
            'created_at': self.created_at.isoformat()
        }
        
        if include_links:
            # SUB-CONSTRAINT 4: HATEOAS
            # Include hypermedia links showing available actions
            data['_links'] = self._get_links()
        
        return data
    
    def _get_links(self):
        """
        HATEOAS: Hypermedia as the Engine of Application State
        Include links to related resources and available actions
        """
        links = {
            'self': {
                'href': url_for('get_book', book_id=self.id, _external=True),
                'method': 'GET',
                'description': 'Get this book'
            },
            'update': {
                'href': url_for('update_book', book_id=self.id, _external=True),
                'method': 'PUT',
                'description': 'Update this book'
            },
            'delete': {
                'href': url_for('delete_book', book_id=self.id, _external=True),
                'method': 'DELETE',
                'description': 'Delete this book'
            },
            'collection': {
                'href': url_for('get_books', _external=True),
                'method': 'GET',
                'description': 'Get all books'
            }
        }
        
        # Conditional links based on state
        if self.available:
            links['borrow'] = {
                'href': url_for('borrow_book', book_id=self.id, _external=True),
                'method': 'POST',
                'description': 'Borrow this book'
            }
        else:
            links['return'] = {
                'href': url_for('return_book', book_id=self.id, _external=True),
                'method': 'POST',
                'description': 'Return this book'
            }
        
        return links


# ============================================================================
# SUB-CONSTRAINT 1: Resource Identification
# Resources are identified by URIs
# Each resource has a unique, predictable URI
# ============================================================================

@app.route('/api', methods=['GET'])
def api_root():
    """
    API entry point with HATEOAS links
    Client discovers available resources through links
    """
    return jsonify({
        'message': 'Library Management API',
        'version': '1.0',
        '_links': {
            'books': {
                'href': url_for('get_books', _external=True),
                'method': 'GET',
                'description': 'List all books'
            },
            'create_book': {
                'href': url_for('create_book', _external=True),
                'method': 'POST',
                'description': 'Create a new book',
                'accepts': 'application/json',
                'schema': {
                    'title': 'string (required)',
                    'author': 'string (required)',
                    'isbn': 'string (required, 10-13 chars)'
                }
            }
        }
    })


# ============================================================================
# UNIFORM HTTP METHODS
# Same methods work on all resources predictably
# ============================================================================

@app.route('/api/books', methods=['GET'])
def get_books():
    """
    UNIFORM METHOD: GET for retrieval
    - Safe: Doesn't modify data
    - Idempotent: Multiple calls same as single call
    - Cacheable: Can be cached
    """
    books = Book.query.all()
    
    response = {
        'success': True,
        'data': [book.to_dict() for book in books],
        'count': len(books),
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
    
    # SUB-CONSTRAINT 3: Self-Descriptive Messages
    # Response includes all information needed to understand it
    response_obj = jsonify(response)
    response_obj.headers['Content-Type'] = 'application/json'
    response_obj.headers['Cache-Control'] = 'max-age=60'
    
    return response_obj


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    RESOURCE IDENTIFICATION: /api/books/{id}
    UNIFORM METHOD: GET
    """
    book = Book.query.get(book_id)
    
    if not book:
        # SUB-CONSTRAINT 3: Self-descriptive error
        return jsonify({
            'success': False,
            'error': {
                'code': 'BOOK_NOT_FOUND',
                'message': f'Book with ID {book_id} not found',
                'status': 404
            },
            '_links': {
                'books': {
                    'href': url_for('get_books', _external=True),
                    'description': 'View all books'
                }
            }
        }), 404
    
    return jsonify({
        'success': True,
        'data': book.to_dict()
    })


@app.route('/api/books', methods=['POST'])
def create_book():
    """
    UNIFORM METHOD: POST for creation
    - Not safe: Modifies data
    - Not idempotent: Multiple calls create multiple resources
    - Returns 201 Created with Location header
    """
    data = request.get_json()
    
    # Validate request (self-descriptive messages)
    if not data:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_REQUEST',
                'message': 'Request body must be JSON',
                'status': 400
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
                'fields': missing,
                'status': 400
            }
        }), 400
    
    # Create resource
    book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn']
    )
    
    db.session.add(book)
    db.session.commit()
    
    # SUB-CONSTRAINT 3: Self-descriptive response
    response = jsonify({
        'success': True,
        'data': book.to_dict(),
        'message': 'Book created successfully'
    })
    
    # Standard REST: Return 201 with Location header
    response.status_code = 201
    response.headers['Location'] = url_for('get_book', book_id=book.id, _external=True)
    response.headers['Content-Type'] = 'application/json'
    
    return response


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """
    UNIFORM METHOD: PUT for update/replace
    - Not safe: Modifies data
    - Idempotent: Multiple identical calls same as single call
    - Replaces entire resource
    """
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({
            'success': False,
            'error': {
                'code': 'BOOK_NOT_FOUND',
                'message': f'Book with ID {book_id} not found',
                'status': 404
            }
        }), 404
    
    data = request.get_json()
    
    # PUT replaces entire resource
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'isbn' in data:
        book.isbn = data['isbn']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': book.to_dict(),
        'message': 'Book updated successfully'
    })


@app.route('/api/books/<int:book_id>', methods=['PATCH'])
def patch_book(book_id):
    """
    UNIFORM METHOD: PATCH for partial update
    - Not safe: Modifies data
    - Not idempotent: Depends on patch operations
    - Updates specific fields only
    """
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({
            'success': False,
            'error': {
                'code': 'BOOK_NOT_FOUND',
                'message': f'Book with ID {book_id} not found',
                'status': 404
            }
        }), 404
    
    data = request.get_json()
    
    # PATCH updates only provided fields
    for field in ['title', 'author', 'available']:
        if field in data:
            setattr(book, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': book.to_dict(),
        'message': 'Book partially updated successfully'
    })


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    UNIFORM METHOD: DELETE for removal
    - Not safe: Modifies data
    - Idempotent: Multiple calls same as single call
    - Returns 204 No Content on success
    """
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({
            'success': False,
            'error': {
                'code': 'BOOK_NOT_FOUND',
                'message': f'Book with ID {book_id} not found',
                'status': 404
            }
        }), 404
    
    db.session.delete(book)
    db.session.commit()
    
    # Standard REST: DELETE returns 204 No Content
    return '', 204


# ============================================================================
# HATEOAS Example: State-dependent operations
# ============================================================================

@app.route('/api/books/<int:book_id>/borrow', methods=['POST'])
def borrow_book(book_id):
    """
    Action based on resource state
    Only available when book.available = True
    """
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({
            'success': False,
            'error': {
                'code': 'BOOK_NOT_FOUND',
                'message': f'Book with ID {book_id} not found',
                'status': 404
            }
        }), 404
    
    if not book.available:
        # HATEOAS: Show available actions based on state
        return jsonify({
            'success': False,
            'error': {
                'code': 'BOOK_NOT_AVAILABLE',
                'message': 'Book is not available for borrowing',
                'status': 400
            },
            '_links': {
                'return': {
                    'href': url_for('return_book', book_id=book_id, _external=True),
                    'description': 'Return this book to make it available'
                }
            }
        }), 400
    
    book.available = False
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': book.to_dict(),
        'message': 'Book borrowed successfully'
    })


@app.route('/api/books/<int:book_id>/return', methods=['POST'])
def return_book(book_id):
    """
    Action based on resource state
    Only available when book.available = False
    """
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({
            'success': False,
            'error': {
                'code': 'BOOK_NOT_FOUND',
                'message': f'Book with ID {book_id} not found',
                'status': 404
            }
        }), 404
    
    if book.available:
        return jsonify({
            'success': False,
            'error': {
                'code': 'BOOK_ALREADY_AVAILABLE',
                'message': 'Book is already available',
                'status': 400
            },
            '_links': {
                'borrow': {
                    'href': url_for('borrow_book', book_id=book_id, _external=True),
                    'description': 'Borrow this book'
                }
            }
        }), 400
    
    book.available = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': book.to_dict(),
        'message': 'Book returned successfully'
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'Uniform Interface Library API',
        'features': [
            'Resource identification (URIs)',
            'Standard representations (JSON)',
            'Self-descriptive messages',
            'HATEOAS links'
        ]
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add sample data
        if Book.query.count() == 0:
            samples = [
                Book(title="RESTful Web APIs", author="Leonard Richardson", isbn="1449358063"),
                Book(title="REST API Design Rulebook", author="Mark Masse", isbn="1449310508"),
            ]
            db.session.add_all(samples)
            db.session.commit()
            print("✓ Sample books added")
    
    print("="*70)
    print("UNIFORM INTERFACE DEMONSTRATION")
    print("="*70)
    print("Server running on http://127.0.0.1:5005")
    print("\nUniform Interface Features:")
    print("  1. Resource Identification: /api/books, /api/books/{id}")
    print("  2. Standard Representations: JSON format")
    print("  3. Self-Descriptive Messages: Complete headers and content")
    print("  4. HATEOAS: Hypermedia links in responses")
    print("\nStandard HTTP Methods:")
    print("  GET    - Retrieve (safe, idempotent, cacheable)")
    print("  POST   - Create (not safe, not idempotent)")
    print("  PUT    - Update/Replace (not safe, idempotent)")
    print("  PATCH  - Partial Update (not safe)")
    print("  DELETE - Remove (not safe, idempotent)")
    print("\nStart at: http://127.0.0.1:5005/api")
    print("="*70)
    
    app.run(debug=True, port=5005)
