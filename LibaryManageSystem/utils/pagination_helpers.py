"""
Pagination utilities for Library Management System
"""
from flask import request, url_for
from sqlalchemy import func
import math

class PaginationHelper:
    """Helper class for handling pagination"""
    
    ALLOWED_PAGE_SIZES = [5, 10, 15]  # Allowed page sizes
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 15
    
    @staticmethod
    def get_pagination_params():
        """Extract and validate pagination parameters from request"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', PaginationHelper.DEFAULT_PAGE_SIZE, type=int)
        
        # Validate page number
        if page < 1:
            page = 1
            
        # Validate page size
        if per_page not in PaginationHelper.ALLOWED_PAGE_SIZES:
            per_page = PaginationHelper.DEFAULT_PAGE_SIZE
            
        return page, per_page
    
    @staticmethod
    def get_search_params():
        """Extract search parameters from request (simplified)"""
        return {
            'search': request.args.get('search', '').strip(),
            'available_only': request.args.get('available_only', 'false').lower() == 'true'
        }
    
    @staticmethod
    def paginate_query(query, page, per_page):
        """Apply pagination to SQLAlchemy query"""
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': math.ceil(total / per_page) if total > 0 else 0,
            'has_prev': page > 1,
            'has_next': page * per_page < total,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page * per_page < total else None
        }
    
    @staticmethod
    def build_pagination_response(paginated_data, endpoint='api.books_book_list'):
        """Build standardized pagination response"""
        pagination_info = {
            'page': paginated_data['page'],
            'per_page': paginated_data['per_page'],
            'total': paginated_data['total'],
            'pages': paginated_data['pages'],
            'has_prev': paginated_data['has_prev'],
            'has_next': paginated_data['has_next'],
            'prev_page': paginated_data['prev_page'],
            'next_page': paginated_data['next_page']
        }
        
        # Add navigation URLs if Flask context is available
        try:
            current_args = dict(request.args)
            
            if pagination_info['has_prev']:
                current_args['page'] = pagination_info['prev_page']
                pagination_info['prev_url'] = url_for(endpoint, **current_args, _external=True)
            
            if pagination_info['has_next']:
                current_args['page'] = pagination_info['next_page']
                pagination_info['next_url'] = url_for(endpoint, **current_args, _external=True)
                
            current_args['page'] = pagination_info['page']
            pagination_info['current_url'] = url_for(endpoint, **current_args, _external=True)
            
        except RuntimeError:
            # Outside of request context, skip URL generation
            pass
        
        return pagination_info


class SearchFilter:
    """Helper class for building search filters"""
    
    @staticmethod
    def apply_book_filters(query, search_params):
        """Apply search filters to book query (simplified)"""
        from models.book import Book
        
        # Text search in title and author
        if search_params.get('search'):
            search_term = f"%{search_params['search']}%"
            query = query.filter(
                (Book.title.ilike(search_term)) | 
                (Book.author.ilike(search_term))
            )
        
        # Availability filter
        if search_params.get('available_only'):
            query = query.filter(Book.available == True)
        
        # Default sort by creation date (newest first)
        query = query.order_by(Book.created_at.desc())
        
        return query
    
    @staticmethod
    def apply_borrow_filters(query, search_params):
        """Apply search filters to borrow query (simplified)"""
        from models.borrow import BorrowRecord
        
        # Search in borrower name and email
        if search_params.get('search'):
            search_term = f"%{search_params['search']}%"
            query = query.filter(
                (BorrowRecord.borrower_name.ilike(search_term)) |
                (BorrowRecord.borrower_email.ilike(search_term))
            )
        
        # Status filter
        if search_params.get('status'):
            if search_params['status'] == 'overdue':
                from datetime import datetime
                query = query.filter(
                    BorrowRecord.returned == False,
                    BorrowRecord.due_date < datetime.utcnow()
                )
            elif search_params['status'] == 'borrowed':
                query = query.filter(BorrowRecord.returned == False)
            elif search_params['status'] == 'returned':
                query = query.filter(BorrowRecord.returned == True)
        
        # Default sort by borrow date (newest first)
        query = query.order_by(BorrowRecord.borrow_date.desc())
        
        return query