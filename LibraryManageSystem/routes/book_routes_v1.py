"""
API Version 1 - Basic Book Operations
No search, no pagination - simple list all books
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from services.book_service import BookService
from utils.response_helpers import success_response, error_response

# Create namespace for books API v1
book_v1_ns = Namespace('v1/books', description='Book operations - Version 1 (Basic)')

# Define models for Swagger documentation
book_v1_model = book_v1_ns.model('BookV1', {
    'id': fields.Integer(readonly=True, description='Book ID'),
    'title': fields.String(required=True, description='Book title'),
    'author': fields.String(required=True, description='Book author'),
    'isbn': fields.String(required=True, description='ISBN number'),
    'available': fields.Boolean(readonly=True, description='Availability status')
})

book_v1_input = book_v1_ns.model('BookV1Input', {
    'title': fields.String(required=True, description='Book title', example='The Great Gatsby'),
    'author': fields.String(required=True, description='Book author', example='F. Scott Fitzgerald'),
    'isbn': fields.String(required=True, description='ISBN number', example='9780743273565')
})

@book_v1_ns.route('')
class BookListV1(Resource):
    @book_v1_ns.doc('get_all_books_v1',
                    description='Get all books - Version 1: Simple list without search or pagination')
    @book_v1_ns.response(200, 'Success')
    def get(self):
        """Get all books (v1 - no search, no pagination)"""
        try:
            # Get all books without any filtering
            books = BookService.get_all_books()
            
            return success_response(
                data={
                    'version': '1.0',
                    'books': [book.to_dict() for book in books],
                    'total': len(books)
                },
                message=f"Retrieved {len(books)} books"
            )
        except Exception as e:
            return error_response(f"Failed to retrieve books: {str(e)}", 500)
    
    @book_v1_ns.doc('create_book_v1')
    @book_v1_ns.expect(book_v1_input, validate=True)
    @book_v1_ns.response(201, 'Book created successfully')
    @book_v1_ns.response(400, 'Validation error')
    def post(self):
        """Create a new book (v1)"""
        try:
            data = request.get_json()
            if not data:
                return error_response("No JSON data provided", 400)
            
            # Validate required fields
            required_fields = ['title', 'author', 'isbn']
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return error_response(f"Missing required fields: {', '.join(missing_fields)}", 400)
            
            # Create book
            book = BookService.create_book(data)
            
            return success_response(
                data={
                    'version': '1.0',
                    'book': book.to_dict()
                },
                message="Book created successfully",
                status_code=201
            )
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response(f"Failed to create book: {str(e)}", 500)

@book_v1_ns.route('/<int:book_id>')
@book_v1_ns.param('book_id', 'The book identifier')
class BookResourceV1(Resource):
    @book_v1_ns.doc('get_book_v1')
    @book_v1_ns.response(200, 'Success')
    @book_v1_ns.response(404, 'Book not found')
    def get(self, book_id):
        """Get a single book by ID (v1)"""
        try:
            book = BookService.get_book_by_id(book_id)
            if not book:
                return error_response("Book not found", 404)
            
            return success_response(
                data={
                    'version': '1.0',
                    'book': book.to_dict()
                },
                message="Book retrieved successfully"
            )
        except Exception as e:
            return error_response(f"Failed to retrieve book: {str(e)}", 500)
    
    @book_v1_ns.doc('update_book_v1')
    @book_v1_ns.expect(book_v1_input, validate=True)
    @book_v1_ns.response(200, 'Book updated successfully')
    @book_v1_ns.response(404, 'Book not found')
    @book_v1_ns.response(400, 'Validation error')
    def put(self, book_id):
        """Update a book (v1)"""
        try:
            data = request.get_json()
            if not data:
                return error_response("No JSON data provided", 400)
            
            book = BookService.update_book(book_id, data)
            if not book:
                return error_response("Book not found", 404)
            
            return success_response(
                data={
                    'version': '1.0',
                    'book': book.to_dict()
                },
                message="Book updated successfully"
            )
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response(f"Failed to update book: {str(e)}", 500)
    
    @book_v1_ns.doc('delete_book_v1')
    @book_v1_ns.response(200, 'Book deleted successfully')
    @book_v1_ns.response(404, 'Book not found')
    @book_v1_ns.response(400, 'Cannot delete book with active borrows')
    def delete(self, book_id):
        """Delete a book (v1)"""
        try:
            success = BookService.delete_book(book_id)
            if not success:
                return error_response("Book not found", 404)
            
            return success_response(
                data={'version': '1.0'},
                message="Book deleted successfully"
            )
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response(f"Failed to delete book: {str(e)}", 500)

@book_v1_ns.route('/available')
class AvailableBooksV1(Resource):
    @book_v1_ns.doc('get_available_books_v1')
    @book_v1_ns.response(200, 'Success')
    def get(self):
        """Get all available books (v1 - no search, no pagination)"""
        try:
            books = BookService.get_available_books()
            
            return success_response(
                data={
                    'version': '1.0',
                    'books': [book.to_dict() for book in books],
                    'total': len(books)
                },
                message=f"Found {len(books)} available books"
            )
        except Exception as e:
            return error_response(f"Failed to retrieve available books: {str(e)}", 500)
