/**
 * UNIFORM INTERFACE CONSTRAINT
 * 
 * The uniform interface is the fundamental constraint that distinguishes REST from other
 * network-based architectural styles. It simplifies and decouples the architecture.
 * 
 * Four sub-constraints:
 * 1. Identification of resources (URI)
 * 2. Manipulation of resources through representations (HTTP methods + JSON/XML)
 * 3. Self-descriptive messages (HTTP headers, status codes)
 * 4. Hypermedia as the engine of application state (HATEOAS)
 * 
 * Benefits:
 * - Simplified architecture
 * - Improved visibility of interactions
 * - Independent evolution of components
 * - Encourages implementation reusability
 */

import java.util.*;
import org.json.JSONObject;
import org.json.JSONArray;

public class ApiController {
    
    // ==================== SUB-CONSTRAINT 1: Resource Identification ====================
    /**
     * Resources are identified by URIs (Uniform Resource Identifiers)
     * Each resource has a unique, meaningful URI
     */
    public static class ResourceUris {
        // Collection resources
        public static final String BOOKS = "/api/books";
        public static final String BORROWS = "/api/borrows";
        
        // Individual resources (with ID parameter)
        public static final String BOOK_BY_ID = "/api/books/{id}";
        public static final String BORROW_BY_ID = "/api/borrows/{id}";
        
        // Sub-resources
        public static final String AVAILABLE_BOOKS = "/api/books/available";
        public static final String OVERDUE_BORROWS = "/api/borrows/overdue";
        
        // Resource actions
        public static final String RETURN_BOOK = "/api/borrows/{id}/return";
        public static final String EXTEND_BORROW = "/api/borrows/{id}/extend";
    }
    
    // ==================== SUB-CONSTRAINT 2: Resource Representations ====================
    /**
     * Resources are manipulated through representations
     * Use standard HTTP methods for operations
     * 
     * GET    - Retrieve resource(s)
     * POST   - Create new resource
     * PUT    - Update/replace resource
     * PATCH  - Partial update
     * DELETE - Remove resource
     */
    
    /**
     * GET /api/books - Retrieve all books
     */
    public Response getAllBooks() {
        List<BookRepresentation> books = fetchAllBooks();
        
        JSONArray booksArray = new JSONArray();
        for (BookRepresentation book : books) {
            booksArray.put(book.toJSON());
        }
        
        return createResponse(200, "application/json", booksArray);
    }
    
    /**
     * GET /api/books/{id} - Retrieve specific book
     */
    public Response getBook(int id) {
        BookRepresentation book = fetchBookById(id);
        
        if (book == null) {
            return createErrorResponse(404, "Book not found");
        }
        
        return createResponse(200, "application/json", book.toJSON());
    }
    
    /**
     * POST /api/books - Create new book
     * Client sends representation of book to create
     */
    public Response createBook(String requestBody) {
        JSONObject bookData = new JSONObject(requestBody);
        
        // Validate representation
        if (!bookData.has("title") || !bookData.has("author") || !bookData.has("isbn")) {
            return createErrorResponse(400, "Missing required fields");
        }
        
        BookRepresentation book = new BookRepresentation(
            generateId(),
            bookData.getString("title"),
            bookData.getString("author"),
            bookData.getString("isbn"),
            true
        );
        
        saveBook(book);
        
        // Return created resource with Location header
        Response response = createResponse(201, "application/json", book.toJSON());
        response.headers.put("Location", "/api/books/" + book.id);
        return response;
    }
    
    /**
     * PUT /api/books/{id} - Update entire book resource
     */
    public Response updateBook(int id, String requestBody) {
        BookRepresentation existingBook = fetchBookById(id);
        
        if (existingBook == null) {
            return createErrorResponse(404, "Book not found");
        }
        
        JSONObject bookData = new JSONObject(requestBody);
        
        // Replace entire resource
        existingBook.title = bookData.getString("title");
        existingBook.author = bookData.getString("author");
        existingBook.isbn = bookData.getString("isbn");
        
        saveBook(existingBook);
        
        return createResponse(200, "application/json", existingBook.toJSON());
    }
    
    /**
     * DELETE /api/books/{id} - Remove book resource
     */
    public Response deleteBook(int id) {
        BookRepresentation book = fetchBookById(id);
        
        if (book == null) {
            return createErrorResponse(404, "Book not found");
        }
        
        if (!book.available) {
            return createErrorResponse(400, "Cannot delete borrowed book");
        }
        
        deleteBookById(id);
        
        return createResponse(204, null, null); // No content
    }
    
