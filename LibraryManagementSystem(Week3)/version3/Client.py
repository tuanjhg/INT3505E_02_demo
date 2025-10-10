"""
Version 3: Simple Uniform Interface Client

Shows how to use the uniform interface features.
"""

import requests
import time

class UniformInterfaceClient:
    def __init__(self, base_url='http://127.0.0.1:5001'):
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_server_health(self):
        """Check server health"""
        try:
            response = self.session.get(f'{self.base_url}/api/health')
            if response.status_code == 200:
                data = response.json()
                print(f"Server: {data['service']} {data['version']}")
                print("  Features:")
                for feature in data['features']:
                    print(f"    - {feature}")
                return True
            return False
        except requests.exceptions.ConnectionError:
            print("Cannot connect to server")
            return False
    
    def discover_api(self):
        """NEW: Discover API through root endpoint"""
        print("\n[GET] Discovering API...")
        
        response = self.session.get(f'{self.base_url}/api')
        
        if response.status_code == 200:
            data = response.json()
            print(f"  {data['message']}")
            print("  Available endpoints:")
            
            for name, link in data['_links'].items():
                method = link.get('method', 'GET')
                desc = link.get('description', '')
                print(f"    - {method} {name}: {desc}")
            
            return data['_links']
        else:
            print(f" Discovery failed: {response.status_code}")
            return {}
    
    def get_books(self):
        """GET books - shows caching and HATEOAS"""
        print("\n[GET] Getting all books...")
        
        start_time = time.time()
        response = self.session.get(f'{self.base_url}/api/books')
        duration = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            cache_status = response.headers.get('X-Cache-Status', 'UNKNOWN')
            
            print(f"  {data['message']}")
            print(f"  Response time: {duration:.0f}ms")
            print(f"  Cache status: {cache_status}")
            
            # Show HATEOAS links
            if '_links' in data:
                print("  Available actions:")
                for name, link in data['_links'].items():
                    method = link.get('method', 'GET')
                    print(f"    - {method} {name}")
            
            # Show individual book links
            if data['data']:
                book = data['data'][0]
                if '_links' in book:
                    print(f"  Book '{book['title']}' actions:")
                    for name, link in book['_links'].items():
                        method = link.get('method', 'GET')
                        print(f"    - {method} {name}")
            
            return data['data']
        else:
            print(f"  Error: {response.status_code}")
            return []
    
    def get_book(self, book_id):
        """GET single book"""
        print(f"\n[GET] Getting book {book_id}...")
        
        response = self.session.get(f'{self.base_url}/api/books/{book_id}')
        
        if response.status_code == 200:
            data = response.json()
            cache_status = response.headers.get('X-Cache-Status', 'UNKNOWN')
            
            print(f"  Found: {data['data']['title']}")
            print(f"  Cache status: {cache_status}")
            return data['data']
        elif response.status_code == 404:
            data = response.json()
            print(f"  {data['error']['message']}")
            
            # Show error links
            if '_links' in data:
                print("  Suggested actions:")
                for name, link in data['_links'].items():
                    desc = link.get('description', name)
                    print(f"    - {desc}")
            
            return None
        else:
            print(f"   Error: {response.status_code}")
            return None
    
    def create_book(self, title, author, isbn):
        """POST - Create book with proper error handling"""
        print(f"\n[POST] Creating book: {title}")
        
        response = self.session.post(
            f'{self.base_url}/api/books',
            json={'title': title, 'author': author, 'isbn': isbn},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            data = response.json()
            location = response.headers.get('Location', 'N/A')
            
            print(f"  {data['message']}")
            print(f"  Location: {location}")
            return data['data']
        elif response.status_code == 400:
            data = response.json()
            error = data['error']
            print(f"  {error['code']}: {error['message']}")
            
            if 'required_fields' in error:
                print(f"    Required: {', '.join(error['required_fields'])}")
            
            return None
        else:
            print(f"  Error: {response.status_code}")
            return None
    
    def update_book(self, book_id, **updates):
        """PUT - Update entire book"""
        print(f"\n[PUT] Updating book {book_id}...")
        
        response = self.session.put(
            f'{self.base_url}/api/books/{book_id}',
            json=updates,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   {data['message']}")
            return data['data']
        elif response.status_code == 404:
            data = response.json()
            print(f"   {data['error']['message']}")
            return None
        else:
            print(f"   Error: {response.status_code}")
            return None
    
    def delete_book(self, book_id):
        """DELETE - Remove book"""
        print(f"\n[DELETE] Deleting book {book_id}...")
        
        response = self.session.delete(f'{self.base_url}/api/books/{book_id}')
        
        if response.status_code == 204:
            print(f"   Book deleted successfully (204 No Content)")
            return True
        elif response.status_code == 404:
            data = response.json()
            print(f"   {data['error']['message']}")
            return False
        else:
            print(f" Error: {response.status_code}")
            return False
    
    def get_stats(self):
        """Get real-time stats"""
        print(f"\n[GET] Getting stats...")
        
        response = self.session.get(f'{self.base_url}/api/stats')
        
        if response.status_code == 200:
            data = response.json()
            cache_control = response.headers.get('Cache-Control', 'none')
            
            print(f"   {data['message']}")
            print(f"  Cache-Control: {cache_control}")
            print(f"  Total books: {data['data']['total_books']}")
            print(f"  Available: {data['data']['available_books']}")
            
            return data['data']
        else:
            print(f"   Error: {response.status_code}")
            return None

def demo_uniform_interface():
    """Demo the uniform interface features"""
    print("="*60)
    print("VERSION 3: SIMPLE UNIFORM INTERFACE DEMO")
    print("="*60)
    print("\nThis demo shows:")
    print("1. API discovery through HATEOAS links")
    print("2. Standard HTTP methods (GET, POST, PUT, DELETE)")
    print("3. Better error messages with proper status codes")
    print("4. Consistent response format")
    print("5. All caching features from Version 2")
    print("="*60)
    
    client = UniformInterfaceClient()
    
    if not client.check_server_health():
        print("\n⚠️  Please start the server first:")
        print("   cd version3 && python Server.py")
        return
    
    client.discover_api()
    
    print(f"\n{'='*60}")
    print("DEMONSTRATING UNIFORM INTERFACE")
    print("="*60)
    
    # GET with caching and HATEOAS
    print("\n1. GET - Read data (cacheable, with HATEOAS links)")
    books = client.get_books()
    
    print("\n2. GET same data (should be cached)")
    books = client.get_books()
    
    # GET single book
    if books:
        print("\n3. GET single book")
        book = client.get_book(books[0]['id'])
    
    # POST - Create
    print("\n4. POST - Create new data")
    new_book = client.create_book("Uniform Interface Guide", "REST Author", "3333333333")
    
    # PUT - Update
    if new_book:
        print("\n5. PUT - Update existing data")
        client.update_book(
            new_book['id'],
            title="Updated Uniform Interface Guide",
            author="REST Author Updated",
            available=True
        )
    
    # Error handling
    print("\n6. Error handling - try to get non-existent book")
    client.get_book(99999)
    
    # DELETE
    if new_book:
        print("\n7. DELETE - Remove data")
        client.delete_book(new_book['id'])
    
    # Show stats (never cached)
    print("\n8. Real-time stats (never cached)")
    client.get_stats()

if __name__ == '__main__':
    demo_uniform_interface()