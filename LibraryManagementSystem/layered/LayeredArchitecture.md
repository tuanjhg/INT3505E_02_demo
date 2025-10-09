# Layered System Architecture

## RESTful Constraint #4: Layered System

### Overview
The layered system constraint means that the architecture is composed of hierarchical layers, with each layer having a specific responsibility. A component in one layer cannot see beyond the immediate layer with which it is interacting. The client cannot ordinarily tell whether it is connected directly to the end server or to an intermediary along the way.

### Key Principles
1. **Hierarchical Organization**: Components organized in layers
2. **Layer Independence**: Each layer only interacts with adjacent layers
3. **Encapsulation**: Implementation details hidden from other layers
4. **Intermediaries**: Support for proxies, gateways, and load balancers
5. **Transparency**: Client unaware of intermediary layers

### Three-Tier Architecture in Library System

```
┌─────────────────────────────────────────────┐
│   PRESENTATION LAYER (API Layer)           │
│   - HTTP Request/Response handling          │
│   - Input validation                        │
│   - Response formatting                     │
│   - Authentication/Authorization            │
└─────────────────┬───────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────┐
│   BUSINESS LOGIC LAYER                      │
│   - Business rules and validation           │
│   - Domain logic                            │
│   - Data transformation                     │
│   - Workflow coordination                   │
└─────────────────┬───────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────┐
│   DATA ACCESS LAYER                         │
│   - Database operations (CRUD)              │
│   - Query optimization                      │
│   - Data persistence                        │
│   - Transaction management                  │
└─────────────────────────────────────────────┘
                  │
                  ↓
          [DATABASE]
```

### Layer Responsibilities

#### Layer 1: Data Access Layer (DAL)
**Purpose**: Direct database interaction
- Raw CRUD operations
- No business logic
- Database-specific code isolated here
- Query optimization

**Example:**
```python
class DataAccessLayer:
    def get_all_books(self):
        return Book.query.all()
    
    def create_book(self, title, author, isbn):
        book = Book(title=title, author=author, isbn=isbn)
        db.session.add(book)
        db.session.commit()
        return book
```

#### Layer 2: Business Logic Layer (BLL)
**Purpose**: Business rules and domain logic
- Validation logic
- Business rule enforcement
- Data transformation
- Independent of data storage and presentation

**Example:**
```python
class BusinessLogicLayer:
    def create_book(self, title, author, isbn):
        # Business validation
        if len(isbn) not in [10, 13]:
            raise ValueError("Invalid ISBN format")
        
        # Check business rule
        if self.book_exists(isbn):
            raise ValueError("Book already exists")
        
        # Delegate to data layer
        return self.dal.create_book(title, author, isbn)
```

#### Layer 3: Presentation Layer (API)
**Purpose**: HTTP interface and request handling
- Request parsing
- Input validation
- Response formatting
- HTTP-specific concerns (headers, status codes)

**Example:**
```python
class PresentationLayer:
    def handle_create_book(self, request_data):
        # HTTP validation
        if not request_data:
            return error_response("No data", 400)
        
        # Delegate to business layer
        try:
            book = self.bll.create_book(...)
            return success_response(book, 201)
        except ValueError as e:
            return error_response(str(e), 400)
```

### Benefits of Layered Architecture

#### 1. Separation of Concerns
- Each layer has single responsibility
- Easier to understand and maintain
- Changes localized to specific layers

#### 2. Testability
- Test layers independently
- Mock adjacent layers
- Unit test business logic without database

```python
# Test business layer without database
mock_dal = Mock()
mock_dal.get_book_by_id.return_value = fake_book
bll = BusinessLogicLayer(mock_dal)
result = bll.get_book(1)
```

#### 3. Flexibility
- Replace implementations without affecting other layers
- Switch databases (DAL change only)
- Add new API versions (Presentation layer)
- Modify business rules (BLL only)

#### 4. Reusability
- Business logic used by multiple APIs (REST, GraphQL, gRPC)
- Data layer used by different business contexts
- Common utilities shared across layers

#### 5. Scalability
- Scale layers independently
- Add caching layer between API and business logic
- Add message queue between layers
- Horizontal scaling of specific layers

### Intermediary Layers in REST

Beyond the three-tier architecture, REST supports intermediaries:

```
[Client] → [CDN] → [Load Balancer] → [API Gateway] → [Server]
```

**Common Intermediaries:**
- **Load Balancer**: Distribute requests across servers
- **API Gateway**: Single entry point, routing, authentication
- **Reverse Proxy**: Caching, SSL termination
- **CDN**: Content delivery, edge caching

### Layer Communication Rules

#### ✓ DO:
- Communicate only with adjacent layers
- Use well-defined interfaces
- Pass data, not behavior
- Return domain objects

#### ✗ DON'T:
- Skip layers (e.g., API → DAL directly)
- Expose internal implementation
- Share database connections across layers
- Couple layers tightly

### Example Flow

**Create Book Request:**
```
1. Client: POST /api/books
   ↓
2. Presentation Layer:
   - Parse JSON request
   - Validate HTTP format
   - Extract data
   ↓
3. Business Layer:
   - Validate ISBN format
   - Check business rules
   - Enforce constraints
   ↓
4. Data Layer:
   - Create database record
   - Execute SQL INSERT
   - Return book object
   ↓
5. Business Layer:
   - Convert to domain object
   - Return to presentation
   ↓
6. Presentation Layer:
   - Format JSON response
   - Set status code 201
   - Return to client
```

### Real-World Application

#### Microservices Architecture
```
[API Gateway Layer]
        ↓
[Service Layer] → [Service A, Service B, Service C]
        ↓
[Data Layer] → [Database A, Database B, Database C]
```

#### N-Tier Enterprise
```
[Web Tier] → [Application Tier] → [Data Tier]
```

Each tier can be on different servers, enabling:
- Independent scaling
- Technology diversity
- Security zones
- Load distribution

### How to Run

1. **Start the Layered Server:**
```bash
python LayeredServer.py
```

2. **Observe Layer Interactions:**
Watch console output to see how requests flow through layers:
```
[API-LAYER] Request: GET /books
[BUSINESS-LAYER] Processing: Get all books
[DATA-LAYER] Fetching all books from database
```

3. **Test with curl:**
```bash
# Create book - see full layer flow
curl -X POST http://127.0.0.1:5004/api/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Book","author":"Test","isbn":"1234567890"}'
```

### Best Practices

1. **Keep Layers Thin**: Each layer should do one thing well
2. **Use DTOs**: Transfer data between layers with Data Transfer Objects
3. **No Business Logic in DAL**: Data layer should be dumb
4. **No HTTP in BLL**: Business layer should be protocol-agnostic
5. **Clear Boundaries**: Well-defined interfaces between layers
6. **Dependency Direction**: Higher layers depend on lower layers, not vice versa

### Summary

The layered system constraint in REST:
- ✓ Organizes code into distinct, responsible layers
- ✓ Enables independent development and scaling of layers
- ✓ Supports intermediaries (proxies, gateways, caches)
- ✓ Improves maintainability and testability
- ✓ Allows client to be unaware of system complexity
