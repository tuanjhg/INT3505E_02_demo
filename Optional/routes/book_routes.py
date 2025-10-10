from flask import request
from flask_restx import Namespace, Resource
from services.book_service import BookService
from utils.response_helpers import success_response, error_response, handle_service_error
from utils.swagger_models import create_api_models

# Create namespace for books API
book_ns = Namespace('books', description='Book management operations', path='/api/books')

# This will be set when the namespace is added to the API
models = None

def init_book_models(api):
    """Initialize Swagger models for this namespace"""
    global models
    models = create_api_models(api)

@book_bp.route('', methods=['GET'])
@handle_service_error
def get_books():
    """Get all books or search books"""
    query = request.args.get('search')
    
    if query:
        books = BookService.search_books(query)
    else:
        books = BookService.get_all_books()
    
    return success_response(
        data=[book.to_dict() for book in books],
        message=f"Found {len(books)} books"
    )

@book_bp.route('/available', methods=['GET'])
@handle_service_error
def get_available_books():
    """Get all available books"""
    books = BookService.get_available_books()
    return success_response(
        data=[book.to_dict() for book in books],
        message=f"Found {len(books)} available books"
    )

@book_bp.route('/<int:book_id>', methods=['GET'])
@handle_service_error
def get_book(book_id):
    """Get a specific book by ID"""
    book = BookService.get_book_by_id(book_id)
    if not book:
        return error_response("Book not found", 404)
    
    return success_response(
        data=book.to_dict(),
        message="Book retrieved successfully"
    )

@book_bp.route('', methods=['POST'])
@validate_json(['title', 'author', 'isbn'])
@handle_service_error
def create_book(data):
    """Create a new book"""
    book = BookService.create_book(data)
    return success_response(
        data=book.to_dict(),
        message="Book created successfully",
        status_code=201
    )

@book_bp.route('/<int:book_id>', methods=['PUT'])
@validate_json()
@handle_service_error
def update_book(data, book_id):
    """Update an existing book"""
    book = BookService.update_book(book_id, data)
    return success_response(
        data=book.to_dict(),
        message="Book updated successfully"
    )

@book_bp.route('/<int:book_id>', methods=['DELETE'])
@handle_service_error
def delete_book(book_id):
    """Delete a book"""
    BookService.delete_book(book_id)
    return success_response(
        message="Book deleted successfully",
        status_code=204
    )