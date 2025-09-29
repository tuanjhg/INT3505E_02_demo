# Library Management System

A simple Flask-based library management system that allows you to manage books and track borrowing activities.

![Library Management System](https://github.com/user-attachments/assets/3c2836a3-3524-4601-b40a-5dbf0429d252)

## Features

- **Book Management**: Add, edit, delete, and view books
- **Borrowing System**: Borrow books with configurable loan periods (7-30 days)
- **Return System**: Return books with automatic availability update
- **History Tracking**: View complete borrowing history with overdue detection
- **Dashboard**: Quick stats and recently added books overview
- **Responsive Design**: Clean web interface with intuitive navigation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd INT3505E_02_demo
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python3 app.py
```

4. Open your web browser and navigate to `http://127.0.0.1:5000`

## Usage

### Adding Books
1. Click "Add Book" in the navigation menu
2. Fill in the book details (Title, Author, ISBN)
3. Click "Add Book" to save

### Borrowing Books
1. Go to "All Books" to view available books
2. Click "Borrow" next to an available book
3. Enter borrower details (name, email)
4. Select borrowing period (7-30 days)
5. Click "Borrow Book"

### Returning Books
1. Go to "Borrowed Books" to view currently borrowed books
2. Click "Return" next to the book you want to return
3. Confirm the return action

### Viewing History
- Go to "History" to view all borrowing records
- See complete borrowing history with status indicators
- Track overdue books and return patterns

## Database

The system uses SQLite database which is automatically created when you first run the application. The database file is stored in the `instance/` directory and includes:

- **Books table**: Stores book information (title, author, ISBN, availability status)
- **BorrowRecords table**: Tracks all borrowing activities with dates and borrower information

## File Structure

```
INT3505E_02_demo/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page
│   ├── books.html        # All books listing
│   ├── add_book.html     # Add book form
│   ├── edit_book.html    # Edit book form
│   ├── borrow_book.html  # Borrow book form
│   ├── borrowed_books.html # Currently borrowed books
│   └── history.html      # Borrowing history
├── instance/             # Database directory (auto-created)
└── README.md
```

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with Flask-SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with responsive design

## Contributing

Feel free to submit issues and enhancement requests!