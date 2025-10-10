"""
Swagger-enhanced routes for Library Management API Version 4
"""

from flask import request, jsonify, url_for
from flask_restx import Resource, Namespace
from functools import wraps
import base64
import time
from datetime import datetime

def create_swagger_routes(api, db, Book, cache, clear_cache):
    """Create Swagger-documented API routes"""
    
    # Import swagger models
    from swagger_models import create_swagger_models
    models = create_swagger_models(api)
    
    # Authentication function
    def get_user_from_token(api_key):
        """Extract user info from API key"""
        try:
            email = base64.b64decode(api_key).decode('utf-8')
            if '@' in email:
                return email
            return None
        except:
            return None

    def require_auth(f):
        """Decorator requiring authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                return {
                    'success': False,
                    'error': {
                        'code': 'MISSING_AUTHORIZATION',
                        'message': 'Authorization header required: Bearer <api_key>'
                    },
                    '_links': {
                        'get_api_key': {
                            'href': url_for('auth_get_api_key', _external=True),
                            'method': 'POST',
                            'description': 'Get API key for authentication'
                        }
                    }
                }, 401
            
            api_key = auth_header.replace('Bearer ', '')
            user_email = get_user_from_token(api_key)
            
            if not user_email:
                return {
                    'success': False,
                    'error': {
                        'code': 'INVALID_API_KEY',
                        'message': 'Invalid API key'
                    }
                }, 401
            
            kwargs['user_email'] = user_email
            return f(*args, **kwargs)
        
        decorated_function.__name__ = f.__name__
        return decorated_function

    # Create namespaces
    auth_ns = api.namespace('auth', description='Authentication operations')
    books_ns = api.namespace('books', description='Book management operations')
    admin_ns = api.namespace('admin', description='Administrative operations')

    # Authentication Routes
    @auth_ns.route('')
    class Authentication(Resource):
        @auth_ns.doc('get_api_key')
        @auth_ns.expect(models['auth_request'], validate=True)
        @auth_ns.marshal_with(models['auth_response'], code=201)
        @auth_ns.response(400, 'Bad Request', models['error_response'])
        def post(self):
            """
            Get API key for authentication
            
            Generate an API key using your email address.
            Use this key in the Authorization header for authenticated endpoints.
            """
            data = request.get_json()
            
            if not data or 'email' not in data:
                return {
                    'success': False,
                    'error': {
                        'code': 'MISSING_EMAIL',
                        'message': 'Email required to generate API key'
                    }
                }, 400
            
            email = data['email']
            
            if '@' not in email:
                return {
                    'success': False,
                    'error': {
                        'code': 'INVALID_EMAIL',
                        'message': 'Valid email address required'
                    }
                }, 400
            
            api_key = base64.b64encode(email.encode('utf-8')).decode('utf-8')
            
            return {
                'success': True,
                'data': {
                    'api_key': api_key,
                    'email': email,
                    'instructions': 'Include in Authorization header: Bearer <api_key>'
                },
                'message': 'API key generated successfully'
            }, 201

    # Book Management Routes
    @books_ns.route('')
    class BookList(Resource):
        @books_ns.doc('get_books', security='Bearer')
        @books_ns.marshal_with(models['success_response'])
        @books_ns.response(401, 'Unauthorized', models['error_response'])
        @books_ns.response(500, 'Internal Server Error', models['error_response'])
        @require_auth
        def get(self, user_email):
            """
            Get all books
            
            Retrieve all books from the library with caching support.
            Returns HATEOAS links for navigation.
            """
            cache_key = 'all_books'
            
            if cache_key in cache:
                print(f"[CACHE] HIT - returning books from cache for {user_email}")
                data = cache[cache_key].copy()
                data['authenticated_user'] = user_email
                response = jsonify(data)
                response.headers['Cache-Control'] = 'max-age=300'
                response.headers['X-Cache-Status'] = 'HIT'
                return response
            
            print(f"[CACHE] MISS - getting books from database for {user_email}")
            books = Book.query.all()
            
            data = {
                'success': True,
                'data': [book.to_dict() for book in books],
                'count': len(books),
                'message': f'Found {len(books)} books',
                'authenticated_user': user_email,
                '_links': {
                    'self': {
                        'href': url_for('books_book_list', _external=True),
                        'method': 'GET'
                    },
                    'create': {
                        'href': url_for('books_book_list', _external=True),
                        'method': 'POST'
                    }
                }
            }
            
            cache[cache_key] = data
            
            response = jsonify(data)
            response.headers['Cache-Control'] = 'max-age=300'
            response.headers['X-Cache-Status'] = 'MISS'
            return response
        
        @books_ns.doc('create_book', security='Bearer')
        @books_ns.expect(models['book_input'], validate=True)
        @books_ns.marshal_with(models['success_response'], code=201)
        @books_ns.response(400, 'Bad Request', models['error_response'])
        @books_ns.response(401, 'Unauthorized', models['error_response'])
        @require_auth
        def post(self, user_email):
            """
            Create a new book
            
            Add a new book to the library. ISBN must be unique.
            """
            data = request.get_json()
            
            if not data:
                return {
                    'success': False,
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'Request body must be JSON'
                    }
                }, 400
            
            required = ['title', 'author', 'isbn']
            missing = [f for f in required if f not in data]
            
            if missing:
                return {
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELDS',
                        'message': f'Missing required fields: {", ".join(missing)}',
                        'required_fields': required
                    }
                }, 400
            
            existing_book = Book.query.filter_by(isbn=data['isbn']).first()
            if existing_book:
                return {
                    'success': False,
                    'error': {
                        'code': 'DUPLICATE_ISBN',
                        'message': 'Book with this ISBN already exists'
                    }
                }, 400
            
            book = Book(
                title=data['title'],
                author=data['author'],
                isbn=data['isbn']
            )
            
            db.session.add(book)
            db.session.commit()
            
            clear_cache()
            
            response_data = {
                'success': True,
                'data': book.to_dict(),
                'message': 'Book created successfully',
                'created_by': user_email
            }
            
            response = jsonify(response_data)
            response.headers['Cache-Control'] = 'no-cache'
            response.headers['Location'] = url_for('books_book_detail', book_id=book.id, _external=True)
            return response, 201

    @books_ns.route('/<int:book_id>')
    @books_ns.param('book_id', 'Book identifier')
    class BookDetail(Resource):
        @books_ns.doc('get_book', security='Bearer')
        @books_ns.marshal_with(models['success_response'])
        @books_ns.response(401, 'Unauthorized', models['error_response'])
        @books_ns.response(404, 'Book not found', models['error_response'])
        @require_auth
        def get(self, user_email, book_id):
            """
            Get a specific book
            
            Retrieve detailed information about a specific book by ID.
            """
            cache_key = f'book_{book_id}'
            
            if cache_key in cache:
                print(f"[CACHE] HIT - book {book_id} from cache for {user_email}")
                data = cache[cache_key].copy()
                data['authenticated_user'] = user_email
                response = jsonify(data)
                response.headers['Cache-Control'] = 'max-age=600'
                response.headers['X-Cache-Status'] = 'HIT'
                return response
            
            print(f"[CACHE] MISS - getting book {book_id} from database for {user_email}")
            book = Book.query.get(book_id)
            
            if not book:
                return {
                    'success': False,
                    'error': {
                        'code': 'BOOK_NOT_FOUND',
                        'message': f'Book with ID {book_id} not found'
                    },
                    '_links': {
                        'books': {
                            'href': url_for('books_book_list', _external=True),
                            'description': 'View all books'
                        }
                    }
                }, 404
            
            data = {
                'success': True,
                'data': book.to_dict(),
                'authenticated_user': user_email
            }
            
            cache[cache_key] = data
            
            response = jsonify(data)
            response.headers['Cache-Control'] = 'max-age=600'
            response.headers['X-Cache-Status'] = 'MISS'
            return response
        
        @books_ns.doc('update_book', security='Bearer')
        @books_ns.expect(models['book_update'], validate=True)
        @books_ns.marshal_with(models['success_response'])
        @books_ns.response(400, 'Bad Request', models['error_response'])
        @books_ns.response(401, 'Unauthorized', models['error_response'])
        @books_ns.response(404, 'Book not found', models['error_response'])
        @require_auth
        def put(self, user_email, book_id):
            """
            Update a specific book
            
            Update book information. All fields are optional.
            """
            book = Book.query.get(book_id)
            
            if not book:
                return {
                    'success': False,
                    'error': {
                        'code': 'BOOK_NOT_FOUND',
                        'message': f'Book with ID {book_id} not found'
                    }
                }, 404
            
            data = request.get_json()
            
            if not data:
                return {
                    'success': False,
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'Request body must be JSON'
                    }
                }, 400
            
            if 'title' in data:
                book.title = data['title']
            if 'author' in data:
                book.author = data['author']
            if 'available' in data:
                book.available = data['available']
            
            db.session.commit()
            clear_cache()
            
            response_data = {
                'success': True,
                'data': book.to_dict(),
                'message': 'Book updated successfully',
                'updated_by': user_email
            }
            
            response = jsonify(response_data)
            response.headers['Cache-Control'] = 'no-cache'
            return response
        
        @books_ns.doc('delete_book', security='Bearer')
        @books_ns.response(204, 'Book deleted successfully')
        @books_ns.response(401, 'Unauthorized', models['error_response'])
        @books_ns.response(404, 'Book not found', models['error_response'])
        @require_auth
        def delete(self, user_email, book_id):
            """
            Delete a specific book
            
            Remove a book from the library permanently.
            """
            book = Book.query.get(book_id)
            
            if not book:
                return {
                    'success': False,
                    'error': {
                        'code': 'BOOK_NOT_FOUND',
                        'message': f'Book with ID {book_id} not found'
                    }
                }, 404
            
            print(f"[DELETE] Book {book_id} deleted by {user_email}")
            db.session.delete(book)
            db.session.commit()
            clear_cache()
            
            return '', 204

    # Administrative Routes
    @admin_ns.route('/stats')
    class Statistics(Resource):
        @admin_ns.doc('get_stats', security='Bearer')
        @admin_ns.marshal_with(models['stats'])
        @admin_ns.response(401, 'Unauthorized', models['error_response'])
        @require_auth
        def get(self, user_email):
            """
            Get real-time statistics
            
            Get current library statistics. This data is never cached.
            """
            total = Book.query.count()
            available = Book.query.filter_by(available=True).count()
            borrowed = total - available
            
            response_data = {
                'success': True,
                'data': {
                    'total_books': total,
                    'available_books': available,
                    'borrowed_books': borrowed,
                    'timestamp': datetime.utcnow().isoformat()
                },
                'message': 'Real-time statistics (never cached)',
                'requested_by': user_email,
                '_links': {
                    'books': {
                        'href': url_for('books_book_list', _external=True),
                        'description': 'View all books'
                    }
                }
            }
            
            response = jsonify(response_data)
            response.headers['Cache-Control'] = 'no-store'
            return response

    @admin_ns.route('/cache/status')
    class CacheStatus(Resource):
        @admin_ns.doc('cache_status')
        @admin_ns.marshal_with(models['cache_status'])
        def get(self):
            """
            Get cache status
            
            Show current cache information including cached items and keys.
            """
            return {
                'success': True,
                'data': {
                    'cached_items': len(cache),
                    'cache_keys': list(cache.keys())
                },
                'note': 'Cache is shared across all authenticated users'
            }

    @admin_ns.route('/cache/clear')
    class CacheClear(Resource):
        @admin_ns.doc('clear_cache')
        @admin_ns.marshal_with(models['success_response'])
        def post(self):
            """
            Clear cache
            
            Clear all cached data from the server.
            """
            clear_cache()
            return {
                'success': True,
                'message': 'Cache cleared successfully'
            }

    return auth_ns, books_ns, admin_ns