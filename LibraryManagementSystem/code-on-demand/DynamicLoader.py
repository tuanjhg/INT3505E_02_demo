"""
RESTful Constraint: Code-On-Demand (Optional)

This demonstrates the code-on-demand constraint - the only optional constraint in REST.
The server can extend client functionality by transferring executable code.

Examples:
- JavaScript sent to web browsers
- Applets, plugins, scripts
- Dynamic UI components
- Client-side validation logic

Key Benefits:
- Reduces client complexity
- Server can push updates to client logic
- Improves extensibility
- Reduces need for pre-implementation of features

Note: This is OPTIONAL - many REST APIs don't use it.
"""

from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_cod.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    available = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'available': self.available
        }

# ============================================================================
# EXAMPLE 1: Server sends JavaScript for client-side validation
# ============================================================================

@app.route('/api/validation/isbn.js', methods=['GET'])
def get_isbn_validator():
    """
    CODE-ON-DEMAND: Server sends JavaScript validation logic
    Client executes this code for ISBN validation
    Server can update validation rules without client updates
    """
    javascript_code = """
// ISBN Validation Logic - Delivered On-Demand from Server
// Server can update this logic without client changes

function validateISBN(isbn) {
    // Remove hyphens and spaces
    isbn = isbn.replace(/[-\\s]/g, '');
    
    // Check length
    if (isbn.length !== 10 && isbn.length !== 13) {
        return {
            valid: false,
            message: 'ISBN must be 10 or 13 characters'
        };
    }
    
    // Validate ISBN-10
    if (isbn.length === 10) {
        return validateISBN10(isbn);
    }
    
    // Validate ISBN-13
    if (isbn.length === 13) {
        return validateISBN13(isbn);
    }
}

function validateISBN10(isbn) {
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        if (!/\\d/.test(isbn[i])) {
            return { valid: false, message: 'ISBN-10 must contain only digits (except last char can be X)' };
        }
        sum += parseInt(isbn[i]) * (10 - i);
    }
    
    let checkDigit = isbn[9].toUpperCase();
    if (checkDigit === 'X') {
        sum += 10;
    } else if (/\\d/.test(checkDigit)) {
        sum += parseInt(checkDigit);
    } else {
        return { valid: false, message: 'Invalid check digit' };
    }
    
    if (sum % 11 === 0) {
        return { valid: true, message: 'Valid ISBN-10' };
    } else {
        return { valid: false, message: 'Invalid ISBN-10 checksum' };
    }
}

function validateISBN13(isbn) {
    let sum = 0;
    for (let i = 0; i < 13; i++) {
        if (!/\\d/.test(isbn[i])) {
            return { valid: false, message: 'ISBN-13 must contain only digits' };
        }
        let digit = parseInt(isbn[i]);
        sum += (i % 2 === 0) ? digit : digit * 3;
    }
    
    if (sum % 10 === 0) {
        return { valid: true, message: 'Valid ISBN-13' };
    } else {
        return { valid: false, message: 'Invalid ISBN-13 checksum' };
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { validateISBN };
}

console.log('[CODE-ON-DEMAND] ISBN validation logic loaded from server');
"""
    
    response = app.response_class(
        response=javascript_code,
        mimetype='application/javascript'
    )
    # Allow caching of validation code
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response


# ============================================================================
# EXAMPLE 2: Server sends JavaScript widget/component
# ============================================================================

@app.route('/api/widgets/book-card.js', methods=['GET'])
def get_book_card_widget():
    """
    CODE-ON-DEMAND: Server sends UI component code
    Client can render books using server-provided logic
    """
    javascript_code = """
// Book Card Widget - Delivered On-Demand
// Server controls presentation logic

class BookCard {
    constructor(book, containerId) {
        this.book = book;
        this.container = document.getElementById(containerId);
        this.render();
    }
    
    render() {
        const card = document.createElement('div');
        card.className = 'book-card';
        card.style.cssText = `
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 16px;
            margin: 10px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;
        
        card.innerHTML = `
            <h3 style="margin: 0 0 10px 0; color: #333;">${this.book.title}</h3>
            <p style="margin: 5px 0; color: #666;">
                <strong>Author:</strong> ${this.book.author}
            </p>
            <p style="margin: 5px 0; color: #666;">
                <strong>ISBN:</strong> ${this.book.isbn}
            </p>
            <p style="margin: 5px 0;">
                <span class="status" style="
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                    background: ${this.book.available ? '#4CAF50' : '#f44336'};
                    color: white;
                ">
                    ${this.book.available ? 'Available' : 'Borrowed'}
                </span>
            </p>
            <button onclick="alert('Book ID: ${this.book.id}')" style="
                margin-top: 10px;
                padding: 8px 16px;
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            ">
                View Details
            </button>
        `;
        
        this.container.appendChild(card);
    }
}

// Function to render all books
function renderBooks(books, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    books.forEach(book => new BookCard(book, containerId));
}

console.log('[CODE-ON-DEMAND] Book card widget loaded from server');
"""
    
    response = app.response_class(
        response=javascript_code,
        mimetype='application/javascript'
    )
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response


