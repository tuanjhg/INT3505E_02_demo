# RESTful Architecture - Library Management System

## Overview

This project demonstrates the **six constraints of RESTful architecture** through a library management system built with Flask. Each constraint is implemented in a separate folder with working code examples, comprehensive documentation, and practical demonstrations.

## Project Structure

```
/LibraryManagementSystem
│
├── /client-server/              # Constraint 1: Client-Server Architecture
│   ├── Client.py               # Client implementation
│   ├── Server.py               # Server implementation
│   └── README.md               # Documentation and explanation
│
├── /stateless/                  # Constraint 2: Stateless Communication
│   ├── StatelessService.py    # Stateless API server
│   ├── StatelessClient.py     # Client demonstrating stateless interaction
│   └── README.md               # Documentation and explanation
│
├── /cacheable/                  # Constraint 3: Cacheable Responses
│   ├── CacheManager.py         # Cache-enabled server
│   ├── CacheClient.py          # Client with cache awareness
│   └── README.md               # Documentation and explanation
│
├── /layered/                    # Constraint 4: Layered System
│   ├── LayeredServer.py        # Three-tier architecture implementation
│   ├── LayeredArchitecture.md  # Detailed architecture documentation
│   └── README.md               # Documentation and explanation
│
├── /uniform-interface/          # Constraint 5: Uniform Interface
│   ├── ApiController.py        # RESTful API with HATEOAS
│   └── README.md               # Documentation and explanation
│
├── /code-on-demand/             # Constraint 6: Code-On-Demand (Optional)
│   ├── DynamicLoader.py        # Server sending executable code
│   └── README.md               # Documentation and explanation
│
└── README.md                    # This file
```

## Six RESTful Constraints

### 1. Client-Server Architecture
**Folder**: `/client-server/`

Separates user interface concerns from data storage concerns. The client handles presentation, while the server manages resources and business logic.

**Key Benefits**:
- Independent evolution of client and server
- Multiple client types can use the same server
- Improved portability across platforms

**Run Demo**:
```bash
cd client-server
python Server.py          # Terminal 1
python Client.py          # Terminal 2
```

---

### 2. Stateless
**Folder**: `/stateless/`

Each request from client to server must contain all information necessary to understand the request. The server does not store client context between requests.

**Key Benefits**:
- Improved scalability (no session storage)
- Better reliability (no session loss)
- Simplified server design

**Run Demo**:
```bash
cd stateless
python StatelessService.py    # Terminal 1
python StatelessClient.py     # Terminal 2
```

---

### 3. Cacheable
**Folder**: `/cacheable/`

Responses must explicitly label themselves as cacheable or non-cacheable to prevent clients from reusing stale or inappropriate data.

**Key Benefits**:
- Improved performance
- Reduced network traffic
- Lower server load

**Run Demo**:
```bash
cd cacheable
python CacheManager.py    # Terminal 1
python CacheClient.py     # Terminal 2
```

---

### 4. Layered System
**Folder**: `/layered/`

The architecture is composed of hierarchical layers, each with specific responsibilities. A client cannot tell whether it is connected directly to the end server or an intermediary.

**Key Benefits**:
- Separation of concerns
- Independent layer testing and scaling
- Support for intermediaries (proxies, load balancers)

**Run Demo**:
```bash
cd layered
python LayeredServer.py
```

---

### 5. Uniform Interface
**Folder**: `/uniform-interface/`

The fundamental feature distinguishing REST from other styles. Consists of four sub-constraints:
1. Identification of resources (URIs)
2. Manipulation through representations (JSON)
3. Self-descriptive messages
4. Hypermedia as the engine of application state (HATEOAS)

**Key Benefits**:
- Simplified architecture
- Improved visibility
- Independent evolution
- Standard methods for all resources

**Run Demo**:
```bash
cd uniform-interface
python ApiController.py
# Open browser: http://127.0.0.1:5005/api
```

---

### 6. Code-On-Demand (Optional)
**Folder**: `/code-on-demand/`

The only **optional** constraint. Allows servers to extend client functionality by transferring executable code (e.g., JavaScript, applets).

**Key Benefits**:
- Reduced client complexity
- Dynamic feature updates
- Centralized logic management

**Run Demo**:
```bash
cd code-on-demand
python DynamicLoader.py
# Open browser: http://127.0.0.1:5006
```

