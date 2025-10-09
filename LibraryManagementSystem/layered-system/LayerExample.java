/**
 * LAYERED SYSTEM CONSTRAINT - Code Example
 * 
 * Demonstrates how layers interact in the library management system.
 * Each layer only knows about the layer immediately below it.
 */

// ==================== DATA LAYER ====================
// Bottom layer - knows nothing about upper layers
class DatabaseLayer {
    public List<Book> queryBooks(String sql) {
        System.out.println("[DATABASE] Executing query: " + sql);
        // Simulate database query
        List<Book> books = new ArrayList<>();
        books.add(new Book(1, "Clean Code", "Robert Martin", true));
        return books;
    }
    
    public void executeUpdate(String sql) {
        System.out.println("[DATABASE] Executing update: " + sql);
    }
}

// ==================== CACHE LAYER ====================
// Knows about: Database Layer only
class CacheLayer {
    private DatabaseLayer database;
    private Map<String, Object> cache = new HashMap<>();
    
    public CacheLayer(DatabaseLayer database) {
        this.database = database;
    }
    
    public List<Book> getAvailableBooks() {
        String cacheKey = "available_books";
        
        // Check cache first
        if (cache.containsKey(cacheKey)) {
            System.out.println("[CACHE] Cache HIT for: " + cacheKey);
            return (List<Book>) cache.get(cacheKey);
        }
        
        // Cache miss - query database
        System.out.println("[CACHE] Cache MISS for: " + cacheKey);
        List<Book> books = database.queryBooks("SELECT * FROM books WHERE available = true");
        
        // Store in cache
        cache.put(cacheKey, books);
        return books;
    }
    
    public void invalidateCache(String key) {
        System.out.println("[CACHE] Invalidating: " + key);
        cache.remove(key);
    }
}

// ==================== APPLICATION LAYER ====================
// Knows about: Cache Layer (which abstracts database access)
// Doesn't know: Whether data comes from cache or database
class ApplicationLayer {
    private CacheLayer cacheLayer;
    
    public ApplicationLayer(CacheLayer cacheLayer) {
        this.cacheLayer = cacheLayer;
    }
    
    public Response getAvailableBooks() {
        System.out.println("[APPLICATION] Processing request: Get available books");
        
        try {
            // Application doesn't know if this hits cache or database!
            List<Book> books = cacheLayer.getAvailableBooks();
            
            return new Response(200, "Success", books);
        } catch (Exception e) {
            return new Response(500, "Internal server error", null);
        }
    }
    
    public Response borrowBook(int bookId, String borrowerName) {
        System.out.println("[APPLICATION] Processing request: Borrow book " + bookId);
        
        // Business logic here
        // When data is modified, invalidate cache
        cacheLayer.invalidateCache("available_books");
        
        return new Response(201, "Book borrowed successfully", null);
    }
}

// ==================== API GATEWAY LAYER ====================
// Knows about: Application Layer
// Doesn't know: About cache or database implementation
class ApiGatewayLayer {
    private ApplicationLayer application;
    private Map<String, Integer> rateLimits = new HashMap<>();
    
    public ApiGatewayLayer(ApplicationLayer application) {
        this.application = application;
    }
    
    public Response handleRequest(Request request) {
        System.out.println("[GATEWAY] Received request: " + request.path);
        
        // Authentication
        if (!authenticate(request.token)) {
            System.out.println("[GATEWAY] Authentication failed");
            return new Response(401, "Unauthorized", null);
        }
        
        // Rate limiting
        if (!checkRateLimit(request.clientId)) {
            System.out.println("[GATEWAY] Rate limit exceeded");
            return new Response(429, "Too many requests", null);
        }
        
        // Route to application
        System.out.println("[GATEWAY] Forwarding to application layer");
        return application.getAvailableBooks();
    }
    
    private boolean authenticate(String token) {
        // Validate token
        return token != null && token.startsWith("Bearer");
    }
    
    private boolean checkRateLimit(String clientId) {
        // Simple rate limiting
        int count = rateLimits.getOrDefault(clientId, 0);
        if (count >= 100) {
            return false;
        }
        rateLimits.put(clientId, count + 1);
        return true;
    }
}

