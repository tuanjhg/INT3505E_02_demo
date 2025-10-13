from flask import request
from flask_restx import Namespace, Resource, fields
from services.borrow_service import BorrowService
from utils.response_helpers import success_response, error_response

# Create namespace for borrows API
borrow_ns = Namespace('borrows', description='Book borrowing operations', path='/api/borrows')

# Define models for Swagger documentation
book_model = borrow_ns.model('BookInfo', {
    'id': fields.Integer(readonly=True, description='Book ID'),
    'title': fields.String(readonly=True, description='Book title'),
    'author': fields.String(readonly=True, description='Book author'),
    'isbn': fields.String(readonly=True, description='ISBN number'),
    'available': fields.Boolean(readonly=True, description='Availability status')
})

borrow_model = borrow_ns.model('BorrowRecord', {
    'id': fields.Integer(readonly=True, description='Borrow record ID'),
    'book_id': fields.Integer(readonly=True, description='Book ID'),
    'book': fields.Nested(book_model, readonly=True, description='Book details'),
    'borrower_name': fields.String(readonly=True, description='Borrower name'),
    'borrower_email': fields.String(readonly=True, description='Borrower email'),
    'borrow_date': fields.DateTime(readonly=True, description='Borrow date'),
    'due_date': fields.DateTime(readonly=True, description='Due date'),
    'return_date': fields.DateTime(readonly=True, description='Return date'),
    'returned': fields.Boolean(readonly=True, description='Return status'),
    'is_overdue': fields.Boolean(readonly=True, description='Overdue status')
})

borrow_input_model = borrow_ns.model('BorrowInput', {
    'book_id': fields.Integer(required=True, description='Book ID to borrow'),
    'borrower_name': fields.String(required=True, description='Borrower name', max_length=100),
    'borrower_email': fields.String(required=True, description='Borrower email', max_length=100),
    'days': fields.Integer(description='Borrowing period in days', default=14, min=1, max=90)
})

extend_input_model = borrow_ns.model('ExtendInput', {
    'additional_days': fields.Integer(required=True, description='Additional days to extend', min=1, max=30)
})

success_response_model = borrow_ns.model('SuccessResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Response message'),
    'data': fields.Raw(description='Response data')
})

error_response_model = borrow_ns.model('ErrorResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Error message'),
    'data': fields.Raw(description='Error details')
})

@borrow_ns.route('')
class BorrowList(Resource):
    @borrow_ns.doc('get_borrow_records')
    @borrow_ns.marshal_with(success_response_model)
    @borrow_ns.param('page', 'Page number (default: 1)', type='integer', default=1)
    @borrow_ns.param('per_page', 'Items per page (5, 10, 15)', type='integer', default=10, enum=[5, 10, 15])
    @borrow_ns.param('search', 'Search by borrower name or email', type='string', required=False)
    @borrow_ns.param('status', 'Filter by status (borrowed, returned, overdue)', type='string', required=False, enum=['borrowed', 'returned', 'overdue'])
    def get(self):
        """Get all borrow records with search, filtering, and pagination"""
        try:
            from utils.pagination_helpers import PaginationHelper
            
            # Get pagination parameters
            page, per_page = PaginationHelper.get_pagination_params()
            
            # Get search parameters (simplified)
            search = request.args.get('search', '').strip()
            status = request.args.get('status', '').strip()
            
            # Prepare simplified search parameters
            search_params = {
                'search': search,
                'status': status
            }
            
            # Handle legacy parameters for backward compatibility
            if request.args.get('active', '').lower() == 'true':
                search_params['status'] = 'borrowed'
            elif request.args.get('overdue', '').lower() == 'true':
                search_params['status'] = 'overdue'
            
            # Perform search with pagination
            result = BorrowService.search_and_paginate_borrows(search_params, page, per_page)
            
            # Build pagination info
            pagination_info = PaginationHelper.build_pagination_response(result, 'borrows_borrow_list')
            
            # Prepare response data
            response_data = {
                'borrows': [record.to_dict() for record in result['items']],
                'pagination': pagination_info,
                'filters': {
                    'search': search or None,
                    'status': status or None
                },
                'total_filtered': result['total']
            }
            
            return success_response(
                data=response_data,
                message=f"Found {result['total']} borrow records (page {page} of {result['pages']})"
            )
        except Exception as e:
            return error_response("Internal server error", 500)
    
    @borrow_ns.doc('borrow_book')
    @borrow_ns.expect(borrow_input_model, validate=True)
    @borrow_ns.marshal_with(success_response_model, code=201)
    @borrow_ns.response(400, 'Validation Error or Book not available', error_response_model)
    def post(self):
        """Borrow a book"""
        try:
            data = request.get_json()
            if not data:
                return error_response("No JSON data provided", 400)
            
            # Validate required fields
            required_fields = ['book_id', 'borrower_name', 'borrower_email']
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return error_response(f"Missing required fields: {', '.join(missing_fields)}", 400)
            
            record = BorrowService.borrow_book(data)
            return success_response(
                data=record.to_dict(),
                message="Book borrowed successfully",
                status_code=201
            )
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response("Internal server error", 500)

@borrow_ns.route('/<int:record_id>')
class BorrowRecord(Resource):
    @borrow_ns.doc('get_borrow_record')
    @borrow_ns.marshal_with(success_response_model)
    @borrow_ns.response(404, 'Borrow record not found', error_response_model)
    def get(self, record_id):
        """Get a specific borrow record"""
        try:
            record = BorrowService.get_borrow_record_by_id(record_id)
            if not record:
                return error_response("Borrow record not found", 404)
            
            return success_response(
                data=record.to_dict(),
                message="Borrow record retrieved successfully"
            )
        except Exception as e:
            return error_response("Internal server error", 500)

@borrow_ns.route('/<int:record_id>/return')
class ReturnBook(Resource):
    @borrow_ns.doc('return_book')
    @borrow_ns.marshal_with(success_response_model)
    @borrow_ns.response(400, 'Book already returned', error_response_model)
    @borrow_ns.response(404, 'Borrow record not found', error_response_model)
    def post(self, record_id):
        """Return a borrowed book"""
        try:
            record = BorrowService.return_book(record_id)
            return success_response(
                data=record.to_dict(),
                message="Book returned successfully"
            )
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response("Internal server error", 500)

@borrow_ns.route('/<int:record_id>/extend')
class ExtendDueDate(Resource):
    @borrow_ns.doc('extend_due_date')
    @borrow_ns.expect(extend_input_model, validate=True)
    @borrow_ns.marshal_with(success_response_model)
    @borrow_ns.response(400, 'Invalid request or book already returned', error_response_model)
    @borrow_ns.response(404, 'Borrow record not found', error_response_model)
    def post(self, record_id):
        """Extend the due date of a borrowed book"""
        try:
            data = request.get_json()
            if not data or 'additional_days' not in data:
                return error_response("Missing required field: additional_days", 400)
            
            additional_days = data.get('additional_days', 7)
            record = BorrowService.extend_due_date(record_id, additional_days)
            return success_response(
                data=record.to_dict(),
                message=f"Due date extended by {additional_days} days"
            )
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response("Internal server error", 500)

@borrow_ns.route('/overdue')
class OverdueBooks(Resource):
    @borrow_ns.doc('get_overdue_books')
    @borrow_ns.marshal_with(success_response_model)
    def get(self):
        """Get all overdue borrow records"""
        try:
            records = BorrowService.get_overdue_borrows()
            return success_response(
                data=[record.to_dict() for record in records],
                message=f"Found {len(records)} overdue books"
            )
        except Exception as e:
            return error_response("Internal server error", 500)