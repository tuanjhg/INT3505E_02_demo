/**
 * CACHEABLE CONSTRAINT
 * 
 * Responses must implicitly or explicitly label themselves as cacheable or non-cacheable.
 * If cacheable, the client can reuse the response data for equivalent requests.
 * 
 * Benefits:
 * - Efficiency: Reduces network traffic and server load
 * - Performance: Faster response times for cached data
 * - Scalability: Fewer requests reach the server
 * 
 * Implementation:
 * - Use HTTP cache headers (Cache-Control, ETag, Last-Modified)
 * - Mark responses as cacheable or non-cacheable
 * - Implement cache invalidation strategies
 */

import java.util.*;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import org.json.JSONObject;

public class CacheManager {
    
    // Simple in-memory cache
    private Map<String, CacheEntry> cache = new HashMap<>();
    
    /**
     * CACHEABLE: Get all books
     * 
     * Book catalog changes infrequently, so it's highly cacheable.
     * Cache for 5 minutes to reduce database queries.
     */
    public Response getBooks() {
        String cacheKey = "books:all";
        
        // Check if we have valid cached data
        CacheEntry cached = cache.get(cacheKey);
        if (cached != null && !cached.isExpired()) {
            System.out.println("Cache HIT: Returning cached books");
            return createCacheableResponse(
                cached.data,
                "Cache hit",
                300,  // Cache for 5 minutes (300 seconds)
                cached.etag
            );
        }
        
        // Cache MISS: Fetch from database
        System.out.println("Cache MISS: Fetching books from database");
        JSONObject books = fetchBooksFromDatabase();
        
        // Generate ETag (entity tag) for cache validation
        String etag = generateETag(books);
        
        // Store in cache
        cache.put(cacheKey, new CacheEntry(books, 300, etag));
        
        return createCacheableResponse(books, "Fetched from database", 300, etag);
    }

    /**
     * CACHEABLE: Get specific book by ID
     * 
     * Individual book data is cacheable with conditional requests support.
     */
    public Response getBook(int bookId, String clientETag) {
        String cacheKey = "book:" + bookId;
        
        // Check cache
        CacheEntry cached = cache.get(cacheKey);
        if (cached != null && !cached.isExpired()) {
            // Client provided ETag - check if data changed
            if (clientETag != null && clientETag.equals(cached.etag)) {
                System.out.println("ETag match: Data not modified");
                return createNotModifiedResponse(cached.etag);
            }
            
            return createCacheableResponse(cached.data, "Cache hit", 600, cached.etag);
        }
        
        // Fetch from database
        JSONObject book = fetchBookFromDatabase(bookId);
        if (book == null) {
            return createNonCacheableResponse("Book not found", 404);
        }
        
        String etag = generateETag(book);
        cache.put(cacheKey, new CacheEntry(book, 600, etag));
        
        return createCacheableResponse(book, "Book retrieved", 600, etag);
    }

    /**
     * NON-CACHEABLE: Borrow book
     * 
     * POST/PUT/DELETE operations should NOT be cached as they modify state.
     * Each borrow operation must be processed by the server.
     */
    public Response borrowBook(int bookId, String borrowerName, String borrowerEmail, int days) {
        // Process the borrow operation
        JSONObject result = processBorrowOperation(bookId, borrowerName, borrowerEmail, days);
        
        // Invalidate related caches
        invalidateCache("books:all");           // Book list changed (availability)
        invalidateCache("book:" + bookId);      // Specific book changed
        invalidateCache("books:available");     // Available books list changed
        
        // Return NON-cacheable response
        return createNonCacheableResponse(result, 201);
    }

    /**
     * CONDITIONALLY CACHEABLE: Search results
     * 
     * Search results can be cached for a short time, but with lower TTL
     * since results may change more frequently.
     */
    public Response searchBooks(String query) {
        String cacheKey = "search:" + query.toLowerCase();
        
        CacheEntry cached = cache.get(cacheKey);
        if (cached != null && !cached.isExpired()) {
            return createCacheableResponse(
                cached.data, 
                "Cached search results", 
                60,  // Only cache for 1 minute
                cached.etag
            );
        }
        
        JSONObject results = performSearch(query);
        String etag = generateETag(results);
        cache.put(cacheKey, new CacheEntry(results, 60, etag));
        
        return createCacheableResponse(results, "Fresh search results", 60, etag);
    }

    /**
     * NON-CACHEABLE: Get overdue books
     * 
     * Time-sensitive data should not be cached or have very short TTL.
     * Overdue status changes as time passes.
     */
    public Response getOverdueBooks() {
        JSONObject overdueBooks = fetchOverdueBooks();
        
        // Mark as non-cacheable or very short cache (e.g., 10 seconds)
        return createCacheableResponse(
            overdueBooks,
            "Current overdue books",
            10,  // Very short cache time
            null
        );
    }

