# Library Management System - RESTful Architecture

This project demonstrates the six constraints of RESTful architecture through a library management system. Each folder represents one constraint with practical code examples.

## 📚 Project Structure

```
LibraryManagementSystem/
├── client-server/          # Constraint 1: Client-Server Architecture
│   ├── Client.java         # Client implementation
│   └── Server.java         # Server implementation
├── stateless/              # Constraint 2: Stateless Communication
│   └── StatelessService.java
├── cacheable/              # Constraint 3: Cacheable Responses
│   └── CacheManager.java
├── layered-system/         # Constraint 4: Layered System
│   ├── LayeredArchitecture.md
│   └── LayerExample.java
├── uniform-interface/      # Constraint 5: Uniform Interface
│   └── ApiController.java
├── code-on-demand/         # Constraint 6: Code-On-Demand (Optional)
│   └── DynamicLoader.js
└── README.md              # This file
```

## 🎯 The Six RESTful Constraints

### 1. Client-Server Architecture (`/client-server`)

**Purpose**: Separation of concerns between user interface and data storage.

**Key Concepts**:
- Client initiates requests
- Server processes requests and manages resources
- Clear separation of responsibilities

**Benefits**:
- Portability of user interface
- Scalability through independent evolution
- Simplified server implementation

**Files**:
- `Client.java` - Demonstrates how clients make HTTP requests to the server
- `Server.java` - Shows server responding to client requests and managing resources

**Example Usage**:
```java
Client client = new Client();
client.getAllBooks();                    // GET /api/books
client.addBook("Title", "Author", "ISBN"); // POST /api/books
client.borrowBook(1, "John", "john@example.com", 14);
```

---

### 2. Stateless Communication (`/stateless`)

**Purpose**: Each request contains all information needed to understand and process it.

**Key Concepts**:
- No client context stored on server between requests
- Each request is independent and self-contained
- Authentication/authorization in every request

**Benefits**:
- Visibility - easy to monitor individual requests
- Reliability - easier recovery from failures
- Scalability - no session management overhead

**Files**:
- `StatelessService.java` - Shows stateless request handling

**Example**:
```java
// Each request includes ALL necessary information
service.searchBooks("REST API", "programming", authToken);
service.getBorrowHistory("user@email.com", page=1, pageSize=10, authToken);

// Server doesn't remember previous requests or user state
```

**Counter-Example** (What NOT to do):
```java
// DON'T: Store client state on server
Map<String, UserSession> sessions = new HashMap<>();
session.lastSearch = query;      // Violates stateless constraint
session.currentPage = page;      // Server shouldn't track this
```

---

### 3. Cacheable Responses (`/cacheable`)

**Purpose**: Responses must label themselves as cacheable or non-cacheable.

**Key Concepts**:
- Use HTTP cache headers (Cache-Control, ETag)
- Client can reuse cached responses
- Implement cache invalidation strategies

**Benefits**:
- Efficiency - reduced network traffic
- Performance - faster response times
- Scalability - fewer requests reach server

**Files**:
- `CacheManager.java` - Demonstrates caching implementation

**Cacheable Examples**:
```java
// Book catalog - cacheable (changes infrequently)
getBooks() -> Cache-Control: max-age=300

// Specific book - cacheable with ETag
getBook(id) -> Cache-Control: max-age=600, ETag: "abc123"

// Search results - short-term cache
searchBooks(query) -> Cache-Control: max-age=60
```

**Non-Cacheable Examples**:
```java
// Borrow operation - NOT cacheable (modifies state)
borrowBook() -> Cache-Control: no-cache, no-store

// Overdue books - time-sensitive, minimal cache
getOverdueBooks() -> Cache-Control: max-age=10
```

---

### 4. Layered System (`/layered-system`)

**Purpose**: Architecture composed of hierarchical layers, each component interacts only with adjacent layers.

**Key Concepts**:
- Client doesn't know about intermediary servers
- Layers can be added/removed transparently
- Each layer has specific responsibilities

**Benefits**:
- Encapsulation - layers are independent
- Scalability - add load balancers, proxies
- Security - enforce policies at different layers
- Legacy integration - wrap old systems

**Files**:
- `LayeredArchitecture.md` - Detailed explanation and diagrams
- `LayerExample.java` - Code demonstrating layer interactions

**Layer Stack**:
```
Client Layer
    ↓
Load Balancer Layer (Nginx, HAProxy)
    ↓
API Gateway Layer (Auth, Rate Limiting)
    ↓
Application Layer (Business Logic)
    ↓
Cache Layer (Redis, Memcached)
    ↓
Database Layer (PostgreSQL, MySQL)
```

**Example**:
```java
// Client only knows about the load balancer endpoint
client.request("https://library.com/api/books");

// Request flows through layers:
// Client → Load Balancer → Gateway → Application → Cache → Database
// Client has no knowledge of intermediate layers!
```

---

### 5. Uniform Interface (`/uniform-interface`)

**Purpose**: Standardized interface that simplifies and decouples the architecture.

**Four Sub-Constraints**:

#### 5.1 Identification of Resources
- Resources identified by URIs
- `/api/books` - book collection
- `/api/books/123` - specific book
- `/api/borrows` - borrow records

#### 5.2 Manipulation Through Representations
- Use standard HTTP methods:
  - `GET` - Retrieve resource(s)
  - `POST` - Create new resource
  - `PUT` - Update/replace resource
  - `DELETE` - Remove resource

#### 5.3 Self-Descriptive Messages
- HTTP status codes (200, 404, 500)
- Content-Type headers
- Standard HTTP methods
- Messages contain all info to process them

