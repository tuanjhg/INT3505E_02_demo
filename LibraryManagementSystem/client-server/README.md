# Client-Server Architecture

## RESTful Constraint #1: Client-Server

### Overview
The client-server constraint establishes a separation of concerns between the user interface (client) and data storage/business logic (server). This architectural style allows both components to evolve independently.

### Key Principles
1. **Separation of Concerns**: Client handles presentation, server handles data and logic
2. **Independent Evolution**: Client and server can be updated separately
3. **Multiple Clients**: One server can support web, mobile, and desktop clients
4. **Portability**: Improves portability of the user interface across platforms

### In This Library Management System

#### Server Side (`Server.py`)
- Manages book resources and database
- Implements business logic (validation, ISBN uniqueness)
- Exposes RESTful API endpoints
- Independent of client implementation

**Key Features:**
- `/api/books` - List all books
- `/api/books` (POST) - Create new book
- `/api/books/<id>` - Get specific book
- `/api/health` - Server health check

#### Client Side (`Client.py`)
- Focuses on user interaction and presentation
- Consumes server APIs
- No business logic or database access
- Can be replaced with different client types

**Key Features:**
- Simple Python client using requests library
- Methods for all server operations
- User-friendly display formatting
- Error handling and server connectivity checks

### How to Run

1. **Start the Server:**
```bash
python Server.py
```
Server will run on http://127.0.0.1:5001

2. **Run the Client (in a new terminal):**
```bash
python Client.py
```

### Benefits Demonstrated
- ✓ Clean separation between UI and business logic
- ✓ Server can be replaced without affecting client
- ✓ Client can be replaced (e.g., web UI, mobile app) without server changes
- ✓ Multiple clients can use the same server simultaneously
- ✓ Each component can scale independently

### Real-World Application
In production:
- Server might be deployed on cloud infrastructure
- Multiple client types: web browser, mobile app, CLI tool
- Server handles authentication, authorization, data validation
- Clients focus on user experience and presentation
