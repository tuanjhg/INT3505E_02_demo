"""
API Version 2 - Enhanced Book Operations
WITH search and pagination support
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from services.book_service import BookService
from utils.response_helpers import success_response, error_response
from utils.pagination_helpers import PaginationHelper

# Create namespace for books API v2
book_v2_ns = Namespace('v2/books', description='Book operations - Version 2 (Enhanced with search & pagination)')

# Define models for Swagger documentation
book_v2_model = book_v2_ns.model('BookV2', {
    'id': fields.Integer(readonly=True, description='Book ID'),
    'title': fields.String(required=True, description='Book title'),
    'author': fields.String(required=True, description='Book author'),
    'isbn': fields.String(required=True, description='ISBN number'),
    'available': fields.Boolean(readonly=True, description='Availability status'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp')
})

book_v2_input = book_v2_ns.model('BookV2Input', {
    'title': fields.String(required=True, description='Book title', example='1984'),
    'author': fields.String(required=True, description='Book author', example='George Orwell'),
    'isbn': fields.String(required=True, description='ISBN number', example='9780451524935')
})

pagination_model = book_v2_ns.model('Pagination', {
    'page': fields.Integer(description='Current page number'),
    'per_page': fields.Integer(description='Items per page'),
    'total': fields.Integer(description='Total items'),
    'pages': fields.Integer(description='Total pages'),
    'has_prev': fields.Boolean(description='Has previous page'),
    'has_next': fields.Boolean(description='Has next page')
})

@book_v2_ns.route('')
class BookListV2(Resource):
    @book_v2_ns.doc('get_books_v2',
                    description='Get books with search and pagination - Version 2',
                    params={
                        'page': {'description': 'Page number (default: 1)', 'type': 'integer', 'default': 1},
                        'per_page': {'description': 'Items per page (5, 10, 15)', 'type': 'integer', 'default': 10, 'enum': [5, 10, 15]},
                        'search': {'description': 'Search query for title or author', 'type': 'string'},
                        'available_only': {'description': 'Show only available books', 'type': 'boolean', 'default': False}
                    })
    @book_v2_ns.response(200, 'Success')
    def get(self):
        """Get books with search and pagination (v2)"""
        try:
            # Get pagination parameters
            page, per_page = PaginationHelper.get_pagination_params()
            
            # Get search parameters
            search = request.args.get('search', '').strip()
            available_only = request.args.get('available_only', 'false').lower() == 'true'
            
            # Prepare search parameters
            search_params = {
                'search': search,
                'available_only': available_only
            }
            
            # Perform search with pagination
            result = BookService.search_and_paginate_books(search_params, page, per_page)
            
            # Build pagination info
            pagination_info = PaginationHelper.build_pagination_response(result, 'v2/books')
            
            # Prepare response data
            response_data = {
                'version': '2.0',
                'books': [book.to_dict() for book in result['items']],
                'pagination': pagination_info,
                'filters': {
                    'search': search or None,
                    'available_only': available_only
                },
                'total_filtered': result['total']
            }
            
            return success_response(
                data=response_data,
                message=f"Found {result['total']} books (page {page} of {result['pages']})"
            )
        except Exception as e:
            return error_response(f"Failed to retrieve books: {str(e)}", 500)
    
    @book_v2_ns.doc('create_book_v2')
    @book_v2_ns.expect(book_v2_input, validate=True)
    @book_v2_ns.response(201, 'Book created successfully')
    @book_v2_ns.response(400, 'Validation error')
    def post(self):
        """Create a new book (v2)"""
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
                    'version': '2.0',
                    'book': book.to_dict()
                },
                message="Book created successfully",
                status_code=201
            )
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response(f"Failed to create book: {str(e)}", 500)

@book_v2_ns.route('/<int:book_id>')
@book_v2_ns.param('book_id', 'The book identifier')
class BookResourceV2(Resource):
    @book_v2_ns.doc('get_book_v2')
    @book_v2_ns.response(200, 'Success')
    @book_v2_ns.response(404, 'Book not found')
    def get(self, book_id):
        """Get a single book by ID (v2)"""
        try:
            book = BookService.get_book_by_id(book_id)
            if not book:
                return error_response("Book not found", 404)
            
            return success_response(
                data={
                    'version': '2.0',
                    'book': book.to_dict()
                },
                message="Book retrieved successfully"
            )
        except Exception as e:
            return error_response(f"Failed to retrieve book: {str(e)}", 500)
    
    @book_v2_ns.doc('update_book_v2')
    @book_v2_ns.expect(book_v2_input, validate=True)
    @book_v2_ns.response(200, 'Book updated successfully')
    @book_v2_ns.response(404, 'Book not found')
    @book_v2_ns.response(400, 'Validation error')
    def put(self, book_id):
        """Update a book (v2)"""
        try:
            data = request.get_json()
            if not data:
                return error_response("No JSON data provided", 400)
            
            book = BookService.update_book(book_id, data)
            if not book:
                return error_response("Book not found", 404)
            
            return success_response(
                data={
                    'version': '2.0',
                    'book': book.to_dict()
                },
                message="Book updated successfully"
            )
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response(f"Failed to update book: {str(e)}", 500)
    
    @book_v2_ns.doc('delete_book_v2')
    @book_v2_ns.response(200, 'Book deleted successfully')
    @book_v2_ns.response(404, 'Book not found')
    @book_v2_ns.response(400, 'Cannot delete book with active borrows')
    def delete(self, book_id):
        """Delete a book (v2)"""
        try:
            success = BookService.delete_book(book_id)
            if not success:
                return error_response("Book not found", 404)
            
            return success_response(
                data={'version': '2.0'},
                message="Book deleted successfully"
            )
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response(f"Failed to delete book: {str(e)}", 500)

@book_v2_ns.route('/available')
class AvailableBooksV2(Resource):
    @book_v2_ns.doc('get_available_books_v2',
                    description='Get available books with search and pagination',
                    params={
                        'page': {'description': 'Page number (default: 1)', 'type': 'integer', 'default': 1},
                        'per_page': {'description': 'Items per page (5, 10, 15)', 'type': 'integer', 'default': 10, 'enum': [5, 10, 15]},
                        'search': {'description': 'Search query for title or author', 'type': 'string'}
                    })
    @book_v2_ns.response(200, 'Success')
    def get(self):
        """Get available books with search and pagination (v2)"""
        try:
            # Get pagination parameters
            page, per_page = PaginationHelper.get_pagination_params()
            
            # Get search parameter
            search = request.args.get('search', '').strip()
            
            # Prepare search parameters (available_only is always True for this endpoint)
            search_params = {
                'search': search,
                'available_only': True
            }
            
            # Perform search with pagination
            result = BookService.search_and_paginate_books(search_params, page, per_page)
            
            # Build pagination info
            pagination_info = PaginationHelper.build_pagination_response(result, 'v2/books/available')
            
            # Prepare response data
            response_data = {
                'version': '2.0',
                'books': [book.to_dict() for book in result['items']],
                'pagination': pagination_info,
                'filters': {
                    'search': search or None,
                    'available_only': True
                },
                'total_available': result['total']
            }
            
            return success_response(
                data=response_data,
                message=f"Found {result['total']} available books (page {page} of {result['pages']})"
            )
        except Exception as e:
            return error_response(f"Failed to retrieve available books: {str(e)}", 500)
