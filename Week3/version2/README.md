# Version 2: Simple Cacheable

## What's New
Version 2 adds **basic caching** to Version 1.

### Key Idea
- Some responses can be cached to make them faster
- GET requests (reading data) = cacheable  
- POST/PUT requests (changing data) = not cacheable

### Simple Changes
1. **Cache GET responses** - store them temporarily
2. **Add Cache-Control headers** - tell client how long to cache
3. **Clear cache when data changes** - keep data fresh

### Benefits
- ✓ Faster responses for repeated requests
- ✓ Less database load
- ✓ Better performance

### How to Run
```bash
python Server.py
python Client.py
```

**Server:** http://127.0.0.1:5001

### Try This
1. GET /api/books (first time = slow, second time = fast from cache)
2. POST /api/books (creates book, clears cache)
3. GET /api/books (fast again, but fresh data)