    // ==================== SUB-CONSTRAINT 3: Self-Descriptive Messages ====================
    /**
     * Messages include enough information to describe how to process them
     * Uses standard HTTP:
     * - Status codes (200, 404, 500, etc.)
     * - Content-Type headers
     * - Cache-Control headers
     * - Standard methods (GET, POST, etc.)
     */
    
    private Response createResponse(int statusCode, String contentType, Object body) {
        Response response = new Response();
        response.statusCode = statusCode;
        response.body = body;
        
        // Self-descriptive headers
        if (contentType != null) {
            response.headers.put("Content-Type", contentType);
        }
        response.headers.put("X-API-Version", "1.0");
        response.headers.put("X-RateLimit-Remaining", "99");
        
        // Status code describes the result
        switch (statusCode) {
            case 200:
                response.statusDescription = "OK";
                break;
            case 201:
                response.statusDescription = "Created";
                break;
            case 204:
                response.statusDescription = "No Content";
                break;
            case 400:
                response.statusDescription = "Bad Request";
                break;
            case 404:
                response.statusDescription = "Not Found";
                break;
            default:
                response.statusDescription = "Unknown";
        }
        
        return response;
    }
    
    private Response createErrorResponse(int statusCode, String message) {
        JSONObject error = new JSONObject();
        error.put("success", false);
        error.put("error", message);
        error.put("status", statusCode);
        
        return createResponse(statusCode, "application/json", error);
    }
    
    // ==================== SUB-CONSTRAINT 4: HATEOAS ====================
    /**
     * Hypermedia As The Engine Of Application State
     * Responses include links to related resources
     * Client discovers available actions through hypermedia
     */
    
    /**
     * GET /api/books/{id} with HATEOAS
     */
    public Response getBookWithHateoas(int id) {
        BookRepresentation book = fetchBookById(id);
        
        if (book == null) {
            return createErrorResponse(404, "Book not found");
        }
        
        JSONObject representation = book.toJSON();
        
        // Add hypermedia links
        JSONObject links = new JSONObject();
        links.put("self", new JSONObject()
            .put("href", "/api/books/" + id)
            .put("method", "GET"));
        
        links.put("update", new JSONObject()
            .put("href", "/api/books/" + id)
            .put("method", "PUT"));
        
        links.put("delete", new JSONObject()
            .put("href", "/api/books/" + id)
            .put("method", "DELETE"));
        
        // Conditional links based on resource state
        if (book.available) {
            links.put("borrow", new JSONObject()
                .put("href", "/api/borrows")
                .put("method", "POST")
                .put("body", new JSONObject()
                    .put("book_id", id)
                    .put("borrower_name", "string")
                    .put("borrower_email", "string")
                    .put("days", "integer")));
        } else {
            links.put("borrower_info", new JSONObject()
                .put("href", "/api/borrows?book_id=" + id)
                .put("method", "GET"));
        }
        
        representation.put("_links", links);
        
        return createResponse(200, "application/json", representation);
    }
    
    /**
     * GET /api - API root with discovery links
     */
    public Response getApiRoot() {
        JSONObject root = new JSONObject();
        root.put("version", "1.0");
        root.put("title", "Library Management API");
        
        JSONObject links = new JSONObject();
        
        // Available endpoints
        links.put("books", new JSONObject()
            .put("href", "/api/books")
            .put("description", "Manage library books"));
        
        links.put("available_books", new JSONObject()
            .put("href", "/api/books/available")
            .put("description", "Get books available for borrowing"));
        
        links.put("borrows", new JSONObject()
            .put("href", "/api/borrows")
            .put("description", "Manage book borrowing"));
        
        links.put("overdue", new JSONObject()
            .put("href", "/api/borrows/overdue")
            .put("description", "Get overdue books"));
        
        root.put("_links", links);
        
        return createResponse(200, "application/json", root);
    }
    
