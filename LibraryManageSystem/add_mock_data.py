#!/usr/bin/env python3
"""
Mock Data Generator for Library Management System

This script adds realistic sample data to the library database including:
- Popular books from various genres
- Sample borrowing records with different statuses
- Mix of available and borrowed books
- Historical and current borrowing activities
"""

from app import app, db, Book, BorrowRecord
from datetime import datetime, timedelta
import random

def add_mock_books():
    """Add a diverse collection of books to the library"""
    books_data = [
        # Fiction Classics
        {
            'title': 'To Kill a Mockingbird',
            'author': 'Harper Lee',
            'isbn': '9780061120084',
            'available': True,
            'created_at': datetime.utcnow() - timedelta(days=365)
        },
        {
            'title': '1984',
            'author': 'George Orwell',
            'isbn': '9780451524935',
            'available': False,  # Currently borrowed
            'created_at': datetime.utcnow() - timedelta(days=300)
        },
        {
            'title': 'Pride and Prejudice',
            'author': 'Jane Austen',
            'isbn': '9780141439518',
            'available': True,
            'created_at': datetime.utcnow() - timedelta(days=280)
        },
        {
            'title': 'The Great Gatsby',
            'author': 'F. Scott Fitzgerald',
            'isbn': '9780743273565',
            'available': True,
            'created_at': datetime.utcnow() - timedelta(days=250)
        },
        
        # Science Fiction
        {
            'title': 'Dune',
            'author': 'Frank Herbert',
            'isbn': '9780441172719',
            'available': False,  # Currently borrowed
            'created_at': datetime.utcnow() - timedelta(days=200)
        },
        {
            'title': 'The Hitchhiker\'s Guide to the Galaxy',
            'author': 'Douglas Adams',
            'isbn': '9780345391803',
            'available': True,
            'created_at': datetime.utcnow() - timedelta(days=180)
        },
        {
            'title': 'Foundation',
            'author': 'Isaac Asimov',
            'isbn': '9780553293357',
            'available': True,
            'created_at': datetime.utcnow() - timedelta(days=150)
        },
        
        # Fantasy
        {
            'title': 'The Lord of the Rings',
            'author': 'J.R.R. Tolkien',
            'isbn': '9780544003415',
            'available': True,
            'created_at': datetime.utcnow() - timedelta(days=320)
        },
        {
            'title': 'Harry Potter and the Philosopher\'s Stone',
            'author': 'J.K. Rowling',
            'isbn': '9780747532699',
            'available': False,  # Currently borrowed
            'created_at': datetime.utcnow() - timedelta(days=100)
        },
        
        # Non-Fiction
        {
            'title': 'Sapiens',
            'author': 'Yuval Noah Harari',
            'isbn': '9780062316097',
            'available': True,
            'created_at': datetime.utcnow() - timedelta(days=90)
        },
        {
            'title': 'Educated',
            'author': 'Tara Westover',
            'isbn': '9780399590504',
            'available': True,
            'created_at': datetime.utcnow() - timedelta(days=60)
        },
        {
            'title': 'The Power of Habit',
            'author': 'Charles Duhigg',
            'isbn': '9781400069286',
            'available': False,  # Currently borrowed
            'created_at': datetime.utcnow() - timedelta(days=45)
        },
        
        # Programming Books
        {
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'isbn': '9780132350884',
            'available': True,
            'created_at': datetime.utcnow() - timedelta(days=30)
        },
        {
            'title': 'Python Crash Course',
            'author': 'Eric Matthes',
            'isbn': '9781593279288',
            'available': True,
            'created_at': datetime.utcnow() - timedelta(days=15)
        },
        {
            'title': 'The Pragmatic Programmer',
            'author': 'David Thomas',
            'isbn': '9780201616224',
            'available': False,  # Currently borrowed
            'created_at': datetime.utcnow() - timedelta(days=10)
        },
        
        # Recently Added
        {
            'title': 'The Seven Husbands of Evelyn Hugo',
            'author': 'Taylor Jenkins Reid',
            'isbn': '9781501161933',
            'available': True,
            'created_at': datetime.utcnow() - timedelta(days=5)
        }
    ]
    
    books = []
    for book_data in books_data:
        # Check if book already exists (avoid duplicates on reruns)
        existing_book = Book.query.filter_by(isbn=book_data['isbn']).first()
        if not existing_book:
            book = Book(**book_data)
            books.append(book)
            db.session.add(book)
    
    db.session.commit()
    print(f"Added {len(books)} books to the library")
    return books

