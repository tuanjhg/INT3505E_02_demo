/**
 * CLIENT-SERVER CONSTRAINT
 * 
 * The server manages resources (books, borrow records) and responds to client requests.
 * The server does not initiate requests to the client - it only responds.
 * 
 * This demonstrates:
 * - Server listening for client requests
 * - Server processing requests and managing data
 * - Server sending responses back to clients
 * - Clear separation between client and server responsibilities
 */

import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import java.io.*;
import java.net.InetSocketAddress;
import java.util.*;
import org.json.JSONObject;
import org.json.JSONArray;

public class Server {
    // Simulated database - in production, this would be a real database
    private static List<Book> books = new ArrayList<>();
    private static List<BorrowRecord> borrowRecords = new ArrayList<>();
    private static int nextBookId = 1;
    private static int nextBorrowId = 1;

    /**
     * Start the server and listen for client requests
     */
    public static void main(String[] args) throws IOException {
        // Initialize with sample data
        initializeSampleData();

        // Create HTTP server on port 5000
        HttpServer server = HttpServer.create(new InetSocketAddress(5000), 0);
        
        // Define endpoints - server waits for client requests
        server.createContext("/api/books", new BooksHandler());
        server.createContext("/api/borrows", new BorrowsHandler());
        
        server.setExecutor(null); // Use default executor
        server.start();
        
        System.out.println("Library Management Server started on port 5000");
        System.out.println("Server is waiting for client requests...");
    }

    /**
     * Handler for /api/books endpoint
     * Server responds to client requests for book operations
     */
    static class BooksHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String method = exchange.getRequestMethod();
            
            if ("GET".equals(method)) {
                // Server retrieves books and sends to client
                handleGetBooks(exchange);
            } else if ("POST".equals(method)) {
                // Server creates a new book based on client data
                handleCreateBook(exchange);
            } else {
                sendResponse(exchange, 405, "Method not allowed");
            }
        }

        private void handleGetBooks(HttpExchange exchange) throws IOException {
            JSONArray booksArray = new JSONArray();
            for (Book book : books) {
                booksArray.put(book.toJSON());
            }
            
            JSONObject response = new JSONObject();
            response.put("success", true);
            response.put("message", "Found " + books.size() + " books");
            response.put("data", booksArray);
            
            sendResponse(exchange, 200, response.toString());
        }

        private void handleCreateBook(HttpExchange exchange) throws IOException {
            // Read client request data
            String body = new String(exchange.getRequestBody().readAllBytes());
            JSONObject bookData = new JSONObject(body);
            
            // Server creates book with received data
            Book newBook = new Book(
                nextBookId++,
                bookData.getString("title"),
                bookData.getString("author"),
                bookData.getString("isbn"),
                true
            );
            books.add(newBook);
            
            JSONObject response = new JSONObject();
            response.put("success", true);
            response.put("message", "Book created successfully");
            response.put("data", newBook.toJSON());
            
            sendResponse(exchange, 201, response.toString());
        }
    }

    /**
     * Handler for /api/borrows endpoint
     * Server manages borrowing operations in response to client requests
     */
    static class BorrowsHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String method = exchange.getRequestMethod();
            
            if ("POST".equals(method)) {
                handleBorrowBook(exchange);
            } else {
                sendResponse(exchange, 405, "Method not allowed");
            }
        }

        private void handleBorrowBook(HttpExchange exchange) throws IOException {
            String body = new String(exchange.getRequestBody().readAllBytes());
            JSONObject borrowData = new JSONObject(body);
            
            int bookId = borrowData.getInt("book_id");
            Book book = findBookById(bookId);
            
            if (book == null) {
                sendResponse(exchange, 404, "Book not found");
                return;
            }
            
            if (!book.available) {
                sendResponse(exchange, 400, "Book is not available");
                return;
            }
            
            // Server processes the borrow operation
            book.available = false;
            BorrowRecord record = new BorrowRecord(
                nextBorrowId++,
                bookId,
                borrowData.getString("borrower_name"),
                borrowData.getString("borrower_email"),
                borrowData.getInt("days")
            );
            borrowRecords.add(record);
            
            JSONObject response = new JSONObject();
            response.put("success", true);
            response.put("message", "Book borrowed successfully");
            response.put("data", record.toJSON());
            
            sendResponse(exchange, 201, response.toString());
        }
    }

    // Helper methods
    private static void sendResponse(HttpExchange exchange, int statusCode, String response) 
            throws IOException {
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        exchange.sendResponseHeaders(statusCode, response.length());
        OutputStream os = exchange.getResponseBody();
        os.write(response.getBytes());
        os.close();
    }

    private static Book findBookById(int id) {
        return books.stream()
            .filter(b -> b.id == id)
            .findFirst()
            .orElse(null);
    }

    private static void initializeSampleData() {
        books.add(new Book(nextBookId++, "The Pragmatic Programmer", 
            "Andy Hunt, Dave Thomas", "9780135957059", true));
        books.add(new Book(nextBookId++, "Design Patterns", 
            "Gang of Four", "9780201633612", true));
    }

    // Simple domain classes
    static class Book {
        int id;
        String title;
        String author;
        String isbn;
        boolean available;

        Book(int id, String title, String author, String isbn, boolean available) {
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

    static class BorrowRecord {
        int id;
        int bookId;
        String borrowerName;
        String borrowerEmail;
        int days;

        BorrowRecord(int id, int bookId, String borrowerName, String borrowerEmail, int days) {
            this.id = id;
            this.bookId = bookId;
            this.borrowerName = borrowerName;
            this.borrowerEmail = borrowerEmail;
            this.days = days;
        }

        JSONObject toJSON() {
            JSONObject json = new JSONObject();
            json.put("id", id);
            json.put("book_id", bookId);
            json.put("borrower_name", borrowerName);
            json.put("borrower_email", borrowerEmail);
            json.put("days", days);
            return json;
        }
    }
}
