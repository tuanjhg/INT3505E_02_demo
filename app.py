from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    available = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Book {self.title}>'

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

# Routes
@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/books')
def books():
    books = Book.query.all()
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        
        if Book.query.filter_by(isbn=isbn).first():
            flash('Book with this ISBN already exists!', 'error')
            return render_template('add_book.html')
        
        book = Book(title=title, author=author, isbn=isbn)
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('books'))
    
    return render_template('add_book.html')

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.isbn = request.form['isbn']
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books'))
    
    return render_template('edit_book.html', book=book)

@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if not book.available:
        flash('Cannot delete book that is currently borrowed!', 'error')
        return redirect(url_for('books'))
    
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books'))

@app.route('/borrow_book/<int:book_id>', methods=['GET', 'POST'])
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if not book.available:
        flash('This book is not available for borrowing!', 'error')
        return redirect(url_for('books'))
    
    if request.method == 'POST':
        borrower_name = request.form['borrower_name']
        borrower_email = request.form['borrower_email']
        days = int(request.form.get('days', 14))
        
        due_date = datetime.utcnow() + timedelta(days=days)
        
        borrow_record = BorrowRecord(
            book_id=book_id,
            borrower_name=borrower_name,
            borrower_email=borrower_email,
            due_date=due_date
        )
        
        book.available = False
        db.session.add(borrow_record)
        db.session.commit()
        
        flash(f'Book borrowed successfully! Due date: {due_date.strftime("%Y-%m-%d")}', 'success')
        return redirect(url_for('borrowed_books'))
    
    return render_template('borrow_book.html', book=book)

@app.route('/borrowed_books')
def borrowed_books():
    records = BorrowRecord.query.filter_by(returned=False).all()
    return render_template('borrowed_books.html', records=records, today=datetime.utcnow())

@app.route('/return_book/<int:record_id>')
def return_book(record_id):
    record = BorrowRecord.query.get_or_404(record_id)
    
    if record.returned:
        flash('This book has already been returned!', 'error')
        return redirect(url_for('borrowed_books'))
    
    record.returned = True
    record.return_date = datetime.utcnow()
    record.book.available = True
    
    db.session.commit()
    flash('Book returned successfully!', 'success')
    return redirect(url_for('borrowed_books'))

@app.route('/history')
def history():
    records = BorrowRecord.query.all()
    return render_template('history.html', records=records, today=datetime.utcnow())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)