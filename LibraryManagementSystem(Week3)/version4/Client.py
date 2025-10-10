"""
Version 4: Simple Stateless Client

Shows how to work with stateless API (must send API key with every request).
"""

import requests
import time

class StatelessClient:
    def __init__(self, base_url='http://127.0.0.1:5001'):
        self.base_url = base_url
        self.session = requests.Session()
        self.api_key = None
        self.user_email = None
    
    def authenticate(self, email):
        """Get API key for stateless authentication"""
        print(f"\n[POST] Getting API key for {email}...")
        
        response = self.session.post(
            f'{self.base_url}/api/auth',
            json={'email': email},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            data = response.json()
            self.api_key = data['data']['api_key']
            self.user_email = data['data']['email']
            
            print(f"   {data['message']}")
            print(f"  API Key: {self.api_key}")
            print(f"  Instructions: {data['data']['instructions']}")
            return True
        else:
            data = response.json()
            error = data.get('error', {})
            print(f"   {error.get('message', 'Authentication failed')}")
            return False
    
    def _make_authenticated_request(self, method, endpoint, **kwargs):
        """Make request with API key (REQUIRED for all requests)"""
        if not self.api_key:
            print("   Not authenticated! Call authenticate() first.")
            return None, False
        
        # IMPORTANT: Add Authorization header to EVERY request
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.api_key}'
        kwargs['headers'] = headers
        
        url = f'{self.base_url}{endpoint}'
        
        try:
            start_time = time.time()
            response = self.session.request(method, url, **kwargs)
            duration = (time.time() - start_time) * 1000
            
            print(f"  Request: {method} {endpoint}")
            print(f"  Authorization: Bearer {self.api_key[:10]}...")
            print(f"  Response time: {duration:.0f}ms")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 204:  
                return None, False
            elif response.status_code in [200, 201]:
                return response.json(), False
            elif response.status_code == 401:
                data = response.json()
                error = data.get('error', {})
                print(f"   Authentication error: {error.get('message')}")
                return data, False
            else:
                try:
                    return response.json(), False
                except:
                    return {'error': {'message': f'HTTP {response.status_code}'}}, False
                    
        except Exception as e:
            print(f"   Request failed: {e}")
            return None, False
    
    def check_server_health(self):
        """Check server health (no auth required)"""
        try:
            response = self.session.get(f'{self.base_url}/api/health')
            if response.status_code == 200:
                data = response.json()
                print(f" Server: {data['service']} {data['version']}")
                print(f"  Authentication: {data['authentication']}")
                print("  Features:")
                for feature in data['features']:
                    print(f"    - {feature}")
                return True
            return False
        except requests.exceptions.ConnectionError:
            print(" Cannot connect to server")
            return False
    
    def discover_api(self):
        """Discover API (no auth required)"""
        print("\n[GET] Discovering API...")
        
        response = self.session.get(f'{self.base_url}/api')
        
        if response.status_code == 200:
            data = response.json()
            print(f"   {data['message']}")
            print(f"  Authentication: {data['authentication']}")
            
            print("  Available endpoints:")
            for name, link in data['_links'].items():
                method = link.get('method', 'GET')
                desc = link.get('description', '')
                print(f"    - {method} {name}: {desc}")
            
            return data['_links']
        else:
            print(f"   Discovery failed: {response.status_code}")
            return {}
    
    def get_books(self):
        """Get all books (requires auth)"""
        print("\n[GET] Getting all books...")
        
        response, from_cache = self._make_authenticated_request('GET', '/api/books')
        
        if response and response.get('success'):
            cache_status = 'N/A'  
            
            print(f"   {response['message']}")
            print(f"  Authenticated as: {response.get('authenticated_user')}")
            
            if '_links' in response:
                print("  Available actions:")
                for name, link in response['_links'].items():
                    method = link.get('method', 'GET')
                    print(f"    - {method} {name}")
            
            return response['data']
        elif response:
            error = response.get('error', {})
            print(f"   {error.get('message', 'Failed to get books')}")
            return []
        
        return []
    
    def get_book(self, book_id):
        """Get single book (requires auth)"""
        print(f"\n[GET] Getting book {book_id}...")
        
        response, _ = self._make_authenticated_request('GET', f'/api/books/{book_id}')
        
        if response and response.get('success'):
            print(f"   Found: {response['data']['title']}")
            print(f"  Authenticated as: {response.get('authenticated_user')}")
            return response['data']
        elif response:
            error = response.get('error', {})
            print(f"   {error.get('message')}")
            return None
        
        return None
    
    def create_book(self, title, author, isbn):
        """Create book (requires auth)"""
        print(f"\n[POST] Creating book: {title}")
        
        response, _ = self._make_authenticated_request(
            'POST', 
            '/api/books',
            json={'title': title, 'author': author, 'isbn': isbn},
            headers={'Content-Type': 'application/json'}
        )
        
        if response and response.get('success'):
            print(f"   {response['message']}")
            print(f"  Created by: {response.get('created_by')}")
            return response['data']
        elif response:
            error = response.get('error', {})
            print(f"   {error.get('message')}")
            return None
        
        return None
    
    def update_book(self, book_id, **updates):
        """Update book (requires auth)"""
        print(f"\n[PUT] Updating book {book_id}...")
        
        response, _ = self._make_authenticated_request(
            'PUT',
            f'/api/books/{book_id}',
            json=updates,
            headers={'Content-Type': 'application/json'}
        )
        
        if response and response.get('success'):
            print(f"   {response['message']}")
            print(f"  Updated by: {response.get('updated_by')}")
            return response['data']
        elif response:
            error = response.get('error', {})
            print(f"   {error.get('message')}")
            return None
        
        return None
    
    def delete_book(self, book_id):
        """Delete book (requires auth)"""
        print(f"\n[DELETE] Deleting book {book_id}...")
        
        response, _ = self._make_authenticated_request('DELETE', f'/api/books/{book_id}')
        
        if response is None: 
            print(f"   Book deleted successfully")
            return True
        elif response:
            error = response.get('error', {})
            print(f"   {error.get('message')}")
            return False
        
        return False
    
    def get_stats(self):
        """Get stats (requires auth)"""
        print(f"\n[GET] Getting statistics...")
        
        response, _ = self._make_authenticated_request('GET', '/api/stats')
        
        if response and response.get('success'):
            print(f"   {response['message']}")
            print(f"  Requested by: {response.get('requested_by')}")
            print(f"  Total books: {response['data']['total_books']}")
            print(f"  Available: {response['data']['available_books']}")
            return response['data']
        elif response:
            error = response.get('error', {})
            print(f"   {error.get('message')}")
            return None
        
        return None

