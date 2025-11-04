# API Testing Guide

This document describes how to use the Postman test suite and run automated tests with Newman for the Library Management System API.

## Overview

The test suite includes comprehensive tests for 5 key endpoints:
1. **User Login** - Authentication endpoint
2. **Get All Books** - Retrieve books with pagination
3. **Create New Book** - Add a new book to the library
4. **Borrow a Book** - Create a borrow record
5. **Return a Book** - Mark a book as returned

Each endpoint includes multiple test assertions to validate:
- HTTP status codes
- Response structure and data types
- Business logic correctness
- Response times
- Error handling

## Prerequisites

### 1. Install Newman (Postman CLI)

Newman is required to run the tests from the command line.

```bash
# Install Newman globally using npm
npm install -g newman

# Verify installation
newman --version
```

### 2. Install Newman HTML Reporter (Optional but Recommended)

For better test reports:

```bash
npm install -g newman-reporter-html
```

## Test Suite Structure

### Postman Collection

The test collection is located at:
```
LibraryManageSystem/LibraryManagement.postman_collection.json
```

### Collection Variables

The collection uses the following variables:
- `base_url`: Base URL of the API (default: http://127.0.0.1:5000)
- `access_token`: JWT token from login (auto-populated)
- `book_id`: ID of a book (auto-populated)
- `created_book_id`: ID of newly created book (auto-populated)
- `borrow_record_id`: ID of borrow record (auto-populated)

## Running Tests

### Method 1: Using the Shell Script (Recommended)

The easiest way to run all tests:

```bash
# 1. Make sure Flask app is running
cd LibraryManageSystem
python app_swagger.py

# 2. In another terminal, run the test script
cd LibraryManageSystem
./run-newman-tests.sh
```

The script will:
- ✅ Check if Newman is installed
- ✅ Verify Flask app is running
- ✅ Run all tests with detailed output
- ✅ Generate HTML and JSON reports

### Method 2: Using Newman Directly

Run Newman with custom options:

```bash
# Basic run
newman run LibraryManagement.postman_collection.json

# Run with HTML report
newman run LibraryManagement.postman_collection.json \
    --reporters cli,html \
    --reporter-html-export newman-report.html

# Run with JSON report
newman run LibraryManagement.postman_collection.json \
    --reporters cli,json \
    --reporter-json-export newman-results.json

# Run with both HTML and JSON reports
newman run LibraryManagement.postman_collection.json \
    --reporters cli,html,json \
    --reporter-html-export newman-report.html \
    --reporter-json-export newman-results.json

# Run with verbose output
newman run LibraryManagement.postman_collection.json --verbose

# Run and stop on first failure
newman run LibraryManagement.postman_collection.json --bail
```

### Method 3: Using Postman Desktop App

1. Open Postman Desktop
2. Click **Import** button
3. Select `LibraryManagement.postman_collection.json`
4. Click on **Collections** in the sidebar
5. Click **Run** button to open Collection Runner
6. Click **Run Library Management System API** button

## Test Details

### 1. User Login Tests
**Endpoint:** `POST /api/auth/login`

Tests performed (7 total):
- ✅ Status code is 200
- ✅ Response has JSON body
- ✅ Success field is true
- ✅ Response contains access_token
- ✅ Response contains user information
- ✅ Token type is Bearer
- ✅ Response time is less than 1000ms

The access token is automatically saved for subsequent tests.

### 2. Get All Books Tests
**Endpoint:** `GET /api/books`

Tests performed (7 total):
- ✅ Status code is 200
- ✅ Response has JSON body
- ✅ Success field is true
- ✅ Response contains books array
- ✅ Response contains pagination information
- ✅ Books have required fields (id, title, author, isbn, available)
- ✅ Response time is less than 1000ms

### 3. Create New Book Tests
**Endpoint:** `POST /api/books`

Tests performed (7 total):
- ✅ Status code is 201 (Created)
- ✅ Response has JSON body
- ✅ Success field is true
- ✅ Response contains book data
- ✅ Created book has correct title
- ✅ New book is available by default
- ✅ Success message indicates creation

The created book ID is saved for the borrow test.

### 4. Borrow a Book Tests
**Endpoint:** `POST /api/borrows`

Tests performed (7 total):
- ✅ Status code is 201
- ✅ Response has JSON body
- ✅ Success field is true
- ✅ Response contains borrow record with all fields
- ✅ Book is marked as not returned
- ✅ Book details are included
- ✅ Success message indicates borrowing

The borrow record ID is saved for the return test.

### 5. Return a Book Tests
**Endpoint:** `POST /api/borrows/{id}/return`

Tests performed (8 total):
- ✅ Status code is 200
- ✅ Response has JSON body
- ✅ Success field is true
- ✅ Response contains borrow record
- ✅ Book is marked as returned
- ✅ Return date is set
- ✅ Success message indicates return
- ✅ Response time is less than 1000ms

## Understanding Test Results

### Console Output

Newman provides detailed console output:

```
→ 1. User Login
  POST http://127.0.0.1:5000/api/auth/login [200 OK, 1.2KB, 245ms]
  ✓ Status code is 200
  ✓ Response has JSON body
  ✓ Success field is true
  ✓ Response contains access_token
  ✓ Response contains user information
  ✓ Token type is Bearer
  ✓ Response time is less than 1000ms
```

### HTML Report

After running tests, open `newman-report.html` in a browser to see:
- Test execution summary
- Pass/fail statistics
- Detailed request/response data
- Performance metrics
- Failure reasons (if any)

### JSON Report

The `newman-results.json` file contains:
- Machine-readable test results
- Detailed execution data
- Can be used for CI/CD integration
- Can be processed by other tools

## Test Execution Flow

The tests execute in sequence:

```
1. Login → Get access token
2. Get All Books → Verify books list
3. Create Book → Save book ID
4. Borrow Book → Use created book ID, save borrow record ID
5. Return Book → Use borrow record ID
```

Each test depends on the previous one's success and uses saved variables.

## Troubleshooting

### Newman Not Found
```bash
# Install Newman globally
npm install -g newman
```

### Flask App Not Running
```bash
# Start the Flask app
cd LibraryManageSystem
python app_swagger.py
```

### Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use a different port by modifying .env
PORT=5001
```

### Tests Failing

1. Check Flask app logs for errors
2. Verify database is initialized:
   ```bash
   python add_mock_data.py
   ```
3. Ensure user exists for login:
   ```bash
   # Register a test user
   curl -X POST http://127.0.0.1:5000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "test123", "full_name": "Test User"}'
   ```
4. Check collection variables are set correctly
5. Review error messages in Newman output

### SSL/Certificate Errors
```bash
# Disable SSL verification (for testing only)
newman run collection.json --insecure
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm install -g newman
      
      - name: Start Flask app
        run: |
          cd LibraryManageSystem
          python app_swagger.py &
          sleep 5
      
      - name: Run API tests
        run: |
          cd LibraryManageSystem
          newman run LibraryManagement.postman_collection.json \
            --reporters cli,json \
            --reporter-json-export test-results.json
      
      - name: Upload test results
        uses: actions/upload-artifact@v2
        with:
          name: newman-results
          path: LibraryManageSystem/test-results.json
```

## Best Practices

1. **Run tests before committing** - Ensure all tests pass
2. **Check test reports** - Review HTML reports for detailed insights
3. **Keep collection updated** - Update tests when API changes
4. **Add new tests** - Expand test coverage for new endpoints
5. **Use environment variables** - For different environments (dev, staging, prod)
6. **Monitor response times** - Ensure API performance is acceptable

## Additional Resources

- [Newman Documentation](https://learning.postman.com/docs/running-collections/using-newman-cli/command-line-integration-with-newman/)
- [Postman Test Scripts](https://learning.postman.com/docs/writing-scripts/test-scripts/)
- [API Documentation](./API_DOCUMENTATION.md)

## Total Test Coverage

**Total Endpoints Tested:** 5  
**Total Test Assertions:** 36

- User Login: 7 tests
- Get All Books: 7 tests  
- Create New Book: 7 tests
- Borrow a Book: 7 tests
- Return a Book: 8 tests

All tests are designed to be independent and idempotent where possible.
