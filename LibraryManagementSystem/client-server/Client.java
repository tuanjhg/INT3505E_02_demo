/**
 * CLIENT-SERVER CONSTRAINT
 * 
 * This constraint establishes a separation of concerns between the user interface (client)
 * and data storage (server). The client initiates requests, and the server processes them.
 * 
 * Benefits:
 * - Portability: User interface can be moved to different platforms
 * - Scalability: Servers can be scaled independently
 * - Simplicity: Separation of concerns improves maintainability
 */

import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import org.json.JSONObject;
import org.json.JSONArray;

public class Client {
    private static final String BASE_URL = "http://localhost:5000/api";
    private final HttpClient httpClient;

    public Client() {
        this.httpClient = HttpClient.newHttpClient();
    }

    /**
     * Get all books from the library
     * Demonstrates client making a GET request to the server
     */
    public void getAllBooks() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/books"))
                .GET()
                .build();

            HttpResponse<String> response = httpClient.send(request, 
                HttpResponse.BodyHandlers.ofString());

            System.out.println("Books retrieved from server:");
            System.out.println(response.body());
        } catch (Exception e) {
            System.err.println("Error connecting to server: " + e.getMessage());
        }
    }

    /**
     * Add a new book to the library
     * Demonstrates client making a POST request to the server
     */
    public void addBook(String title, String author, String isbn) {
        try {
            JSONObject book = new JSONObject();
            book.put("title", title);
            book.put("author", author);
            book.put("isbn", isbn);

            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/books"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(book.toString()))
                .build();

            HttpResponse<String> response = httpClient.send(request, 
                HttpResponse.BodyHandlers.ofString());

            System.out.println("Book added. Server response:");
            System.out.println(response.body());
        } catch (Exception e) {
            System.err.println("Error adding book: " + e.getMessage());
        }
    }

    /**
     * Borrow a book from the library
     * Demonstrates client initiating a business operation on the server
     */
    public void borrowBook(int bookId, String borrowerName, String borrowerEmail, int days) {
        try {
            JSONObject borrowData = new JSONObject();
            borrowData.put("book_id", bookId);
            borrowData.put("borrower_name", borrowerName);
            borrowData.put("borrower_email", borrowerEmail);
            borrowData.put("days", days);

            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/borrows"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(borrowData.toString()))
                .build();

            HttpResponse<String> response = httpClient.send(request, 
                HttpResponse.BodyHandlers.ofString());

            System.out.println("Book borrowed. Server response:");
            System.out.println(response.body());
        } catch (Exception e) {
            System.err.println("Error borrowing book: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        Client client = new Client();
        
        // Example usage demonstrating client-server separation
        System.out.println("=== Library Management Client ===\n");
        
        // Client requests data from server
        client.getAllBooks();
        
        // Client sends data to server
        client.addBook("Clean Code", "Robert C. Martin", "9780132350884");
        
        // Client initiates business operation on server
        client.borrowBook(1, "John Doe", "john@example.com", 14);
    }
}
