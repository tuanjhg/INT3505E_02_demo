from datetime import datetime
from models import db
from models.borrow import BorrowRecord
from models.book import Book
from services.book_service import BookService

class BorrowService:
    @staticmethod
    def get_all_borrow_records():
        """Get all borrow records"""
        return BorrowRecord.query.all()
    
    @staticmethod
    def get_borrow_record_by_id(record_id):
        """Get borrow record by ID"""
        return BorrowRecord.query.get(record_id)
    
    @staticmethod
    def get_active_borrows():
        """Get all active (not returned) borrow records"""
        return BorrowRecord.query.filter_by(returned=False).all()
    
    @staticmethod
    def get_overdue_borrows():
        """Get all overdue borrow records"""
        return BorrowRecord.query.filter(
            BorrowRecord.returned == False,
            BorrowRecord.due_date < datetime.utcnow()
        ).all()
    
    @staticmethod
    def get_borrower_history(borrower_email):
        """Get borrow history for a specific borrower"""
        return BorrowRecord.query.filter_by(borrower_email=borrower_email).all()
    
    @staticmethod
    def borrow_book(data):
        """Borrow a book"""
        book_id = data.get('book_id')
        book = BookService.get_book_by_id(book_id)
        
        if not book:
            raise ValueError("Book not found")
        
        if not book.available:
            raise ValueError("Book is not available for borrowing")
        
        # Create borrow record
        borrow_record = BorrowRecord.from_dict(data)
        
        # Mark book as unavailable
        book.available = False
        
        db.session.add(borrow_record)
        db.session.commit()
        
        return borrow_record
    
    @staticmethod
    def return_book(record_id):
        """Return a borrowed book"""
        record = BorrowService.get_borrow_record_by_id(record_id)
        
        if not record:
            raise ValueError("Borrow record not found")
        
        if record.returned:
            raise ValueError("Book has already been returned")
        
        # Mark as returned
        record.returned = True
        record.return_date = datetime.utcnow()
        
        # Mark book as available
        record.book.available = True
        
        db.session.commit()
        
        return record
    
    @staticmethod
    def extend_due_date(record_id, additional_days):
        """Extend the due date of a borrowed book"""
        record = BorrowService.get_borrow_record_by_id(record_id)
        
        if not record:
            raise ValueError("Borrow record not found")
        
        if record.returned:
            raise ValueError("Cannot extend due date for returned book")
        
        from datetime import timedelta
        record.due_date += timedelta(days=additional_days)
        db.session.commit()
        
        return record
    
    @staticmethod
    def search_and_paginate_borrows(search_params, page=1, per_page=10):
        """Search borrow records with pagination and filtering"""
        from utils.pagination_helpers import PaginationHelper, SearchFilter
        
        # Start with base query
        query = BorrowRecord.query
        
        # Apply search filters
        query = SearchFilter.apply_borrow_filters(query, search_params)
        
        # Apply pagination
        paginated_result = PaginationHelper.paginate_query(query, page, per_page)
        
        return paginated_result
    
    @staticmethod
    def get_borrows_paginated(page=1, per_page=10, search=None, status=None):
        """Get paginated borrow records with search and filtering support (simplified)"""
        from utils.pagination_helpers import PaginationHelper, SearchFilter
        
        # Prepare search parameters (simplified)
        search_params = {
            'search': search or '',
            'status': status or ''
        }
        
        # Use the existing search_and_paginate_borrows method
        result = BorrowService.search_and_paginate_borrows(search_params, page, per_page)
        
        return result