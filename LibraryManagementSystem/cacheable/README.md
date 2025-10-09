# Cacheable Architecture

## RESTful Constraint #3: Cacheable

### Overview
The cacheable constraint requires that responses must implicitly or explicitly label themselves as cacheable or non-cacheable. When a response is cacheable, the client can reuse that response data for equivalent subsequent requests, improving performance.

### Key Principles
1. **Explicit Cacheability**: Responses clearly indicate if they can be cached
2. **Cache Control**: HTTP headers define caching behavior
3. **Performance Optimization**: Reduce latency and server load
4. **Cache Validation**: ETags allow checking if cached data is still fresh

### In This Library Management System

#### Cache Manager (`CacheManager.py`)
Implements caching at the server level with:
- **Cache-Control headers**: Define caching policy
- **ETags**: Enable cache validation
- **Cache decorators**: Easily mark endpoints as cacheable/non-cacheable
- **Smart invalidation**: Clear cache when data changes

**Cacheable Endpoints:**
- `GET /api/books` - List all books (5 min cache)
- `GET /api/books/<id>` - Single book (10 min cache)
- `GET /api/books/available` - Available books (1 min cache)

**Non-Cacheable Endpoints:**
- `POST /api/books` - Create book (write operation)
- `PUT /api/books/<id>` - Update book (write operation)
- `GET /api/stats/realtime` - Real-time stats (must be fresh)

#### Cache Client (`CacheClient.py`)
Demonstrates client-side cache utilization:
- Respects Cache-Control headers
- Implements client-side caching
- Uses ETags for validation
- Shows performance benefits

### HTTP Caching Headers

#### Cache-Control
```
Cache-Control: public, max-age=300
```
- `public`: Can be cached by any cache
- `private`: Only client browser can cache
- `no-store`: Must not be cached at all
- `no-cache`: Can cache but must validate before use
- `max-age=N`: Cache valid for N seconds

#### ETag (Entity Tag)
```
ETag: "abc123def456"
```
- Unique identifier for resource version
- Client sends in `If-None-Match` header
- Server returns `304 Not Modified` if unchanged

#### Age
```
Age: 45
```
- How long response has been in cache (seconds)

### Caching Strategy

```python
# CACHEABLE - Data doesn't change often
@cacheable(max_age=300)
def get_books():
    books = Book.query.all()
    return books

# NON-CACHEABLE - Write operation
@no_cache
def create_book():
    book = Book(...)
    db.session.add(book)
    db.session.commit()
    invalidate_cache()  # Clear related caches
    return book
```

### How to Run

1. **Start the Cache-Enabled Server:**
```bash
python CacheManager.py
```
Server runs on http://127.0.0.1:5003

2. **Run the Cache Demo:**
```bash
python CacheClient.py
```

### Performance Impact

**Without Caching:**
```
Request 1: GET /api/books → 150ms (database query)
Request 2: GET /api/books → 150ms (database query)
Request 3: GET /api/books → 150ms (database query)
Total: 450ms + 3× database load
```

**With Caching:**
```
Request 1: GET /api/books → 150ms (database query, cached)
Request 2: GET /api/books → 1ms (from cache)
Request 3: GET /api/books → 1ms (from cache)
Total: 152ms + 1× database load
```

### Cache Invalidation

When data changes:
```python
def update_book(book_id):
    # Update database
    book.title = "New Title"
    db.session.commit()
    
    # Invalidate affected caches
    invalidate_book_caches()
```

### Benefits Demonstrated

✓ **Reduced Latency**: Cached responses served instantly
✓ **Lower Server Load**: Fewer database queries
✓ **Bandwidth Savings**: 304 responses are tiny
✓ **Better Scalability**: Serve more users with same resources
✓ **Improved UX**: Faster page loads

### Cache Layers

1. **Client Cache**: Browser/app caches responses
2. **CDN Cache**: Content delivery network
3. **Server Cache**: Application-level caching (Redis, Memcached)
4. **Database Cache**: Query result caching

### When to Cache

**DO Cache (GET requests for):**
- ✓ Static content
- ✓ Infrequently changing data
- ✓ List/collection endpoints
- ✓ Public data

**DON'T Cache:**
- ✗ POST/PUT/DELETE operations
- ✗ User-specific sensitive data
- ✗ Real-time data
- ✗ Dynamic calculations

### Real-World Caching

**Production Tools:**
- **Redis**: In-memory cache
- **Memcached**: Distributed caching
- **Varnish**: HTTP accelerator
- **CloudFlare/Akamai**: CDN with edge caching

**Best Practices:**
- Set appropriate `max-age` based on data volatility
- Use ETags for validation
- Implement cache invalidation on writes
- Consider cache warming for critical data
- Monitor cache hit rates
- Use cache-busting for critical updates