# ============================================================================
# EXAMPLE 3: Interactive HTML client that loads code on-demand
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """
    HTML client that demonstrates code-on-demand
    Dynamically loads JavaScript from server
    """
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Code-On-Demand Demo - Library</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: #2196F3;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        input, button {
            padding: 10px;
            margin: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background: #45a049;
        }
        .validation-result {
            margin-top: 10px;
            padding: 10px;
            border-radius: 4px;
        }
        .valid {
            background: #dff0d8;
            color: #3c763d;
        }
        .invalid {
            background: #f2dede;
            color: #a94442;
        }
        .info {
            background: #d9edf7;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 Code-On-Demand Demonstration</h1>
        <p>This page dynamically loads code from the server</p>
    </div>

    <div class="section">
        <h2>Example 1: Dynamic Validation Logic</h2>
        <div class="info">
            <strong>Code-On-Demand:</strong> ISBN validation logic is loaded from server.
            The server can update validation rules without changing the client.
        </div>
        <input type="text" id="isbnInput" placeholder="Enter ISBN (e.g., 0132350882)" />
        <button onclick="validateISBN()">Validate ISBN</button>
        <div id="validationResult"></div>
    </div>

    <div class="section">
        <h2>Example 2: Dynamic UI Components</h2>
        <div class="info">
            <strong>Code-On-Demand:</strong> Book display widget is loaded from server.
            The server controls how books are presented.
        </div>
        <button onclick="loadBooks()">Load Books</button>
        <div id="booksContainer"></div>
    </div>

    <div class="section">
        <h2>Code Loading Status</h2>
        <div id="codeStatus"></div>
    </div>

    <script>
        // Step 1: Load ISBN validation code from server (Code-On-Demand)
        console.log('[CLIENT] Loading ISBN validation code from server...');
        const validationScript = document.createElement('script');
        validationScript.src = '/api/validation/isbn.js';
        validationScript.onload = () => {
            document.getElementById('codeStatus').innerHTML += 
                '<p style="color: green;">✓ ISBN validation code loaded from server</p>';
        };
        document.head.appendChild(validationScript);

        // Step 2: Load book card widget from server (Code-On-Demand)
        console.log('[CLIENT] Loading book widget code from server...');
        const widgetScript = document.createElement('script');
        widgetScript.src = '/api/widgets/book-card.js';
        widgetScript.onload = () => {
            document.getElementById('codeStatus').innerHTML += 
                '<p style="color: green;">✓ Book widget code loaded from server</p>';
        };
        document.head.appendChild(widgetScript);

        // Client-side function to validate ISBN using server-provided code
        function validateISBN() {
            const isbn = document.getElementById('isbnInput').value;
            const resultDiv = document.getElementById('validationResult');
            
            // Use validation function loaded from server
            const result = window.validateISBN(isbn);
            
            resultDiv.className = 'validation-result ' + (result.valid ? 'valid' : 'invalid');
            resultDiv.innerHTML = `
                <strong>${result.valid ? '✓' : '✗'} ${result.message}</strong>
                <p>Validation performed using server-provided logic</p>
            `;
        }

        // Client-side function to load and display books
        async function loadBooks() {
            const response = await fetch('/api/books');
            const data = await response.json();
            
            // Use widget loaded from server to render books
            window.renderBooks(data.data, 'booksContainer');
        }

        // Display info about code-on-demand
        document.getElementById('codeStatus').innerHTML += 
            '<p><strong>Note:</strong> This page loaded executable code from the server:</p>' +
            '<ul>' +
            '<li>/api/validation/isbn.js - Validation logic</li>' +
            '<li>/api/widgets/book-card.js - UI component</li>' +
            '</ul>' +
            '<p>The server can update this code without changing the client!</p>';
    </script>
</body>
</html>
    """
    return render_template_string(html)


# ============================================================================
# Standard API endpoints
# ============================================================================

@app.route('/api/books', methods=['GET'])
def get_books():
    """Get all books"""
    books = Book.query.all()
    return jsonify({
        'success': True,
        'data': [book.to_dict() for book in books]
    })


@app.route('/api/books', methods=['POST'])
def create_book():
    """Create a new book"""
    data = request.get_json()
    
    book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn']
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': book.to_dict(),
        'message': 'Book created'
    }), 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add sample data
        if Book.query.count() == 0:
            samples = [
                Book(title="Designing Data-Intensive Applications", author="Martin Kleppmann", isbn="1449373321"),
                Book(title="Site Reliability Engineering", author="Google", isbn="149192912X"),
                Book(title="The Phoenix Project", author="Gene Kim", isbn="0988262592"),
            ]
            db.session.add_all(samples)
            db.session.commit()
            print("✓ Sample books added")
    
    print("="*70)
    print("CODE-ON-DEMAND DEMONSTRATION")
    print("="*70)
    print("Server running on http://127.0.0.1:5006")
    print("\nCode-On-Demand Features:")
    print("  • Server sends JavaScript validation logic")
    print("  • Server sends UI component code")
    print("  • Client executes server-provided code")
    print("  • Server can update logic without client changes")
    print("\nThis is the ONLY OPTIONAL REST constraint!")
    print("\nOpen browser: http://127.0.0.1:5006")
    print("="*70)
    
    app.run(debug=True, port=5006)
