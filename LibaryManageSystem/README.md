# Library Management System

A comprehensive Flask-based library management system with both web interface and REST API, featuring Swagger documentation, modular architecture, and modern web development practices.

## 🏗️ Architecture

The application follows a modular architecture pattern with clear separation of concerns:

```
LibraryManageSystem/
├── models/          # Data models and database schemas
├── routes/          # Request routing and API endpoints
├── services/        # Business logic and data processing
├── utils/           # Helper functions and utilities
├── templates/       # HTML templates for web interface
└── app files        # Application entry points
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning)

### Setup Steps

1. **Navigate to the project directory**
   ```bash
   cd LibaryManageSystem
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the template (if available in parent directory)
   cp ../.env.template .env
   
   # Or create manually with your preferred settings
   ```

5. **Initialize the database with sample data**
   ```bash
   python add_mock_data.py
   ```

## ⚙️ Configuration

### Environment Variables

The application supports configuration through environment variables. Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=sqlite:///library.db

# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
HOST=127.0.0.1
PORT=5000

# API Configuration
API_VERSION=1.0
API_TITLE=Library Management API
API_DESCRIPTION=A comprehensive library management system API
```

### Default Configuration
If no `.env` file is provided, the application uses these defaults:
- **Database**: `sqlite:///library.db`
- **Host**: `127.0.0.1`
- **Port**: `5000`
- **Debug Mode**: `True`

## 💻 Usage

### Running the Application

#### Option 1: Basic Flask App
```bash
python app_new.py
```
- Web interface: http://127.0.0.1:5000
- API endpoints available but no Swagger documentation

#### Option 2: Flask App with Swagger
```bash
python app_swagger.py
```
- Web interface: http://127.0.0.1:5000
- API endpoints: http://127.0.0.1:5000/api
- Swagger UI: http://127.0.0.1:5000/swagger/


### Sample Data

Generate realistic sample data for testing:

```bash
python add_mock_data.py
```

## 📖 API Documentation

### Swagger UI
When using `app_swagger.py`, interactive API documentation is available at:
- **Swagger UI**: http://127.0.0.1:5000/swagger/

### API Endpoints

#### Books API (`/api/books/`)
- `GET /api/books/` - List all books
- `POST /api/books/` - Add a new book
- `GET /api/books/{id}` - Get book details
- `PUT /api/books/{id}` - Update book
- `DELETE /api/books/{id}` - Delete book

#### Enhanced Borrowing API (`/api/borrows/`)
- `GET /api/borrows/` - **List all borrow records with search, filtering, and pagination**
- `POST /api/borrows/` - Create new borrow record
- `GET /api/borrows/{id}` - Get borrow details
- `PUT /api/borrows/{id}/return` - Return a book