    /**
     * GET /api/books with collection-level HATEOAS
     */
    public Response getBooksCollectionWithHateoas() {
        List<BookRepresentation> books = fetchAllBooks();
        
        JSONObject response = new JSONObject();
        
        // Books data
        JSONArray booksArray = new JSONArray();
        for (BookRepresentation book : books) {
            JSONObject bookJson = book.toJSON();
            
            // Add link to individual resource
            bookJson.put("_links", new JSONObject()
                .put("self", new JSONObject()
                    .put("href", "/api/books/" + book.id)));
            
            booksArray.put(bookJson);
        }
        response.put("books", booksArray);
        
        // Collection metadata
        response.put("total", books.size());
        
        // Collection-level links
        JSONObject links = new JSONObject();
        links.put("self", new JSONObject().put("href", "/api/books"));
        links.put("create", new JSONObject()
            .put("href", "/api/books")
            .put("method", "POST"));
        links.put("available", new JSONObject()
            .put("href", "/api/books/available"));
        
        response.put("_links", links);
        
        return createResponse(200, "application/json", response);
    }
    
    // ==================== Supporting Classes ====================
    
    static class BookRepresentation {
        int id;
        String title;
        String author;
        String isbn;
        boolean available;
        
        BookRepresentation(int id, String title, String author, String isbn, boolean available) {
            this.id = id;
            this.title = title;
            this.author = author;
            this.isbn = isbn;
            this.available = available;
        }
        
        JSONObject toJSON() {
            JSONObject json = new JSONObject();
            json.put("id", id);
            json.put("title", title);
            json.put("author", author);
            json.put("isbn", isbn);
            json.put("available", available);
            return json;
        }
    }
    
    static class Response {
        int statusCode;
        String statusDescription;
        Map<String, String> headers = new HashMap<>();
        Object body;
    }
    
    // Mock data methods
    private static int idCounter = 1;
    private static List<BookRepresentation> bookStore = new ArrayList<>();
    
    private List<BookRepresentation> fetchAllBooks() {
        return new ArrayList<>(bookStore);
    }
    
    private BookRepresentation fetchBookById(int id) {
        return bookStore.stream()
            .filter(b -> b.id == id)
            .findFirst()
            .orElse(null);
    }
    
    private void saveBook(BookRepresentation book) {
        bookStore.removeIf(b -> b.id == book.id);
        bookStore.add(book);
    }
    
    private void deleteBookById(int id) {
        bookStore.removeIf(b -> b.id == id);
    }
    
    private int generateId() {
        return idCounter++;
    }
    
    // ==================== DEMO ====================
    
    public static void main(String[] args) {
        ApiController controller = new ApiController();
        
        System.out.println("=== Uniform Interface Constraint Demo ===\n");
        
        // 1. Resource Identification
        System.out.println("--- 1. Resource Identification (URIs) ---");
        System.out.println("Books Collection: " + ResourceUris.BOOKS);
        System.out.println("Specific Book: " + ResourceUris.BOOK_BY_ID);
        System.out.println("Available Books: " + ResourceUris.AVAILABLE_BOOKS);
        
        // 2. Manipulation through representations
        System.out.println("\n--- 2. Manipulation through Representations ---");
        System.out.println("Creating book with POST...");
        String newBook = "{\"title\":\"Clean Code\",\"author\":\"Robert Martin\",\"isbn\":\"9780132350884\"}";
        Response created = controller.createBook(newBook);
        System.out.println("Status: " + created.statusCode + " " + created.statusDescription);
        System.out.println("Location: " + created.headers.get("Location"));
        
        // 3. Self-descriptive messages
        System.out.println("\n--- 3. Self-Descriptive Messages ---");
        Response getResponse = controller.getBook(1);
        System.out.println("Status: " + getResponse.statusCode + " " + getResponse.statusDescription);
        System.out.println("Content-Type: " + getResponse.headers.get("Content-Type"));
        System.out.println("API Version: " + getResponse.headers.get("X-API-Version"));
        
        // 4. HATEOAS
        System.out.println("\n--- 4. HATEOAS (Hypermedia Links) ---");
        System.out.println("API Root Discovery:");
        Response root = controller.getApiRoot();
        System.out.println(root.body);
        
        System.out.println("\nBook with Links:");
        Response bookWithLinks = controller.getBookWithHateoas(1);
        System.out.println(bookWithLinks.body);
        
        System.out.println("\n✓ Uniform Interface provides consistency across the API");
        System.out.println("✓ Clients can discover available operations");
        System.out.println("✓ Standard HTTP makes the API self-documenting");
    }
}
