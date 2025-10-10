"""
RESTful Constraint: Client-Server Architecture

This demonstrates the separation of concerns between client and server.
The server manages resources (books, borrows) and exposes them through APIs.
The client consumes these APIs without knowing the implementation details.

Key Benefits:
- Separation of concerns (UI vs business logic)
- Independent evolution of client and server
- Multiple clients can use the same server
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_server.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model - Server Side
class Book(db.Model):
    """Book model representing library resources on the server"""
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

# Server API Endpoints
@app.route('/api/books', methods=['GET'])
def get_books():
    """
    Server endpoint to retrieve all books
    Client doesn't need to know how data is stored or retrieved
    """
    books = Book.query.all()
    return jsonify({
        'success': True,
        'data': [book.to_dict() for book in books],
        'message': f'Found {len(books)} books'
    })

@app.route('/api/books', methods=['POST'])
def create_book():
    """
    Server endpoint to create a new book
    Server handles validation and persistence
    """
    data = request.get_json()
    
    if not data or not all(key in data for key in ['title', 'author', 'isbn']):
        return jsonify({
            'success': False,
            'message': 'Missing required fields: title, author, isbn'
        }), 400
    
    # Server-side business logic
    existing_book = Book.query.filter_by(isbn=data['isbn']).first()
    if existing_book:
        return jsonify({
            'success': False,
            'message': 'Book with this ISBN already exists'
        }), 400
    
    book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn']
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': book.to_dict(),
        'message': 'Book created successfully'
    }), 201

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a specific book by ID"""
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({
            'success': False,
            'message': 'Book not found'
        }), 404
    
    return jsonify({
        'success': True,
        'data': book.to_dict()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Server health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Library Management Server',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    print("="*60)
    print("CLIENT-SERVER ARCHITECTURE DEMONSTRATION")
    print("="*60)
    print("Server running on http://127.0.0.1:5001")
    print("\nThis server:")
    print("- Manages book resources and business logic")
    print("- Exposes RESTful APIs for client consumption")
    print("- Is independent from client implementation")
    print("- Can serve multiple different clients")
    print("="*60)
    
    app.run(debug=True, port=5001)
