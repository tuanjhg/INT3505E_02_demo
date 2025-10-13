from datetime import datetime, timedelta
from . import db

class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrower_name = db.Column(db.String(100), nullable=False)
    borrower_email = db.Column(db.String(100), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    returned = db.Column(db.Boolean, default=False, nullable=False)
    
    book = db.relationship('Book', backref=db.backref('borrow_records', lazy=True))
    
    def __repr__(self):
        return f'<BorrowRecord {self.borrower_name} - {self.book.title}>'
    
    def to_dict(self):
        """Convert BorrowRecord object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book': self.book.to_dict() if self.book else None,
            'borrower_name': self.borrower_name,
            'borrower_email': self.borrower_email,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'returned': self.returned,
            'is_overdue': self.is_overdue()
        }
    
    def is_overdue(self):
        """Check if the book is overdue"""
        if self.returned:
            return False
        return datetime.utcnow() > self.due_date
    
    @staticmethod
    def from_dict(data):
        """Create BorrowRecord object from dictionary"""
        due_date = datetime.utcnow() + timedelta(days=data.get('days', 14))
        return BorrowRecord(
            book_id=data.get('book_id'),
            borrower_name=data.get('borrower_name'),
            borrower_email=data.get('borrower_email'),
            due_date=due_date
        )