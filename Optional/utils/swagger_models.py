from flask_restx import fields

def create_api_models(api):
    """Create API models for Swagger documentation"""
    
    # Book models
    book_model = api.model('Book', {
        'id': fields.Integer(readonly=True, description='Book ID'),
        'title': fields.String(required=True, description='Book title', max_length=100),
        'author': fields.String(required=True, description='Book author', max_length=100),
        'isbn': fields.String(required=True, description='ISBN number', max_length=13),
        'available': fields.Boolean(readonly=True, description='Availability status'),
        'created_at': fields.DateTime(readonly=True, description='Creation timestamp')
    })
    
    book_input_model = api.model('BookInput', {
        'title': fields.String(required=True, description='Book title', max_length=100),
        'author': fields.String(required=True, description='Book author', max_length=100),
        'isbn': fields.String(required=True, description='ISBN number', max_length=13)
    })
    
    # Borrow models
    borrow_model = api.model('BorrowRecord', {
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
    
    borrow_input_model = api.model('BorrowInput', {
        'book_id': fields.Integer(required=True, description='Book ID to borrow'),
        'borrower_name': fields.String(required=True, description='Borrower name', max_length=100),
        'borrower_email': fields.String(required=True, description='Borrower email', max_length=100),
        'days': fields.Integer(description='Borrowing period in days', default=14, min=1, max=90)
    })
    
    extend_input_model = api.model('ExtendInput', {
        'additional_days': fields.Integer(required=True, description='Additional days to extend', min=1, max=30)
    })
    
    # Response models
    success_response_model = api.model('SuccessResponse', {
        'success': fields.Boolean(description='Operation success status'),
        'message': fields.String(description='Response message'),
        'data': fields.Raw(description='Response data')
    })
    
    error_response_model = api.model('ErrorResponse', {
        'success': fields.Boolean(description='Operation success status'),
        'message': fields.String(description='Error message'),
        'data': fields.Raw(description='Error details')
    })
    
    return {
        'book_model': book_model,
        'book_input_model': book_input_model,
        'borrow_model': borrow_model,
        'borrow_input_model': borrow_input_model,
        'extend_input_model': extend_input_model,
        'success_response_model': success_response_model,
        'error_response_model': error_response_model
    }