from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from services.book_service import BookService
from services.borrow_service import BorrowService

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    books = BookService.get_all_books()
    return render_template('index.html', books=books)

@web_bp.route('/books')
def books():
    books = BookService.get_all_books()
    return render_template('books.html', books=books)

@web_bp.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        data = {
            'title': request.form['title'],
            'author': request.form['author'],
            'isbn': request.form['isbn']
        }
        
        try:
            BookService.create_book(data)
            flash('Book added successfully!', 'success')
            return redirect(url_for('web.books'))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('add_book.html')

@web_bp.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = BookService.get_book_by_id(book_id)
    if not book:
        flash('Book not found!', 'error')
        return redirect(url_for('web.books'))
    
    if request.method == 'POST':
        data = {
            'title': request.form['title'],
            'author': request.form['author'],
            'isbn': request.form['isbn']
        }
        
        try:
            BookService.update_book(book_id, data)
            flash('Book updated successfully!', 'success')
            return redirect(url_for('web.books'))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('edit_book.html', book=book)

@web_bp.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    try:
        BookService.delete_book(book_id)
        flash('Book deleted successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('web.books'))

@web_bp.route('/borrow_book/<int:book_id>', methods=['GET', 'POST'])
def borrow_book(book_id):
    book = BookService.get_book_by_id(book_id)
    if not book:
        flash('Book not found!', 'error')
        return redirect(url_for('web.books'))
    
    if not book.available:
        flash('This book is not available for borrowing!', 'error')
        return redirect(url_for('web.books'))
    
    if request.method == 'POST':
        data = {
            'book_id': book_id,
            'borrower_name': request.form['borrower_name'],
            'borrower_email': request.form['borrower_email'],
            'days': int(request.form.get('days', 14))
        }
        
        try:
            record = BorrowService.borrow_book(data)
            flash(f'Book borrowed successfully! Due date: {record.due_date.strftime("%Y-%m-%d")}', 'success')
            return redirect(url_for('web.borrowed_books'))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('borrow_book.html', book=book)

@web_bp.route('/borrowed_books')
def borrowed_books():
    records = BorrowService.get_active_borrows()
    return render_template('borrowed_books.html', records=records, today=datetime.utcnow())

@web_bp.route('/return_book/<int:record_id>')
def return_book(record_id):
    try:
        BorrowService.return_book(record_id)
        flash('Book returned successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('web.borrowed_books'))

@web_bp.route('/history')
def history():
    records = BorrowService.get_all_borrow_records()
    return render_template('history.html', records=records, today=datetime.utcnow())