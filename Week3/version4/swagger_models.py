"""
Swagger Models for Library Management API Version 4
"""

from flask_restx import fields

def create_swagger_models(api):
    """Create Swagger models for API documentation"""
    
    # Book models
    book_model = api.model('Book', {
        'id': fields.Integer(readonly=True, description='Book ID', example=1),
        'title': fields.String(description='Book title', example='REST in Practice'),
        'author': fields.String(description='Book author', example='Jim Webber'),
        'isbn': fields.String(description='ISBN number', example='0596805829'),
        'available': fields.Boolean(description='Availability status', example=True),
        'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
        '_links': fields.Raw(description='HATEOAS navigation links')
    })

    book_input_model = api.model('BookInput', {
        'title': fields.String(required=True, description='Book title', example='REST in Practice'),
        'author': fields.String(required=True, description='Book author', example='Jim Webber'),
        'isbn': fields.String(required=True, description='ISBN number (unique)', example='0596805829')
    })

    book_update_model = api.model('BookUpdate', {
        'title': fields.String(description='Book title', example='Updated Title'),
        'author': fields.String(description='Book author', example='Updated Author'),
        'available': fields.Boolean(description='Availability status', example=False)
    })

    # Authentication models
    auth_request_model = api.model('AuthRequest', {
        'email': fields.String(required=True, description='Valid email address', example='user@example.com')
    })

    auth_response_model = api.model('AuthResponse', {
        'success': fields.Boolean(description='Operation success', example=True),
        'data': fields.Nested(api.model('AuthData', {
            'api_key': fields.String(description='API key for authentication'),
            'email': fields.String(description='User email'),
            'instructions': fields.String(description='Usage instructions')
        })),
        'message': fields.String(description='Response message')
    })

    # Response models
    success_response_model = api.model('SuccessResponse', {
        'success': fields.Boolean(description='Operation success', example=True),
        'data': fields.Raw(description='Response data'),
        'message': fields.String(description='Success message'),
        'authenticated_user': fields.String(description='User who made the request'),
        '_links': fields.Raw(description='HATEOAS navigation links')
    })

    error_response_model = api.model('ErrorResponse', {
        'success': fields.Boolean(description='Operation success', example=False),
        'error': fields.Nested(api.model('ErrorDetails', {
            'code': fields.String(description='Error code', example='BOOK_NOT_FOUND'),
            'message': fields.String(description='Error message', example='Book not found')
        })),
        '_links': fields.Raw(description='HATEOAS navigation links')
    })

    # Statistics model
    stats_model = api.model('Statistics', {
        'success': fields.Boolean(description='Operation success', example=True),
        'data': fields.Nested(api.model('StatsData', {
            'total_books': fields.Integer(description='Total number of books', example=10),
            'available_books': fields.Integer(description='Available books', example=8),
            'borrowed_books': fields.Integer(description='Borrowed books', example=2),
            'timestamp': fields.String(description='Statistics timestamp')
        })),
        'message': fields.String(description='Response message'),
        'requested_by': fields.String(description='User who requested stats'),
        '_links': fields.Raw(description='HATEOAS navigation links')
    })

    # Cache model
    cache_status_model = api.model('CacheStatus', {
        'success': fields.Boolean(description='Operation success', example=True),
        'data': fields.Nested(api.model('CacheData', {
            'cached_items': fields.Integer(description='Number of cached items', example=5),
            'cache_keys': fields.List(fields.String, description='Cache keys')
        })),
        'note': fields.String(description='Cache information')
    })

    # Health check model
    health_model = api.model('Health', {
        'status': fields.String(description='Health status', example='healthy'),
        'service': fields.String(description='Service name', example='Library Management Server'),
        'version': fields.String(description='Service version', example='4.0 - Simple Stateless'),
        'features': fields.List(fields.String, description='Available features'),
        'authentication': fields.String(description='Authentication info')
    })

    return {
        'book': book_model,
        'book_input': book_input_model,
        'book_update': book_update_model,
        'auth_request': auth_request_model,
        'auth_response': auth_response_model,
        'success_response': success_response_model,
        'error_response': error_response_model,
        'stats': stats_model,
        'cache_status': cache_status_model,
        'health': health_model
    }