#### 5.4 HATEOAS (Hypermedia As The Engine Of Application State)
- Responses include links to related resources
- Clients discover available actions through hypermedia

**Files**:
- `ApiController.java` - Complete implementation of uniform interface

**Example - HATEOAS**:
```json
GET /api/books/1
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert Martin",
  "available": true,
  "_links": {
    "self": { "href": "/api/books/1", "method": "GET" },
    "update": { "href": "/api/books/1", "method": "PUT" },
    "delete": { "href": "/api/books/1", "method": "DELETE" },
    "borrow": { 
      "href": "/api/borrows", 
      "method": "POST",
      "body": { "book_id": 1, "borrower_name": "...", ... }
    }
  }
}
```

---

### 6. Code-On-Demand (`/code-on-demand`) - **OPTIONAL**

**Purpose**: Server can extend client functionality by transferring executable code.

**Key Concepts**:
- Server sends JavaScript to browser
- Client executes code dynamically
- Features deployed without client updates

**Benefits**:
- Improved client extensibility
- Reduced initial client complexity
- Centralized business logic updates

**Trade-offs**:
- Reduced visibility
- Security concerns
- Network dependency

**Files**:
- `DynamicLoader.js` - Client and server code examples

**Use Cases**:

1. **Validation Rules**:
```javascript
// Server sends validation code
const code = await fetch('/api/code/validation');
eval(code); // Now validateISBN() function is available
validateISBN('9780132350884'); // Use server-provided validator
```

2. **UI Enhancements**:
```javascript
// Load UI enhancement code from server
await loader.loadCode('ui-enhancement');
enhanceBookDisplay(bookElement, bookData); // Function from server
```

3. **Analytics**:
```javascript
// Load analytics code dynamically
await loader.loadCode('analytics');
trackBookView(bookId); // Server-provided tracking
```

---

## 🚀 Getting Started

### Prerequisites
- Java Development Kit (JDK) 11+
- Node.js 14+ (for JavaScript examples)
- Basic understanding of REST architecture

### Running Examples

#### Java Examples
```bash
# Compile
javac client-server/Client.java
javac stateless/StatelessService.java

# Run
java -cp . client-server.Client
java -cp . stateless.StatelessService
```

#### JavaScript Examples
```bash
# Run with Node.js
node code-on-demand/DynamicLoader.js

# Or open in browser with HTML
<script src="code-on-demand/DynamicLoader.js"></script>
```

---

## 📖 Learning Path

**Recommended Order**:

1. **Start with Client-Server** (`/client-server`)
   - Understand basic separation of concerns
   - See how clients and servers interact

2. **Move to Stateless** (`/stateless`)
   - Learn why storing state is problematic
   - Understand self-contained requests

3. **Study Cacheable** (`/cacheable`)
   - See how caching improves performance
   - Learn cache invalidation strategies

4. **Explore Uniform Interface** (`/uniform-interface`)
   - Understand REST's most important constraint
   - Learn about HATEOAS and resource representations

5. **Understand Layered System** (`/layered-system`)
   - See how layers provide scalability
   - Learn about intermediary components

6. **Optional: Code-On-Demand** (`/code-on-demand`)
   - Understand the only optional constraint
   - See dynamic code loading in action

---

## 🔗 Integration Example

All six constraints work together in a complete RESTful system:

```
┌─────────────────────────────────────────────────────────┐
│  Client (Client-Server)                                  │
│  - Sends stateless requests (Stateless)                  │
│  - Caches responses (Cacheable)                          │
│  - Loads dynamic code (Code-On-Demand)                   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Layered System                                          │
│  ├─ Load Balancer                                        │
│  ├─ API Gateway                                          │
│  ├─ Application Server                                   │
│  ├─ Cache Layer                                          │
│  └─ Database                                             │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Uniform Interface                                       │
│  - Standard URIs (/api/books)                            │
│  - HTTP methods (GET, POST, PUT, DELETE)                 │
│  - Self-descriptive messages (status codes, headers)     │
│  - HATEOAS (hypermedia links)                            │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Key Takeaways

### Must-Have Constraints (1-5):
✅ **Client-Server**: Separate UI from data storage  
✅ **Stateless**: Each request is self-contained  
✅ **Cacheable**: Label responses for caching  
✅ **Layered System**: Use hierarchical layers  
✅ **Uniform Interface**: Standardize communication  

### Optional Constraint (6):
🔷 **Code-On-Demand**: Extend client with server code

### Benefits of RESTful Architecture:
- **Scalability**: Handle millions of clients
- **Simplicity**: Easy to understand and implement
- **Reliability**: Fault-tolerant and recoverable
- **Performance**: Efficient through caching
- **Modifiability**: Easy to evolve independently
- **Portability**: Platform-independent

---

## 📚 Additional Resources

- **REST Dissertation**: Roy Fielding's original paper
- **HTTP RFC 7231**: HTTP/1.1 Semantics and Content
- **REST API Design Rulebook**: O'Reilly
- **Existing Implementation**: See parent directory for full Flask-based library system

---

## 🤝 Contributing

This is an educational project demonstrating RESTful constraints. Feel free to:
- Add more examples
- Improve documentation
- Add examples in other languages (Python, Go, etc.)
- Create integration examples

---

## 📄 License

Educational use - demonstrating RESTful architectural constraints for library management systems.

---

## 💡 Questions & Learning

Each constraint folder contains:
- ✅ Detailed code examples
- ✅ Comments explaining concepts
- ✅ Runnable demonstrations
- ✅ Best practices and anti-patterns

**Happy Learning! 🎓**