// ==================== LOAD BALANCER LAYER ====================
// Knows about: Multiple API Gateway instances
// Distributes load across them
class LoadBalancerLayer {
    private List<ApiGatewayLayer> gateways;
    private int currentIndex = 0;
    
    public LoadBalancerLayer(List<ApiGatewayLayer> gateways) {
        this.gateways = gateways;
    }
    
    public Response distributeRequest(Request request) {
        System.out.println("[LOAD BALANCER] Distributing request");
        
        // Round-robin load balancing
        ApiGatewayLayer selectedGateway = gateways.get(currentIndex);
        currentIndex = (currentIndex + 1) % gateways.size();
        
        System.out.println("[LOAD BALANCER] Routing to gateway " + (currentIndex));
        return selectedGateway.handleRequest(request);
    }
}

// ==================== CLIENT LAYER ====================
// Knows about: Load Balancer endpoint only
// Doesn't know: About gateways, applications, caches, or databases
class ClientLayer {
    private String apiEndpoint = "https://library.com/api";
    private LoadBalancerLayer loadBalancer;
    
    public ClientLayer(LoadBalancerLayer loadBalancer) {
        this.loadBalancer = loadBalancer;
    }
    
    public void getAvailableBooks(String authToken) {
        System.out.println("[CLIENT] Requesting available books from: " + apiEndpoint);
        
        Request request = new Request();
        request.path = "/api/books/available";
        request.token = authToken;
        request.clientId = "client-123";
        
        // Client sends request - doesn't know about all the layers it goes through
        Response response = loadBalancer.distributeRequest(request);
        
        System.out.println("[CLIENT] Received response: " + response.statusCode + " - " + response.message);
    }
}

// ==================== SUPPORTING CLASSES ====================

class Book {
    int id;
    String title;
    String author;
    boolean available;
    
    Book(int id, String title, String author, boolean available) {
        this.id = id;
        this.title = title;
        this.author = author;
        this.available = available;
    }
}

class Request {
    String path;
    String token;
    String clientId;
}

class Response {
    int statusCode;
    String message;
    Object data;
    
    Response(int statusCode, String message, Object data) {
        this.statusCode = statusCode;
        this.message = message;
        this.data = data;
    }
}

// ==================== MAIN DEMONSTRATION ====================

public class LayerExample {
    public static void main(String[] args) {
        System.out.println("=== Layered System Architecture Demo ===\n");
        
        // Build the layers from bottom to top
        // Each layer only knows about the layer below it
        
        System.out.println("Building layered architecture...\n");
        
        // Layer 1: Database (bottom layer)
        DatabaseLayer database = new DatabaseLayer();
        
        // Layer 2: Cache (knows about database)
        CacheLayer cache = new CacheLayer(database);
        
        // Layer 3: Application (knows about cache)
        ApplicationLayer app1 = new ApplicationLayer(cache);
        ApplicationLayer app2 = new ApplicationLayer(cache);
        
        // Layer 4: API Gateway (knows about application)
        ApiGatewayLayer gateway1 = new ApiGatewayLayer(app1);
        ApiGatewayLayer gateway2 = new ApiGatewayLayer(app2);
        
        // Layer 5: Load Balancer (knows about gateways)
        List<ApiGatewayLayer> gateways = Arrays.asList(gateway1, gateway2);
        LoadBalancerLayer loadBalancer = new LoadBalancerLayer(gateways);
        
        // Layer 6: Client (top layer - knows about load balancer endpoint only)
        ClientLayer client = new ClientLayer(loadBalancer);
        
        // Execute requests
        System.out.println("=== Request 1: Client fetches available books ===");
        client.getAvailableBooks("Bearer valid-token");
        
        System.out.println("\n=== Request 2: Same request (will hit cache) ===");
        client.getAvailableBooks("Bearer valid-token");
        
        System.out.println("\n=== Key Points ===");
        System.out.println("✓ Client doesn't know about cache or database");
        System.out.println("✓ Gateway doesn't know about cache implementation");
        System.out.println("✓ Application doesn't know if data comes from cache or DB");
        System.out.println("✓ Each layer can be modified independently");
        System.out.println("✓ Intermediate layers (cache, gateway) can be added/removed transparently");
    }
}
