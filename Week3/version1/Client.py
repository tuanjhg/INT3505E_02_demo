"""
RESTful Constraint: Client-Server Architecture - Client Side

This demonstrates the client side of the client-server architecture.
The client focuses on presentation and user interaction,
consuming the server's APIs without knowing implementation details.

Key Benefits:
- Client is lightweight (no business logic)
- Can be easily replaced or updated
- Multiple client types can use the same server (web, mobile, CLI)
"""

import requests
import json
from datetime import datetime

class LibraryClient:
    """
    Client for Library Management System
    Demonstrates separation from server implementation
    """
    
    def __init__(self, base_url='http://127.0.0.1:5001'):
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_server_health(self):
        """Check if server is available"""
        try:
            response = self.session.get(f'{self.base_url}/api/health')
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Server is healthy: {data['service']}")
                return True
            return False
        except requests.exceptions.ConnectionError:
            print("✗ Cannot connect to server")
            return False
    
    def get_all_books(self):
        """
        Retrieve all books from server
        Client only cares about the API contract, not implementation
        """
        try:
            response = self.session.get(f'{self.base_url}/api/books')
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                print(f"Error: {response.status_code}")
                return []
        except Exception as e:
            print(f"Connection error: {e}")
            return []
    
    def create_book(self, title, author, isbn):
        """
        Create a new book through server API
        Client sends data, server handles validation and storage
        """
        book_data = {
            'title': title,
            'author': author,
            'isbn': isbn
        }
        
        try:
            response = self.session.post(
                f'{self.base_url}/api/books',
                json=book_data,
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            
            if response.status_code == 201:
                print(f"✓ Book created: {result['data']['title']}")
                return result['data']
            else:
                print(f"✗ Error: {result.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            print(f"Connection error: {e}")
            return None
    
    def get_book(self, book_id):
        """Get a specific book by ID"""
        try:
            response = self.session.get(f'{self.base_url}/api/books/{book_id}')
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data')
            else:
                print(f"Book not found (ID: {book_id})")
                return None
        except Exception as e:
            print(f"Connection error: {e}")
            return None
    
    def display_books(self, books):
        """Display books in a user-friendly format - UI logic on client side"""
        if not books:
            print("\nNo books found.")
            return
        
        print(f"\n{'='*80}")
        print(f"{'ID':<5} {'Title':<30} {'Author':<25} {'Status':<15}")
        print(f"{'='*80}")
        
        for book in books:
            status = "Available" if book.get('available') else "Borrowed"
            print(f"{book['id']:<5} {book['title']:<30} {book['author']:<25} {status:<15}")
        
        print(f"{'='*80}\n")


def demo_client_server():
    """
    Demonstration of Client-Server Architecture
    Shows the clear separation between client and server
    """
    print("="*80)
    print("CLIENT-SERVER ARCHITECTURE DEMONSTRATION")
    print("="*80)
    print("\nThis demonstrates:")
    print("1. Server manages resources and business logic")
    print("2. Client handles presentation and user interaction")
    print("3. They communicate through well-defined APIs")
    print("4. Each can evolve independently")
    print("="*80)
    
    client = LibraryClient()
    
    # Check server connectivity
    print("\n[1] Checking server connectivity...")
    if not client.check_server_health():
        print("\n⚠️  Please start the server first:")
        print("   python Server.py")
        return
    
    # Demonstrate client operations
    print("\n[2] Fetching all books from server...")
    books = client.get_all_books()
    client.display_books(books)
    
    print("[3] Creating new books through server API...")
    client.create_book(
        "The Pragmatic Programmer",
        "Andrew Hunt",
        "9780135957059"
    )
    
    client.create_book(
        "Clean Code",
        "Robert C. Martin",
        "9780132350884"
    )
    
    print("\n[4] Fetching updated book list...")
    books = client.get_all_books()
    client.display_books(books)
    
    print("\n[5] Retrieving specific book...")
    if books:
        book = client.get_book(books[0]['id'])
        if book:
            print(f"\nBook Details:")
            print(f"  Title: {book['title']}")
            print(f"  Author: {book['author']}")
            print(f"  ISBN: {book['isbn']}")
            print(f"  Status: {'Available' if book['available'] else 'Borrowed'}")
    
    print("\n" + "="*80)
    print("SUMMARY:")
    print("- Client focused on presentation and user interaction")
    print("- Server handled all business logic and data management")
    print("- Communication through standard HTTP/REST APIs")
    print("- Either side can be modified without affecting the other")
    print("="*80)


if __name__ == '__main__':
    demo_client_server()
