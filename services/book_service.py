from models import db
from models.book import Book
from sqlalchemy.exc import IntegrityError

class BookService:
    @staticmethod
    def get_all_books():
        """Get all books"""
        return Book.query.all()
    
    @staticmethod
    def get_book_by_id(book_id):
        """Get book by ID"""
        return Book.query.get(book_id)
    
    @staticmethod
    def get_book_by_isbn(isbn):
        """Get book by ISBN"""
        return Book.query.filter_by(isbn=isbn).first()
    
    @staticmethod
    def create_book(data):
        """Create a new book"""
        # Check if book with this ISBN already exists
        existing_book = BookService.get_book_by_isbn(data.get('isbn'))
        if existing_book:
            raise ValueError("Book with this ISBN already exists")
        
        book = Book.from_dict(data)
        db.session.add(book)
        try:
            db.session.commit()
            return book
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Book with this ISBN already exists")
    
    @staticmethod
    def update_book(book_id, data):
        """Update an existing book"""
        book = BookService.get_book_by_id(book_id)
        if not book:
            raise ValueError("Book not found")
        
        # Check if updating ISBN conflicts with existing book
        if 'isbn' in data and data['isbn'] != book.isbn:
            existing_book = BookService.get_book_by_isbn(data['isbn'])
            if existing_book:
                raise ValueError("Book with this ISBN already exists")
        
        # Update book fields
        for key, value in data.items():
            if hasattr(book, key):
                setattr(book, key, value)
        
        try:
            db.session.commit()
            return book
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Book with this ISBN already exists")
    
    @staticmethod
    def delete_book(book_id):
        """Delete a book"""
        book = BookService.get_book_by_id(book_id)
        if not book:
            raise ValueError("Book not found")
        
        if not book.available:
            raise ValueError("Cannot delete book that is currently borrowed")
        
        db.session.delete(book)
        db.session.commit()
        return True
    
    @staticmethod
    def get_available_books():
        """Get all available books"""
        return Book.query.filter_by(available=True).all()
    
    @staticmethod
    def search_books(query):
        """Search books by title or author"""
        return Book.query.filter(
            Book.title.contains(query) | Book.author.contains(query)
        ).all()