    /**
     * Cache invalidation when data is modified
     */
    public void invalidateCache(String cacheKey) {
        cache.remove(cacheKey);
        System.out.println("Cache invalidated: " + cacheKey);
    }

    /**
     * Create a cacheable response with appropriate headers
     */
    private Response createCacheableResponse(JSONObject data, String message, 
                                            int maxAgeSeconds, String etag) {
        Response response = new Response();
        response.statusCode = 200;
        response.body = data;
        response.headers.put("Cache-Control", "max-age=" + maxAgeSeconds + ", public");
        if (etag != null) {
            response.headers.put("ETag", etag);
        }
        response.headers.put("Last-Modified", Instant.now().toString());
        response.cacheable = true;
        
        System.out.println("Response: CACHEABLE for " + maxAgeSeconds + " seconds");
        return response;
    }

    /**
     * Create a non-cacheable response
     */
    private Response createNonCacheableResponse(Object data, int statusCode) {
        Response response = new Response();
        response.statusCode = statusCode;
        response.body = data;
        response.headers.put("Cache-Control", "no-cache, no-store, must-revalidate");
        response.headers.put("Pragma", "no-cache");
        response.headers.put("Expires", "0");
        response.cacheable = false;
        
        System.out.println("Response: NON-CACHEABLE");
        return response;
    }

    /**
     * Create 304 Not Modified response when ETag matches
     */
    private Response createNotModifiedResponse(String etag) {
        Response response = new Response();
        response.statusCode = 304;
        response.body = null;
        response.headers.put("ETag", etag);
        response.cacheable = true;
        
        System.out.println("Response: 304 Not Modified (use cached version)");
        return response;
    }

    // Helper methods
    private JSONObject fetchBooksFromDatabase() {
        JSONObject result = new JSONObject();
        result.put("books", new ArrayList<>());
        return result;
    }

    private JSONObject fetchBookFromDatabase(int bookId) {
        JSONObject book = new JSONObject();
        book.put("id", bookId);
        book.put("title", "Sample Book");
        return book;
    }

    private JSONObject processBorrowOperation(int bookId, String name, String email, int days) {
        JSONObject result = new JSONObject();
        result.put("success", true);
        result.put("borrow_id", 123);
        return result;
    }

    private JSONObject performSearch(String query) {
        return new JSONObject();
    }

    private JSONObject fetchOverdueBooks() {
        return new JSONObject();
    }

    private String generateETag(Object data) {
        // Generate hash of data as ETag
        return "\"" + Integer.toHexString(data.hashCode()) + "\"";
    }

    // Cache entry class
    static class CacheEntry {
        JSONObject data;
        Instant expiresAt;
        String etag;

        CacheEntry(JSONObject data, int ttlSeconds, String etag) {
            this.data = data;
            this.expiresAt = Instant.now().plus(ttlSeconds, ChronoUnit.SECONDS);
            this.etag = etag;
        }

        boolean isExpired() {
            return Instant.now().isAfter(expiresAt);
        }
    }

    // Response class
    static class Response {
        int statusCode;
        Object body;
        Map<String, String> headers = new HashMap<>();
        boolean cacheable;
    }

    /**
     * Example demonstrating cache behavior
     */
    public static void main(String[] args) throws InterruptedException {
        CacheManager cacheManager = new CacheManager();
        
        System.out.println("=== Cacheable Library API ===\n");
        
        // First request - cache miss
        System.out.println("--- Request 1: Get all books ---");
        cacheManager.getBooks();
        
        System.out.println("\n--- Request 2: Get all books (immediate) ---");
        // Second request - cache hit
        cacheManager.getBooks();
        
        System.out.println("\n--- Request 3: Borrow a book ---");
        // Modify operation - not cached, invalidates related caches
        cacheManager.borrowBook(1, "John Doe", "john@example.com", 14);
        
        System.out.println("\n--- Request 4: Get all books (after modification) ---");
        // Cache was invalidated, so this is a miss
        cacheManager.getBooks();
        
        System.out.println("\n--- Request 5: Get specific book with ETag ---");
        Response response = cacheManager.getBook(1, null);
        String etag = response.headers.get("ETag");
        
        System.out.println("\n--- Request 6: Get same book with matching ETag ---");
        // Client provides ETag - server returns 304 Not Modified
        cacheManager.getBook(1, etag);
        
        System.out.println("\n--- Request 7: Get overdue books ---");
        // Time-sensitive data with short cache time
        cacheManager.getOverdueBooks();
        
        System.out.println("\nCaching improves performance and reduces server load!");
    }
}
