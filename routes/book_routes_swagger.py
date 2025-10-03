from flask import request
from flask_restx import Namespace, Resource, fields
from services.book_service import BookService
from utils.response_helpers import success_response, error_response, handle_service_error

# Create namespace for books API
book_ns = Namespace('books', description='Book management operations', path='/api/books')

# Define models for Swagger documentation
book_model = book_ns.model('Book', {
    'id': fields.Integer(readonly=True, description='Book ID'),
    'title': fields.String(required=True, description='Book title', max_length=100),
    'author': fields.String(required=True, description='Book author', max_length=100),
    'isbn': fields.String(required=True, description='ISBN number', max_length=13),
    'available': fields.Boolean(readonly=True, description='Availability status'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp')
})

book_input_model = book_ns.model('BookInput', {
    'title': fields.String(required=True, description='Book title', max_length=100),
    'author': fields.String(required=True, description='Book author', max_length=100),
    'isbn': fields.String(required=True, description='ISBN number', max_length=13)
})

success_response_model = book_ns.model('SuccessResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Response message'),
    'data': fields.Raw(description='Response data')
})

error_response_model = book_ns.model('ErrorResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Error message'),
    'data': fields.Raw(description='Error details')
})

@book_ns.route('')
class BookList(Resource):
    @book_ns.doc('get_books')
    @book_ns.marshal_with(success_response_model)
    @book_ns.param('search', 'Search query for title or author', type='string', required=False)
    def get(self):
        """Get all books or search books"""
        try:
            query = request.args.get('search')
            
            if query:
                books = BookService.search_books(query)
            else:
                books = BookService.get_all_books()
            
            return success_response(
                data=[book.to_dict() for book in books],
                message=f"Found {len(books)} books"
            )
        except Exception as e:
            return error_response("Internal server error", 500)
    
    @book_ns.doc('create_book')
    @book_ns.expect(book_input_model, validate=True)
    @book_ns.marshal_with(success_response_model, code=201)
    @book_ns.response(400, 'Validation Error', error_response_model)
    def post(self):
        """Create a new book"""
        try:
            data = request.get_json()
            if not data:
                return error_response("No JSON data provided", 400)
            
            # Validate required fields
            required_fields = ['title', 'author', 'isbn']
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return error_response(f"Missing required fields: {', '.join(missing_fields)}", 400)
            
            book = BookService.create_book(data)
            return success_response(
                data=book.to_dict(),
                message="Book created successfully",
                status_code=201
            )
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response("Internal server error", 500)

@book_ns.route('/available')
class AvailableBooks(Resource):
    @book_ns.doc('get_available_books')
    @book_ns.marshal_with(success_response_model)
    def get(self):
        """Get all available books"""
        try:
            books = BookService.get_available_books()
            return success_response(
                data=[book.to_dict() for book in books],
                message=f"Found {len(books)} available books"
            )
        except Exception as e:
            return error_response("Internal server error", 500)

@book_ns.route('/<int:book_id>')
class Book(Resource):
    @book_ns.doc('get_book')
    @book_ns.marshal_with(success_response_model)
    @book_ns.response(404, 'Book not found', error_response_model)
    def get(self, book_id):
        """Get a specific book by ID"""
        try:
            book = BookService.get_book_by_id(book_id)
            if not book:
                return error_response("Book not found", 404)
            
            return success_response(
                data=book.to_dict(),
                message="Book retrieved successfully"
            )
        except Exception as e:
            return error_response("Internal server error", 500)
    
    @book_ns.doc('update_book')
    @book_ns.expect(book_input_model, validate=True)
    @book_ns.marshal_with(success_response_model)
    @book_ns.response(400, 'Validation Error', error_response_model)
    @book_ns.response(404, 'Book not found', error_response_model)
    def put(self, book_id):
        """Update an existing book"""
        try:
            data = request.get_json()
            if not data:
                return error_response("No JSON data provided", 400)
                
            book = BookService.update_book(book_id, data)
            return success_response(
                data=book.to_dict(),
                message="Book updated successfully"
            )
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response("Internal server error", 500)
    
    @book_ns.doc('delete_book')
    @book_ns.marshal_with(success_response_model, code=204)
    @book_ns.response(400, 'Cannot delete borrowed book', error_response_model)
    @book_ns.response(404, 'Book not found', error_response_model)
    def delete(self, book_id):
        """Delete a book"""
        try:
            BookService.delete_book(book_id)
            return success_response(
                message="Book deleted successfully",
                status_code=204
            )
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response("Internal server error", 500)