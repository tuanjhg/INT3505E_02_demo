/**
 * STATELESS CONSTRAINT
 * 
 * Each request from client to server must contain ALL information necessary to understand
 * the request. The server does NOT store client context between requests.
 * 
 * Benefits:
 * - Visibility: Monitoring systems can understand requests in isolation
 * - Reliability: Easy to recover from failures
 * - Scalability: Server doesn't need to manage session state
 * 
 * Implementation:
 * - No session data stored on server
 * - Each request includes authentication/authorization data
 * - Client maintains application state
 */

import java.util.*;
import org.json.JSONObject;

public class StatelessService {
    
    /**
     * STATELESS EXAMPLE: Search Books
     * 
     * Each request contains all necessary information (search query, filters).
     * Server doesn't remember previous searches or user preferences.
     */
    public JSONObject searchBooks(String searchQuery, String filterBy, String authToken) {
        // Validate auth token in THIS request (no session stored)
        if (!isValidToken(authToken)) {
            return createErrorResponse("Invalid authentication token");
        }
        
        // ALL search parameters are provided in the request
        // Server doesn't remember what user searched for before
        List<Book> results = performSearch(searchQuery, filterBy);
        
        JSONObject response = new JSONObject();
        response.put("success", true);
        response.put("query", searchQuery);  // Echo back for client reference
        response.put("filter", filterBy);
        response.put("results", results.size());
        response.put("message", "Search completed successfully");
        
        return response;
        // No state saved on server after response is sent
    }

    /**
     * STATELESS EXAMPLE: Borrow Book
     * 
     * Request includes ALL information needed:
     * - Book ID (what to borrow)
     * - Borrower details (who is borrowing)
     * - Duration (how long)
     * - Authentication (authorization to borrow)
     */
    public JSONObject borrowBook(int bookId, String borrowerName, String borrowerEmail, 
                                  int days, String authToken) {
        // Authenticate THIS request (no remembered login session)
        if (!isValidToken(authToken)) {
            return createErrorResponse("Authentication required");
        }
        
        // Validate that user has permission (from token, not stored session)
        if (!hasPermission(authToken, "borrow_books")) {
            return createErrorResponse("Insufficient permissions");
        }
        
        // All business logic parameters provided in request
        if (days < 1 || days > 30) {
            return createErrorResponse("Borrow period must be between 1 and 30 days");
        }
        
        // Process the complete request
        BorrowRecord record = createBorrowRecord(bookId, borrowerName, borrowerEmail, days);
        
        JSONObject response = new JSONObject();
        response.put("success", true);
        response.put("message", "Book borrowed successfully");
        response.put("borrow_id", record.getId());
        response.put("due_date", record.getDueDate());
        
        return response;
        // Server forgets everything about this request after response
    }

    /**
     * STATELESS EXAMPLE: Get Borrow History
     * 
     * Client must provide:
     * - User identifier (in token or parameter)
     * - Pagination info (page number, page size)
     * - Filter criteria (if any)
     * 
     * Server doesn't remember "where the user left off" in pagination
     */
    public JSONObject getBorrowHistory(String borrowerEmail, int page, int pageSize, 
                                       String authToken) {
        // Validate auth for THIS request
        if (!isValidToken(authToken)) {
            return createErrorResponse("Authentication required");
        }
        
        // Verify token owner matches requested email (or has admin rights)
        if (!canAccessBorrowerData(authToken, borrowerEmail)) {
            return createErrorResponse("Access denied");
        }
        
        // ALL pagination state provided by client
        List<BorrowRecord> history = fetchBorrowHistory(borrowerEmail, page, pageSize);
        int totalRecords = countBorrowRecords(borrowerEmail);
        
        JSONObject response = new JSONObject();
        response.put("success", true);
        response.put("borrower", borrowerEmail);
        response.put("page", page);              // Echo back current page
        response.put("page_size", pageSize);     // Echo back page size
        response.put("total_records", totalRecords);
        response.put("total_pages", (totalRecords + pageSize - 1) / pageSize);
        response.put("data", history);
        
        // Client decides which page to request next
        // Server doesn't track "current page" for this user
        return response;
    }

    /**
     * COUNTER-EXAMPLE: What NOT to do (Stateful approach)
     * 
     * This violates the stateless constraint:
     */
    /*
    // DON'T DO THIS - Server storing client state
    private Map<String, UserSession> sessions = new HashMap<>();
    
    public JSONObject statefulSearch(String query, String sessionId) {
        UserSession session = sessions.get(sessionId);
        session.lastSearch = query;           // Storing client state
        session.currentPage = 1;              // Tracking pagination
        session.preferences.addRecent(query); // Remembering user activity
        // ... This makes the server stateful!
    }
    */

    /**
     * Authentication token validation
     * Token contains ALL necessary auth info (user ID, permissions, expiry)
     * No session storage needed
     */
    private boolean isValidToken(String token) {
        // In real implementation: verify JWT signature, check expiry, etc.
        // All auth info is IN the token itself
        return token != null && token.startsWith("Bearer ");
    }

    private boolean hasPermission(String token, String permission) {
        // Extract permissions from token (not from stored session)
        // JWT tokens can contain claims about user permissions
        return true; // Simplified for example
    }

    private boolean canAccessBorrowerData(String token, String borrowerEmail) {
        // Check if token's user matches borrower or has admin role
        // All info comes from the token, not stored session
        return true; // Simplified for example
    }

    // Helper methods (database operations)
    private List<Book> performSearch(String query, String filter) {
        // Database query - returns results for THIS request only
        return new ArrayList<>();
    }

    private BorrowRecord createBorrowRecord(int bookId, String name, String email, int days) {
        return new BorrowRecord(1, bookId, name, email, days);
    }

    private List<BorrowRecord> fetchBorrowHistory(String email, int page, int pageSize) {
        return new ArrayList<>();
    }

    private int countBorrowRecords(String email) {
        return 0;
    }

    private JSONObject createErrorResponse(String message) {
        JSONObject response = new JSONObject();
        response.put("success", false);
        response.put("message", message);
        return response;
    }

    // Domain classes
    static class Book {
        int id;
        String title;
        String author;
    }

    static class BorrowRecord {
        private int id;
        private int bookId;
        private String borrowerName;
        private String borrowerEmail;
        private int days;
        private String dueDate;

        BorrowRecord(int id, int bookId, String name, String email, int days) {
            this.id = id;
            this.bookId = bookId;
            this.borrowerName = name;
            this.borrowerEmail = email;
            this.days = days;
            this.dueDate = "2024-12-31"; // Calculated
        }

        public int getId() { return id; }
        public String getDueDate() { return dueDate; }
    }

    /**
     * Example usage demonstrating stateless requests
     */
    public static void main(String[] args) {
        StatelessService service = new StatelessService();
        
        String authToken = "Bearer eyJhbGc..."; // Example JWT token
        
        System.out.println("=== Stateless Library Service ===\n");
        
        // Each request is independent and contains all necessary information
        System.out.println("Request 1: Search books");
        service.searchBooks("REST API", "programming", authToken);
        
        System.out.println("\nRequest 2: Borrow book");
        service.borrowBook(1, "Jane Smith", "jane@example.com", 14, authToken);
        
        System.out.println("\nRequest 3: Get history - page 1");
        service.getBorrowHistory("jane@example.com", 1, 10, authToken);
        
        System.out.println("\nRequest 4: Get history - page 2");
        // Client provides page number - server doesn't remember we were on page 1
        service.getBorrowHistory("jane@example.com", 2, 10, authToken);
        
        System.out.println("\nEach request is complete and self-contained!");
    }
}
