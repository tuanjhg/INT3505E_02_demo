# API Documentation

## Books API

### Get all books
```
GET /api/books
```

### Search books
```
GET /api/books?search=python
```

### Get available books only
```
GET /api/books/available
```

### Get specific book
```
GET /api/books/{id}
```

### Create new book
```
POST /api/books
Content-Type: application/json

{
    "title": "Python Programming",
    "author": "John Doe",
    "isbn": "1234567890123"
}
```

### Update book
```
PUT /api/books/{id}
Content-Type: application/json

{
    "title": "Updated Title",
    "author": "Updated Author",
    "isbn": "1234567890123"
}
```

### Delete book
```
DELETE /api/books/{id}
```

## Borrows API

### Get all borrow records
```
GET /api/borrows
```

### Get active borrows only
```
GET /api/borrows?active=true
```

### Get overdue borrows
```
GET /api/borrows?overdue=true
```

### Get borrower history
```
GET /api/borrows?borrower_email=john@example.com
```

### Get specific borrow record
```
GET /api/borrows/{id}
```

### Borrow a book
```
POST /api/borrows
Content-Type: application/json

{
    "book_id": 1,
    "borrower_name": "John Doe",
    "borrower_email": "john@example.com",
    "days": 14
}
```

### Return a book
```
POST /api/borrows/{id}/return
```

### Extend due date
```
POST /api/borrows/{id}/extend
Content-Type: application/json

{
    "additional_days": 7
}
```

### Get overdue books
```
GET /api/borrows/overdue
```

## Response Format

All API responses follow this format:

```json
{
    "success": true/false,
    "message": "Description of the result",
    "data": {...} // Actual data or null
}
```

## Error Codes

- 200: Success
- 201: Created
- 204: No Content (for deletes)
- 400: Bad Request
- 404: Not Found
- 405: Method Not Allowed
- 500: Internal Server Error