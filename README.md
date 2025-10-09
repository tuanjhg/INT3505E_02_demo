# Library Management System

A comprehensive Flask-based library management system that demonstrates RESTful architecture principles and allows you to manage books and track borrowing activities.

![Library Management System](https://github.com/user-attachments/assets/3c2836a3-3524-4601-b40a-5dbf0429d252)

## 🎓 NEW: RESTful Architecture Educational Module

This repository now includes a complete educational module demonstrating the **six constraints of RESTful architecture**! Each constraint is implemented in a separate, runnable example with comprehensive documentation.

📂 **See**: [`LibraryManagementSystem/`](./LibraryManagementSystem/) folder for the complete RESTful architecture demonstration.

### Six RESTful Constraints Demonstrated:

1. **Client-Server**: Separation of concerns between UI and data storage
2. **Stateless**: Each request contains all needed information
3. **Cacheable**: Responses explicitly marked as cacheable or not
4. **Layered System**: Hierarchical architecture with clear responsibilities
5. **Uniform Interface**: Standard HTTP methods, URIs, and HATEOAS
6. **Code-On-Demand** (Optional): Server sends executable code to client

👉 **[Explore the RESTful Architecture Demo →](./LibraryManagementSystem/README.md)**

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

3. (Optional) Add mock data to the library:
```bash
python3 add_mock_data.py
```

4. Run the application:
```bash
python3 app.py
```

5. Open your web browser and navigate to `http://127.0.0.1:5000`

## Mock Data

The repository includes a mock data generator (`add_mock_data.py`) that populates the library with:

- **16 diverse books** across multiple genres (Fiction, Science Fiction, Fantasy, Non-Fiction, Programming)
- **Sample borrowing records** with various statuses (current loans, overdue books, returned books)
- **Realistic borrower information** with different borrowing patterns
- **Historical data** showing on-time and late returns

The mock data demonstrates all system features including:
- Book availability tracking
- Overdue detection
- Borrowing history with status indicators
- Mixed scenarios for testing functionality

To reset the database and add fresh mock data, simply delete the `instance/library.db` file and run the mock data script again.

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



## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with Flask-SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with responsive design
- **API Documentation**: Flask-RESTX with Swagger UI
- **RESTful Demo**: Complete implementation of all 6 REST constraints

## Project Structure

```
INT3505E_02_demo/
├── LibraryManagementSystem/    # 🎓 RESTful Architecture Educational Module
│   ├── client-server/          # Constraint 1: Client-Server
│   ├── stateless/              # Constraint 2: Stateless
│   ├── cacheable/              # Constraint 3: Cacheable
│   ├── layered/                # Constraint 4: Layered System
│   ├── uniform-interface/      # Constraint 5: Uniform Interface
│   └── code-on-demand/         # Constraint 6: Code-On-Demand (Optional)
├── app.py                      # Main application (original)
├── app_swagger.py              # Application with Swagger/OpenAPI
├── models/                     # Database models
├── routes/                     # API and web routes
├── services/                   # Business logic layer
├── templates/                  # HTML templates
└── utils/                      # Helper utilities
```