---

## Quick Start

### Prerequisites
```bash
pip install Flask Flask-SQLAlchemy requests
```

### Running All Demos

Each constraint can be tested independently:

1. **Client-Server** (Port 5001):
   ```bash
   cd client-server && python Server.py &
   python Client.py
   ```

2. **Stateless** (Port 5002):
   ```bash
   cd stateless && python StatelessService.py &
   python StatelessClient.py
   ```

3. **Cacheable** (Port 5003):
   ```bash
   cd cacheable && python CacheManager.py &
   python CacheClient.py
   ```

4. **Layered** (Port 5004):
   ```bash
   cd layered && python LayeredServer.py
   ```

5. **Uniform Interface** (Port 5005):
   ```bash
   cd uniform-interface && python ApiController.py
   # Visit: http://127.0.0.1:5005/api
   ```

6. **Code-On-Demand** (Port 5006):
   ```bash
   cd code-on-demand && python DynamicLoader.py
   # Visit: http://127.0.0.1:5006
   ```

## Testing the APIs

### Using curl

```bash
# Client-Server
curl http://127.0.0.1:5001/api/books

# Stateless (requires authentication)
curl http://127.0.0.1:5002/api/books \
  -H "Authorization: Bearer <api_key>"

# Cacheable
curl -v http://127.0.0.1:5003/api/books
# Check Cache-Control and ETag headers

# Layered
curl http://127.0.0.1:5004/api/books

# Uniform Interface (with HATEOAS)
curl http://127.0.0.1:5005/api
curl http://127.0.0.1:5005/api/books/1

# Code-On-Demand
curl http://127.0.0.1:5006/api/validation/isbn.js
```

### Using Python

```python
import requests

# Example: Testing uniform interface
response = requests.get('http://127.0.0.1:5005/api/books/1')
data = response.json()

# Access HATEOAS links
self_link = data['data']['_links']['self']
print(f"Book URL: {self_link['href']}")
```

## Learning Path

For the best learning experience, explore the constraints in this order:

1. **Client-Server** - Understand the basic separation
2. **Uniform Interface** - Learn RESTful API design
3. **Stateless** - Understand stateless communication
4. **Cacheable** - Learn performance optimization
5. **Layered** - Understand architectural organization
6. **Code-On-Demand** - Explore advanced optional feature

## Key Concepts Summary

| Constraint | Required? | Key Benefit | Example |
|------------|-----------|-------------|---------|
| Client-Server | ✓ | Separation of concerns | Web browser + API server |
| Stateless | ✓ | Scalability | Token-based auth |
| Cacheable | ✓ | Performance | Cache-Control headers |
| Layered | ✓ | Flexibility | 3-tier architecture |
| Uniform Interface | ✓ | Simplicity | HTTP methods, HATEOAS |
| Code-On-Demand | ✗ (Optional) | Extensibility | JavaScript loading |

## RESTful Best Practices Demonstrated

### ✓ DO:
- Use standard HTTP methods (GET, POST, PUT, DELETE)
- Use meaningful URIs (/api/books/1, not /api/getBook?id=1)
- Return appropriate status codes (200, 201, 404, etc.)
- Include proper headers (Content-Type, Cache-Control)
- Provide HATEOAS links for discoverability
- Keep servers stateless
- Make responses cacheable when appropriate

### ✗ DON'T:
- Store session state on server (violates stateless)
- Use verbs in URIs (/api/deleteBook)
- Return 200 for errors
- Cache write operations
- Skip layers in layered architecture
- Execute untrusted code on demand

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with Flask-SQLAlchemy
- **HTTP Client**: Python requests library
- **Code-On-Demand**: JavaScript

## Further Reading

Each folder contains detailed README files with:
- Theoretical explanations
- Practical examples
- Code walkthrough
- Best practices
- Real-world applications

Start with any constraint folder and explore the README.md for in-depth information.

## Author Notes

This project was created to demonstrate RESTful architecture principles in a practical, hands-on way. Each constraint is isolated to make it easier to understand individually, but in production systems, all constraints work together to create robust, scalable APIs.

## License

This is an educational project demonstrating RESTful architecture principles.

---

**Happy Learning! 🚀**

For questions or issues, please refer to the individual README files in each constraint folder.
