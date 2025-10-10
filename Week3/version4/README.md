# Version 4: Simple Stateless

## What's New
Version 4 adds **stateless** to Version 3 (keeps caching, uniform interface).

### Key Idea
- Server doesn't remember anything about clients
- Each request must include all needed information
- Use API keys instead of sessions
- No server-side session storage

### Simple Changes
1. **No sessions**: Server doesn't store client state
2. **API keys**: Simple authentication with each request
3. **Self-contained requests**: Each request has everything needed
4. **Stateless authentication**: Bearer token in every request

### Authentication
- Client gets API key: `POST /api/auth`
- Include in every request: `Authorization: Bearer <key>`
- Server extracts user info from key (no session lookup)

### Benefits
- ✓ Better scalability (no session storage)
- ✓ Simpler server (no session management)
- ✓ Easy load balancing (any server can handle any request)
- ✓ All features from Versions 1-3

### How to Run
```bash
python Server.py
python Client.py
```

**Server:** http://127.0.0.1:5001

### Try This
1. POST /api/auth - get API key
2. GET /api/books (with Authorization header)
3. All requests need the Authorization header
4. Server never stores session data