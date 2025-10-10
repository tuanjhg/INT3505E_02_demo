# Version 3: Simple Uniform Interface

## What's New
Version 3 adds **uniform interface** to Version 2 (keeps all caching features).

### Key Idea
- Use standard HTTP methods consistently
- Add simple HATEOAS links 
- Better error messages
- Standard response format

### Simple Changes
1. **Standard HTTP methods**: GET, POST, PUT, DELETE
2. **HATEOAS links**: Show what actions are available
3. **Better errors**: Clear error messages with status codes
4. **Consistent format**: All responses follow same pattern

### HTTP Methods
- **GET** - Read data (safe, cacheable)
- **POST** - Create new data (not safe, not cacheable)
- **PUT** - Update existing data (not safe, not cacheable)
- **DELETE** - Remove data (not safe, not cacheable)

### Benefits
- ✓ Predictable API behavior
- ✓ Self-describing responses
- ✓ Better error handling
- ✓ Links show available actions
- ✓ All caching from Version 2

### How to Run
```bash
python Server.py
python Client.py
```

**Server:** http://127.0.0.1:5001

### Try This
1. GET /api - see available links
2. GET /api/books - cached list with action links
3. POST /api/books - create with proper status codes
4. PUT /api/books/1 - update existing book
5. DELETE /api/books/1 - remove book