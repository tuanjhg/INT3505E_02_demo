# Uniform Interface

## RESTful Constraint #5: Uniform Interface

### Overview
The uniform interface is the fundamental feature that distinguishes REST from other network architectural styles. It simplifies and decouples the architecture, enabling each part to evolve independently. The uniform interface consists of four sub-constraints.

### Four Sub-Constraints

#### 1. Identification of Resources
Resources are identified by URIs (Uniform Resource Identifiers). Each resource has a unique, predictable URI.

**Examples:**
```
/api/books              - Collection of books
/api/books/1            - Specific book (ID 1)
/api/books/1/borrow     - Action on book
```

**Benefits:**
- Predictable resource locations
- Clear resource hierarchy
- Easy to understand and remember

#### 2. Manipulation of Resources Through Representations
Clients interact with resources through representations (typically JSON or XML). The representation includes enough information to modify or delete the resource.

**Example Response:**
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "0132350882",
  "available": true,
  "_links": {
    "self": {"href": "/api/books/1"},
    "update": {"href": "/api/books/1", "method": "PUT"},
    "delete": {"href": "/api/books/1", "method": "DELETE"}
  }
}
```

#### 3. Self-Descriptive Messages
Each message includes enough information to describe how to process the message. This includes:
- HTTP method indicates operation
- Headers describe content and caching
- Status codes indicate result
- Complete error information

**Example:**
```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=60
ETag: "abc123"

{
  "success": true,
  "data": { ... }
}
```

#### 4. Hypermedia as the Engine of Application State (HATEOAS)
Responses include links to related resources and possible actions. Clients navigate the API by following these links, not by constructing URLs.

**Example:**
```json
{
  "id": 1,
  "title": "Book Title",
  "available": true,
  "_links": {
    "self": {"href": "/api/books/1"},
    "borrow": {
      "href": "/api/books/1/borrow",
      "method": "POST",
      "description": "Borrow this book"
    }
  }
}
```

If the book is borrowed, the `borrow` link disappears and a `return` link appears, guiding the client on available actions.

### Standard HTTP Methods

The uniform interface uses standard HTTP methods with consistent semantics:

| Method | Purpose | Safe | Idempotent | Cacheable |
|--------|---------|------|------------|-----------|
| GET | Retrieve resource | ✓ | ✓ | ✓ |
| POST | Create resource | ✗ | ✗ | ✗ |
| PUT | Update/Replace | ✗ | ✓ | ✗ |
| PATCH | Partial Update | ✗ | ✗ | ✗ |
| DELETE | Remove resource | ✗ | ✓ | ✗ |

**Properties:**
- **Safe**: Does not modify resources
- **Idempotent**: Multiple identical requests have same effect as single request
- **Cacheable**: Response can be cached

### Example API Flow

#### 1. Discover API
```bash
GET /api
```
```json
{
  "_links": {
    "books": {"href": "/api/books"},
    "create_book": {"href": "/api/books", "method": "POST"}
  }
}
```

#### 2. List Resources
```bash
GET /api/books
```
```json
{
  "data": [
    {
      "id": 1,
      "title": "Clean Code",
      "_links": {
        "self": {"href": "/api/books/1"},
        "borrow": {"href": "/api/books/1/borrow"}
      }
    }
  ]
}
```

#### 3. Get Specific Resource
```bash
GET /api/books/1
```
```json
{
  "id": 1,
  "title": "Clean Code",
  "available": true,
  "_links": {
    "self": {"href": "/api/books/1"},
    "update": {"href": "/api/books/1", "method": "PUT"},
    "delete": {"href": "/api/books/1", "method": "DELETE"},
    "borrow": {"href": "/api/books/1/borrow", "method": "POST"}
  }
}
```

#### 4. Create Resource
```bash
POST /api/books
Content-Type: application/json

{
  "title": "New Book",
  "author": "Author Name",
  "isbn": "1234567890"
}
```
Response:
```http
HTTP/1.1 201 Created
Location: /api/books/2
Content-Type: application/json

{
  "id": 2,
  "title": "New Book",
  "_links": {
    "self": {"href": "/api/books/2"}
  }
}
```

#### 5. Update Resource
```bash
PUT /api/books/2
Content-Type: application/json

{
  "title": "Updated Title",
  "author": "Author Name",
  "isbn": "1234567890"
}
```

#### 6. Partial Update
```bash
PATCH /api/books/2
Content-Type: application/json

{
  "title": "Partially Updated Title"
}
```

#### 7. Delete Resource
```bash
DELETE /api/books/2
```
Response:
```http
HTTP/1.1 204 No Content
```

### Benefits of Uniform Interface

#### 1. Simplicity
- Standard methods for all resources
- Predictable behavior
- Easy to learn and use

#### 2. Visibility
- Operations are self-descriptive
- Easy to monitor and debug
- Clear intent from HTTP method

#### 3. Independent Evolution
- Client and server evolve independently
- New resources follow same patterns
- No tight coupling

#### 4. Scalability
- Intermediaries (proxies, caches) can understand and optimize
- Standard methods enable generic caching
- Load balancing simplified

### HATEOAS Benefits

**Loose Coupling:**
- Clients don't hardcode URLs
- Server can change URL structure
- Links guide client behavior

**Discoverability:**
- API is self-documenting
- Clients explore through links
- Less documentation needed

**State-Driven:**
- Available actions based on resource state
- Prevents invalid operations
- Guides user workflow

### How to Run

1. **Start the Uniform Interface Server:**
```bash
python ApiController.py
```
Server runs on http://127.0.0.1:5005

2. **Explore the API:**
```bash
# Start at root
curl http://127.0.0.1:5005/api

# Follow links to books
curl http://127.0.0.1:5005/api/books

# Get specific book with HATEOAS links
curl http://127.0.0.1:5005/api/books/1
```

3. **Test Standard Methods:**
```bash
# POST - Create
curl -X POST http://127.0.0.1:5005/api/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","author":"Author","isbn":"1234567890"}'

# PUT - Update
curl -X PUT http://127.0.0.1:5005/api/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated","author":"Author","isbn":"1234567890"}'

# DELETE - Remove
curl -X DELETE http://127.0.0.1:5005/api/books/1 -v
```

### Best Practices

#### Resource Naming
```
✓ /api/books           - Plural nouns
✓ /api/books/1         - Resource ID
✓ /api/books/1/borrow  - Action as sub-resource

✗ /api/getBooks        - No verbs in URLs
✗ /api/books/delete    - Use HTTP methods, not URL verbs
```

#### HTTP Methods
```
✓ GET /api/books       - Retrieve
✓ POST /api/books      - Create
✓ PUT /api/books/1     - Update
✓ DELETE /api/books/1  - Remove

✗ POST /api/deleteBook - Don't use POST for everything
✗ GET /api/updateBook  - GET should be safe
```

#### Response Codes
```
200 OK              - Successful GET, PUT, PATCH
201 Created         - Successful POST
204 No Content      - Successful DELETE
400 Bad Request     - Invalid input
404 Not Found       - Resource doesn't exist
500 Internal Error  - Server error
```

### Summary

The uniform interface:
- ✓ Uses standard HTTP methods consistently
- ✓ Identifies resources with URIs
- ✓ Represents resources in standard formats
- ✓ Includes self-descriptive messages
- ✓ Provides hypermedia links (HATEOAS)
- ✓ Enables independent client/server evolution
- ✓ Simplifies architecture and improves scalability
