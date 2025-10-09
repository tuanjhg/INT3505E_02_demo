"""
Stateless Client Demo

Demonstrates how clients interact with stateless APIs:
- Must include authentication with EVERY request
- No reliance on server-side sessions
- Each request is independent
"""

import requests
import json

class StatelessLibraryClient:
    """
    Client for stateless library API
    Must maintain API key and send with each request
    """
    
    def __init__(self, base_url='http://127.0.0.1:5002'):
        self.base_url = base_url
        self.api_key = None
        self.email = None
    
    def authenticate(self, email):
        """
        Get API key for stateless authentication
        Client must store this and send with each request
        """
        try:
            response = requests.post(
                f'{self.base_url}/api/auth/generate-key',
                json={'email': email}
            )
            
            if response.status_code == 201:
                data = response.json()['data']
                self.api_key = data['api_key']
                self.email = data['email']
                print(f"✓ Authenticated as: {self.email}")
                print(f"  API Key: {self.api_key}")
                return True
            else:
                print(f"✗ Authentication failed: {response.json().get('message')}")
                return False
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def _make_request(self, method, endpoint, **kwargs):
        """
        IMPORTANT: Include authentication with EVERY request
        This demonstrates stateless nature - no session on server
        """
        if not self.api_key:
            print("✗ Not authenticated. Call authenticate() first.")
            return None
        
        # Add Authorization header to EVERY request
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.api_key}'
        kwargs['headers'] = headers
        
        url = f'{self.base_url}{endpoint}'
        
        try:
            response = requests.request(method, url, **kwargs)
            return response
        except Exception as e:
            print(f"✗ Request error: {e}")
            return None
    
    def get_books(self):
        """Get all books - auth required with each request"""
        print("\n[GET] Fetching books (with auth token)...")
        response = self._make_request('GET', '/api/books')
        
        if response and response.status_code == 200:
            data = response.json()
            print(f"✓ {data['message']}")
            return data['data']
        else:
            print("✗ Failed to fetch books")
            return []
    
    def borrow_book(self, book_id, borrower_name, days=14):
        """
        Borrow a book - must provide ALL context in request
        Server doesn't remember previous requests
        """
        print(f"\n[POST] Borrowing book {book_id}...")
        
        response = self._make_request(
            'POST',
            f'/api/books/{book_id}/borrow',
            json={
                'borrower_name': borrower_name,
                'days': days
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if response and response.status_code == 201:
            data = response.json()
            print(f"✓ {data['message']}")
            return data['data']
        elif response:
            print(f"✗ {response.json().get('message')}")
            return None
        return None
    
    def get_my_borrows(self):
        """
        Get borrowing history - identity from token, not session
        """
        print("\n[GET] Fetching my borrow records...")
        response = self._make_request('GET', '/api/borrows')
        
        if response and response.status_code == 200:
            data = response.json()
            print(f"✓ {data['message']}")
            return data['data']
        else:
            print("✗ Failed to fetch borrow records")
            return []
    
    def return_book(self, record_id):
        """Return a book - complete context in single request"""
        print(f"\n[POST] Returning book (record {record_id})...")
        
        response = self._make_request(
            'POST',
            f'/api/borrows/{record_id}/return'
        )
        
        if response and response.status_code == 200:
            data = response.json()
            print(f"✓ {data['message']}")
            return data['data']
        elif response:
            print(f"✗ {response.json().get('message')}")
            return None
        return None
    
    def display_books(self, books):
        """Display books"""
        if not books:
            print("  No books found")
            return
        
        print(f"\n  {'ID':<5} {'Title':<30} {'Status':<15}")
        print(f"  {'-'*50}")
        for book in books:
            status = "Available" if book['available'] else "Borrowed"
            print(f"  {book['id']:<5} {book['title']:<30} {status:<15}")
    
    def display_borrows(self, records):
        """Display borrow records"""
        if not records:
            print("  No borrow records found")
            return
        
        print(f"\n  {'ID':<5} {'Book':<30} {'Status':<15}")
        print(f"  {'-'*50}")
        for record in records:
            status = "Returned" if record['returned'] else "Active"
            print(f"  {record['id']:<5} {record['book_title']:<30} {status:<15}")


def demo_stateless():
    """
    Demonstrate stateless API interaction
    """
    print("="*70)
    print("STATELESS API DEMONSTRATION")
    print("="*70)
    print("\nKey Concepts:")
    print("1. No server-side session storage")
    print("2. Client includes credentials with EVERY request")
    print("3. Each request is independent and self-contained")
    print("4. Server doesn't remember previous client requests")
    print("="*70)
    
    # Create client
    client = StatelessLibraryClient()
    
    # Authenticate - get API key
    print("\n[Step 1] Authenticating with server...")
    print("(Client receives API key, server doesn't create session)")
    if not client.authenticate('john.doe@example.com'):
        print("\n⚠️  Please start the server first:")
        print("   python StatelessService.py")
        return
    
    # Every subsequent request includes the API key
    print("\n[Step 2] Making stateless requests...")
    print("(Notice: Authorization header included in every request)")
    
    # Get books
    books = client.get_books()
    client.display_books(books)
    
    if books:
        # Borrow a book
        print("\n[Step 3] Borrowing a book...")
        print("(All context provided in single request)")
        book_id = books[0]['id']
        client.borrow_book(book_id, 'John Doe', days=14)
        
        # Get borrows
        print("\n[Step 4] Fetching borrow history...")
        print("(User identity from token, not server session)")
        borrows = client.get_my_borrows()
        client.display_borrows(borrows)
        
        # Return book
        if borrows:
            print("\n[Step 5] Returning a book...")
            print("(Complete operation in single request)")
            client.return_book(borrows[0]['id'])
    
    # Demonstrate independence of requests
    print("\n" + "="*70)
    print("DEMONSTRATING STATELESS NATURE:")
    print("="*70)
    print("\n1. Create a new client instance (simulating new connection)")
    new_client = StatelessLibraryClient()
    
    print("\n2. Without authentication, requests fail:")
    new_client.get_books()
    
    print("\n3. With same API key, immediate access (no session needed):")
    new_client.api_key = client.api_key
    new_client.email = client.email
    books = new_client.get_books()
    print(f"   ✓ Got {len(books)} books using token from different 'session'")
    
    print("\n" + "="*70)
    print("SUMMARY:")
    print("- Server maintains NO session state")
    print("- Each request includes complete authentication")
    print("- Requests are independent and self-contained")
    print("- Enables better scalability and reliability")
    print("- Multiple clients can use same credentials simultaneously")
    print("="*70)


if __name__ == '__main__':
    demo_stateless()