def add_mock_borrow_records():
    """Add sample borrowing records with various scenarios"""
    
    # Get all books that should be marked as borrowed
    borrowed_books = Book.query.filter_by(available=False).all()
    
    borrowers_data = [
        ('Alice Johnson', 'alice.johnson@email.com'),
        ('Bob Smith', 'bob.smith@email.com'),
        ('Carol Davis', 'carol.davis@email.com'),
        ('David Wilson', 'david.wilson@email.com'),
        ('Emma Brown', 'emma.brown@email.com'),
        ('Frank Miller', 'frank.miller@email.com'),
        ('Grace Taylor', 'grace.taylor@email.com'),
        ('Henry Anderson', 'henry.anderson@email.com'),
        ('Ivy Chen', 'ivy.chen@email.com'),
        ('Jack Thompson', 'jack.thompson@email.com')
    ]
    
    records = []
    
    # Create current borrowing records for books marked as unavailable
    for i, book in enumerate(borrowed_books):
        if i < len(borrowers_data):
            borrower_name, borrower_email = borrowers_data[i]
            
            # Random borrow date in the last 30 days
            borrow_days_ago = random.randint(1, 30)
            borrow_date = datetime.utcnow() - timedelta(days=borrow_days_ago)
            
            # Due date is typically 14-21 days after borrow date
            loan_period = random.randint(14, 21)
            due_date = borrow_date + timedelta(days=loan_period)
            
            record = BorrowRecord(
                book_id=book.id,
                borrower_name=borrower_name,
                borrower_email=borrower_email,
                borrow_date=borrow_date,
                due_date=due_date,
                returned=False
            )
            records.append(record)
            db.session.add(record)
    
    # Add some historical records (returned books)
    available_books = Book.query.filter_by(available=True).all()
    
    # Create 8-10 historical records
    for i in range(min(8, len(available_books))):
        book = available_books[i]
        borrower_name, borrower_email = random.choice(borrowers_data)
        
        # Historical borrow date (30-90 days ago)
        borrow_days_ago = random.randint(30, 90)
        borrow_date = datetime.utcnow() - timedelta(days=borrow_days_ago)
        
        # Loan period
        loan_period = random.randint(7, 21)
        due_date = borrow_date + timedelta(days=loan_period)
        
        # Return date (could be on time, early, or late)
        return_variation = random.randint(-3, 7)  # -3 days early to 7 days late
        return_date = due_date + timedelta(days=return_variation)
        
        record = BorrowRecord(
            book_id=book.id,
            borrower_name=borrower_name,
            borrower_email=borrower_email,
            borrow_date=borrow_date,
            due_date=due_date,
            return_date=return_date,
            returned=True
        )
        records.append(record)
        db.session.add(record)
    
    db.session.commit()
    print(f"Added {len(records)} borrowing records")
    return records

def main():
    """Main function to populate the database with mock data"""
    print("Starting mock data generation...")
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Clear existing data (optional - uncomment if you want to reset)
        # print("Clearing existing data...")
        # BorrowRecord.query.delete()
        # Book.query.delete()
        # db.session.commit()
        
        # Add mock data
        books = add_mock_books()
        records = add_mock_borrow_records()
        
        # Print summary
        total_books = Book.query.count()
        total_records = BorrowRecord.query.count()
        available_books = Book.query.filter_by(available=True).count()
        borrowed_books = Book.query.filter_by(available=False).count()
        current_borrows = BorrowRecord.query.filter_by(returned=False).count()
        
        print("\n" + "="*50)
        print("MOCK DATA GENERATION COMPLETE")
        print("="*50)
        print(f"Total books in library: {total_books}")
        print(f"Available books: {available_books}")
        print(f"Currently borrowed books: {borrowed_books}")
        print(f"Total borrowing records: {total_records}")
        print(f"Current active borrows: {current_borrows}")
        print("="*50)
        print("\nYou can now start the Flask application with: python app.py")
        print("Visit http://127.0.0.1:5000 to see the library management system with mock data!")

if __name__ == '__main__':
    main()