def demo_stateless():
    """Demo the stateless features"""
    
    client = StatelessClient()
    
    # Check server
    if not client.check_server_health():
        print("\n⚠️  Please start the server first:")
        print("   cd version4 && python Server.py")
        return
    
    # Discover API
    client.discover_api()
    
    print(f"\n{'='*60}")
    print("DEMONSTRATING STATELESS AUTHENTICATION")
    print("="*60)
    
    # Step 1: Authenticate (get API key)
    print("\n1. Authenticate - get API key")
    if not client.authenticate('john.doe@example.com'):
        return
    
    # Step 2: Make authenticated requests
    print("\n2. Make requests with API key")
    books = client.get_books()
    
    print("\n3. Another request - API key required again")
    if books:
        book = client.get_book(books[0]['id'])
    
    # Step 3: Create data (with auth)
    print("\n4. Create book - API key identifies user")
    new_book = client.create_book("Stateless Systems", "API Author", "4444444444")
    
    # Step 4: Update (with auth)
    if new_book:
        print("\n5. Update book - API key still required")
        client.update_book(new_book['id'], title="Updated Stateless Systems")
    
    # Step 5: Get stats (with auth)
    print("\n6. Get stats - shows who requested")
    client.get_stats()
    
    # Step 6: Delete (with auth)
    if new_book:
        print("\n7. Delete book - final authenticated action")
        client.delete_book(new_book['id'])
    
    # Step 7: Demonstrate what happens without auth
    print("\n8. Try request without API key")
    client_no_auth = StatelessClient()
    response, _ = client_no_auth._make_authenticated_request('GET', '/api/books')

if __name__ == '__main__':
    demo_stateless()