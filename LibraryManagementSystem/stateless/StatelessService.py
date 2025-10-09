"""
RESTful Constraint: Stateless

This demonstrates the stateless nature of REST APIs.
Each request contains all information needed to process it.
The server does not store client context between requests.

Key Benefits:
- Improved scalability (no session storage needed)
- Better reliability (no session loss on server failure)
- Simplified server design
- Easier load balancing
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import base64
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_stateless.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    available = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'available': self.available
        }

class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrower_name = db.Column(db.String(100), nullable=False)
    borrower_email = db.Column(db.String(100), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    returned = db.Column(db.Boolean, default=False)
    
    book = db.relationship('Book', backref='borrow_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else None,
            'borrower_name': self.borrower_name,
            'borrower_email': self.borrower_email,
            'borrow_date': self.borrow_date.isoformat(),
            'due_date': self.due_date.isoformat(),
            'returned': self.returned
        }

# Authentication Helper (Stateless - using tokens, not sessions)
def verify_api_key(api_key):
    """
    Stateless authentication - each request includes credentials
    No session storage on server
    """
    # Simple demo: API key = base64(email)
    try:
        email = base64.b64decode(api_key).decode('utf-8')
        # In production, verify against database
        return email if '@' in email else None
    except:
        return None

def require_auth(f):
    """
    Decorator for stateless authentication
    Client must provide credentials with EVERY request
    """
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Missing or invalid authorization header'
            }), 401
        
        api_key = auth_header.replace('Bearer ', '')
        user_email = verify_api_key(api_key)
        
        if not user_email:
            return jsonify({
                'success': False,
                'message': 'Invalid API key'
            }), 401
        
        # Pass user info to the route handler
        # Note: We don't store this in a session - it's extracted from the request
        kwargs['user_email'] = user_email
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

# STATELESS ENDPOINTS
# Note: Each endpoint receives ALL needed information in the request
# No server-side session state is maintained

@app.route('/api/auth/generate-key', methods=['POST'])
def generate_api_key():
    """
    Generate API key for stateless authentication
    This is just for demo - in production, use JWT or OAuth
    """
    data = request.get_json()
    email = data.get('email')
    
    if not email or '@' not in email:
        return jsonify({
            'success': False,
            'message': 'Valid email required'
        }), 400
    
    # Generate simple API key (demo only)
    api_key = base64.b64encode(email.encode('utf-8')).decode('utf-8')
    
    return jsonify({
        'success': True,
        'data': {
            'api_key': api_key,
            'email': email
        },
        'message': 'API key generated. Include in Authorization header: Bearer <api_key>'
    }), 201

@app.route('/api/books', methods=['GET'])
@require_auth
def get_books(user_email):
    """
    STATELESS: Get all books
    - Request includes authentication (no session)
    - Server doesn't remember previous requests from this client
    - Each request is self-contained
    """
    books = Book.query.all()
    
    return jsonify({
        'success': True,
        'data': [book.to_dict() for book in books],
        'message': f'Found {len(books)} books',
        'authenticated_user': user_email  # Extracted from request, not session
    })

@app.route('/api/books/<int:book_id>/borrow', methods=['POST'])
@require_auth
def borrow_book(user_email, book_id):
    """
    STATELESS: Borrow a book
    - All context provided in request (book_id, user from auth, borrower details)
    - No server session tracking user's previous actions
    - Request is self-sufficient
    """
    data = request.get_json()
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({
            'success': False,
            'message': 'Book not found'
        }), 404
    
    if not book.available:
        return jsonify({
            'success': False,
            'message': 'Book is not available'
        }), 400
    
    # Get borrower details from request (not from session)
    borrower_name = data.get('borrower_name')
    days = data.get('days', 14)
    
    if not borrower_name:
        return jsonify({
            'success': False,
            'message': 'borrower_name required in request'
        }), 400
    
    # Create borrow record
    due_date = datetime.utcnow() + timedelta(days=days)
    record = BorrowRecord(
        book_id=book_id,
        borrower_name=borrower_name,
        borrower_email=user_email,  # From auth token, not session
        due_date=due_date
    )
    
    book.available = False
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': record.to_dict(),
        'message': f'Book borrowed successfully. Due: {due_date.strftime("%Y-%m-%d")}'
    }), 201

@app.route('/api/borrows', methods=['GET'])
@require_auth
def get_user_borrows(user_email):
    """
    STATELESS: Get borrowing history for authenticated user
    - User identity from request header (not session)
    - Can filter by email from any client/device
    - No server-side state about user's browsing session
    """
    # Email from authentication token (stateless)
    records = BorrowRecord.query.filter_by(borrower_email=user_email).all()
    
    return jsonify({
        'success': True,
        'data': [record.to_dict() for record in records],
        'message': f'Found {len(records)} borrow records',
        'queried_user': user_email
    })

@app.route('/api/borrows/<int:record_id>/return', methods=['POST'])
@require_auth
def return_book(user_email, record_id):
    """
    STATELESS: Return a borrowed book
    - All information in request (record_id, auth token)
    - Server doesn't maintain conversation state
    - Request is complete and independent
    """
    record = BorrowRecord.query.get(record_id)
    
    if not record:
        return jsonify({
            'success': False,
            'message': 'Borrow record not found'
        }), 404
    
    # Verify ownership (from token, not session)
    if record.borrower_email != user_email:
        return jsonify({
            'success': False,
            'message': 'Unauthorized: This book was not borrowed by you'
        }), 403
    
    if record.returned:
        return jsonify({
            'success': False,
            'message': 'Book already returned'
        }), 400
    
    # Process return
    record.returned = True
    record.book.available = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': record.to_dict(),
        'message': 'Book returned successfully'
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Public endpoint - no auth required"""
    return jsonify({
        'status': 'healthy',
        'service': 'Stateless Library API',
        'note': 'All authenticated endpoints require Authorization header with each request'
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add sample books if database is empty
        if Book.query.count() == 0:
            sample_books = [
                Book(title="Design Patterns", author="Gang of Four", isbn="0201633612"),
                Book(title="Refactoring", author="Martin Fowler", isbn="0201485672"),
                Book(title="Domain-Driven Design", author="Eric Evans", isbn="0321125215")
            ]
            db.session.add_all(sample_books)
            db.session.commit()
            print("✓ Sample books added")
    
    print("="*70)
    print("STATELESS ARCHITECTURE DEMONSTRATION")
    print("="*70)
    print("Server running on http://127.0.0.1:5002")
    print("\nKey Stateless Features:")
    print("- No session storage on server")
    print("- Each request includes complete context (auth token)")
    print("- Server doesn't remember previous requests")
    print("- Requests are self-contained and independent")
    print("\nTry the demo client: python StatelessClient.py")
    print("="*70)
    
    app.run(debug=True, port=5002)
