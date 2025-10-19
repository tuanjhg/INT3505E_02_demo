from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from services.book_service import BookService
from services.borrow_service import BorrowService
from services.auth_service import AuthService
from utils.auth_middleware import login_required

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
@login_required
def index():
    books = BookService.get_all_books()
    return render_template('index.html', books=books)

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to index
    if 'user_id' in session:
        return redirect(url_for('web.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        user, error = AuthService.authenticate_user(username, password)
        
        if error:
            flash(error, 'error')
            return render_template('login.html')
        
        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session.permanent = True  # Make session permanent
        
        flash('Login successful!', 'success')
        
        # Redirect to next page or index
        next_page = request.args.get('next')
        return redirect(next_page if next_page else url_for('web.index'))
    
    return render_template('login.html')

@web_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in, redirect to index
    if 'user_id' in session:
        return redirect(url_for('web.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        if not username or not email or not password:
            flash('Username, email, and password are required', 'error')
            return render_template('register.html')
        
        user, error = AuthService.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name
        )
        
        if error:
            flash(error, 'error')
            return render_template('register.html')
        
        # Auto-login after registration
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session.permanent = True
        
        flash('Registration successful! Welcome!', 'success')
        return redirect(url_for('web.index'))
    
    return render_template('register.html')

@web_bp.route('/logout')
def logout():
    # Clear session
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('web.login'))

@web_bp.route('/books')
@login_required
def books():
    # Get search and pagination parameters from request (simplified)
    search = request.args.get('search', '').strip()
    available_only = request.args.get('available_only') == 'true'
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Validate per_page values
    if per_page not in [5, 10, 15]:
        per_page = 10
    
    # Get paginated books with search filters (simplified)
    result = BookService.get_books_paginated(
        page=page,
        per_page=per_page,
        search=search,
        available_only=available_only
    )
    
    return render_template('books.html', 
                         books=result['items'],  # Use 'items' from pagination result
                         pagination=result,      # Pass the entire result as pagination
                         search=search,
                         available_only=available_only,
                         per_page=per_page,
                         total_pages=result.get('total_pages', 1),
                         page=result.get('page', page))

@web_bp.route('/add_book', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def delete_book(book_id):
    try:
        BookService.delete_book(book_id)
        flash('Book deleted successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('web.books'))

@web_bp.route('/borrow_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
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
@login_required
def borrowed_books():
    # Get search and pagination parameters from request (simplified)
    search = request.args.get('search', '').strip()
    status = request.args.get('status', 'borrowed')  # Default to active borrows
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Validate per_page values
    if per_page not in [5, 10, 15]:
        per_page = 10
    
    # Check if BorrowService has paginated method, otherwise use the basic method
    try:
        result = BorrowService.get_borrows_paginated(
            page=page,
            per_page=per_page,
            search=search,
            status=status
        )
        return render_template('borrowed_books.html', 
                             records=result['items'],  # Use 'items' from pagination result
                             pagination=result,        # Pass the entire result as pagination
                             search=search,
                             status=status,
                             per_page=per_page,
                             today=datetime.utcnow())
    except (AttributeError, KeyError):
        # Fallback to basic method if paginated method doesn't exist
        records = BorrowService.get_active_borrows()
        return render_template('borrowed_books.html', records=records, today=datetime.utcnow())

@web_bp.route('/return_book/<int:record_id>')
@login_required
def return_book(record_id):
    try:
        BorrowService.return_book(record_id)
        flash('Book returned successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('web.borrowed_books'))

@web_bp.route('/history')
@login_required
def history():
    # Get search and pagination parameters from request (simplified)
    search = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Validate per_page values
    if per_page not in [5, 10, 15]:
        per_page = 10
    
    # Get paginated borrow records (all statuses for history)
    try:
        result = BorrowService.get_borrows_paginated(
            page=page,
            per_page=per_page,
            search=search,
            status=None  # Show all records in history
        )
        return render_template('history.html', 
                             records=result['items'],  # Use 'items' from pagination result
                             pagination=result,        # Pass the entire result as pagination
                             search=search,
                             per_page=per_page,
                             today=datetime.utcnow())
    except (AttributeError, KeyError):
        # Fallback to basic method if paginated method doesn't work properly
        records = BorrowService.get_all_borrow_records()
        return render_template('history.html', records=records, today=datetime.utcnow())