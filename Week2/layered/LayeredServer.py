"""
RESTful Constraint: Layered System

This demonstrates a layered architecture where components are organized
into hierarchical layers, each with specific responsibilities.
The client cannot tell if it's connected directly to the end server or an intermediary.

Key Benefits:
- Separation of concerns
- Independent layer evolution
- Load balancing and caching through intermediaries
- Enhanced security through layer isolation
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging

# Configure logging to demonstrate layer operations
logging.basicConfig(
    level=logging.INFO,
    format='[%(name)s] %(message)s'
)

# ============================================================================
# LAYER 1: DATA ACCESS LAYER (DAL)
# Responsible for direct database operations
# ============================================================================

class DataAccessLayer:
    """
    Layer 1: Data Access Layer
    - Direct interaction with database
    - CRUD operations
    - No business logic
    """
    
    logger = logging.getLogger('DATA-LAYER')
    
    def __init__(self, db):
        self.db = db
    
    def get_all_books(self):
        """Retrieve all books from database"""
        self.logger.info("Fetching all books from database")
        from models import Book
        return Book.query.all()
    
    def get_book_by_id(self, book_id):
        """Get single book by ID"""
        self.logger.info(f"Fetching book ID {book_id} from database")
        from models import Book
        return Book.query.get(book_id)
    
    def create_book(self, title, author, isbn):
        """Create new book record"""
        self.logger.info(f"Creating book: {title}")
        from models import Book
        book = Book(title=title, author=author, isbn=isbn)
        self.db.session.add(book)
        self.db.session.commit()
        return book
    
    def update_book(self, book, **kwargs):
        """Update book attributes"""
        self.logger.info(f"Updating book ID {book.id}")
        for key, value in kwargs.items():
            if hasattr(book, key):
                setattr(book, key, value)
        self.db.session.commit()
        return book
    
    def delete_book(self, book):
        """Delete book from database"""
        self.logger.info(f"Deleting book ID {book.id}")
        self.db.session.delete(book)
        self.db.session.commit()


# ============================================================================
# LAYER 2: BUSINESS LOGIC LAYER (BLL)
# Contains business rules and validation
# ============================================================================

class BusinessLogicLayer:
    """
    Layer 2: Business Logic Layer
    - Business rules and validation
    - Uses DAL for data operations
    - Independent of data storage details
    """
    
    logger = logging.getLogger('BUSINESS-LAYER')
    
    def __init__(self, dal):
        self.dal = dal
    
    def get_all_books(self):
        """Get all books with business logic"""
        self.logger.info("Processing: Get all books")
        books = self.dal.get_all_books()
        return [self._book_to_dict(book) for book in books]
    
    def get_book(self, book_id):
        """Get book with validation"""
        self.logger.info(f"Processing: Get book {book_id}")
        book = self.dal.get_book_by_id(book_id)
        
        if not book:
            raise ValueError("Book not found")
        
        return self._book_to_dict(book)
    
    def create_book(self, title, author, isbn):
        """Create book with business validation"""
        self.logger.info("Processing: Create new book")
        
        # Business rule: Validate ISBN format
        if not isbn or len(isbn) not in [10, 13]:
            raise ValueError("ISBN must be 10 or 13 characters")
        
        # Business rule: Title and author required
        if not title or not author:
            raise ValueError("Title and author are required")
        
        # Business rule: Check for duplicate ISBN
        existing = self.dal.db.session.query(
            self.dal.db.Model.metadata.tables['book']
        ).filter_by(isbn=isbn).first()
        
        if existing:
            raise ValueError(f"Book with ISBN {isbn} already exists")
        
        book = self.dal.create_book(title, author, isbn)
        self.logger.info(f"✓ Book created: {book.title}")
        return self._book_to_dict(book)
    
    def update_book_availability(self, book_id, available):
        """Update book availability with business logic"""
        self.logger.info(f"Processing: Update availability for book {book_id}")
        
        book = self.dal.get_book_by_id(book_id)
        if not book:
            raise ValueError("Book not found")
        
        # Business rule: Can only update availability status
        self.dal.update_book(book, available=available)
        self.logger.info(f"✓ Book {book_id} availability: {available}")
        return self._book_to_dict(book)
    
    def _book_to_dict(self, book):
        """Convert book model to dictionary"""
        return {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'available': book.available
        }


# ============================================================================
# LAYER 3: API/PRESENTATION LAYER
# Handles HTTP requests/responses
# ============================================================================

class PresentationLayer:
    """
    Layer 3: Presentation/API Layer
    - HTTP request/response handling
    - Input validation
    - Response formatting
    - Uses BLL for business operations
    """
    
    logger = logging.getLogger('API-LAYER')
    
    def __init__(self, bll):
        self.bll = bll
    
    def handle_get_books(self):
        """Handle GET /books request"""
        self.logger.info("Request: GET /books")
        try:
            books = self.bll.get_all_books()
            return self._success_response(books, f"Found {len(books)} books")
        except Exception as e:
            return self._error_response(str(e), 500)
    
    def handle_get_book(self, book_id):
        """Handle GET /books/<id> request"""
        self.logger.info(f"Request: GET /books/{book_id}")
        try:
            book = self.bll.get_book(book_id)
            return self._success_response(book)
        except ValueError as e:
            return self._error_response(str(e), 404)
        except Exception as e:
            return self._error_response(str(e), 500)
    
    def handle_create_book(self, request_data):
        """Handle POST /books request"""
        self.logger.info("Request: POST /books")
        
        # Presentation layer: Validate request format
        if not request_data:
            return self._error_response("No data provided", 400)
        
        required = ['title', 'author', 'isbn']
        missing = [f for f in required if f not in request_data]
        
        if missing:
            return self._error_response(
                f"Missing fields: {', '.join(missing)}",
                400
            )
        
        try:
            book = self.bll.create_book(
                request_data['title'],
                request_data['author'],
                request_data['isbn']
            )
            return self._success_response(book, "Book created", 201)
        except ValueError as e:
            return self._error_response(str(e), 400)
        except Exception as e:
            return self._error_response(str(e), 500)
    
    def handle_update_availability(self, book_id, request_data):
        """Handle PUT /books/<id>/availability request"""
        self.logger.info(f"Request: PUT /books/{book_id}/availability")
        
        if 'available' not in request_data:
            return self._error_response("'available' field required", 400)
        
        try:
            book = self.bll.update_book_availability(
                book_id,
                request_data['available']
            )
            return self._success_response(book, "Availability updated")
        except ValueError as e:
            return self._error_response(str(e), 404)
        except Exception as e:
            return self._error_response(str(e), 500)
    
    def _success_response(self, data, message="Success", status_code=200):
        """Standard success response format"""
        return {
            'success': True,
            'data': data,
            'message': message
        }, status_code
    
    def _error_response(self, message, status_code=400):
        """Standard error response format"""
        return {
            'success': False,
            'message': message,
            'data': None
        }, status_code


# ============================================================================
# FLASK APPLICATION - Integrates all layers
# ============================================================================

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_layered.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    available = db.Column(db.Boolean, default=True)

# Make Book available to DAL
import sys
sys.modules['models'] = type(sys)('models')
sys.modules['models'].Book = Book

# Initialize layers
dal = DataAccessLayer(db)
bll = BusinessLogicLayer(dal)
presentation = PresentationLayer(bll)

# API Routes - Delegate to Presentation Layer
@app.route('/api/books', methods=['GET'])
def get_books():
    """API endpoint delegates to presentation layer"""
    result, status_code = presentation.handle_get_books()
    return jsonify(result), status_code

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """API endpoint delegates to presentation layer"""
    result, status_code = presentation.handle_get_book(book_id)
    return jsonify(result), status_code

@app.route('/api/books', methods=['POST'])
def create_book():
    """API endpoint delegates to presentation layer"""
    result, status_code = presentation.handle_create_book(request.get_json())
    return jsonify(result), status_code

@app.route('/api/books/<int:book_id>/availability', methods=['PUT'])
def update_availability(book_id):
    """API endpoint delegates to presentation layer"""
    result, status_code = presentation.handle_update_availability(
        book_id,
        request.get_json()
    )
    return jsonify(result), status_code

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'Layered Library System',
        'layers': ['Data Access', 'Business Logic', 'Presentation/API']
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add sample data
        if Book.query.count() == 0:
            samples = [
                Book(title="Microservices Patterns", author="Chris Richardson", isbn="1617294543"),
                Book(title="Building Microservices", author="Sam Newman", isbn="1491950358"),
            ]
            db.session.add_all(samples)
            db.session.commit()
            print("✓ Sample books added")
    
    print("="*70)
    print("LAYERED SYSTEM ARCHITECTURE DEMONSTRATION")
    print("="*70)
    print("Server running on http://127.0.0.1:5004")
    print("\nArchitecture Layers:")
    print("  1. Data Access Layer (DAL) - Database operations")
    print("  2. Business Logic Layer (BLL) - Business rules")
    print("  3. Presentation Layer (API) - HTTP handling")
    print("\nBenefits:")
    print("  ✓ Separation of concerns")
    print("  ✓ Independent layer testing")
    print("  ✓ Easy to modify or replace layers")
    print("  ✓ Clear responsibility boundaries")
    print("\nWatch the console to see layer interactions!")
    print("="*70)
    
    app.run(debug=True, port=5004)
