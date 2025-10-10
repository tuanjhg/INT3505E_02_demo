"""
Version 2: Simple Cacheable Client

Shows how the client can see caching in action.
"""

import requests
import time

class SimpleCacheClient:
    def __init__(self, base_url='http://127.0.0.1:5001'):
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_server_health(self):
        """Check if server is running"""
        try:
            response = self.session.get(f'{self.base_url}/api/health')
            if response.status_code == 200:
                data = response.json()
                print(f" Server: {data['service']} {data['version']}")
                print("  New features:")
                for feature in data['new_features']:
                    print(f"    - {feature}")
                return True
            return False
        except requests.exceptions.ConnectionError:
            return False
    
    def get_books(self):
        print("\n[GET] Requesting all books...")
        
        start_time = time.time()
        response = self.session.get(f'{self.base_url}/api/books')
        duration = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            cache_status = response.headers.get('X-Cache-Status', 'UNKNOWN')
            cache_control = response.headers.get('Cache-Control', 'none')
            
            print(f"  Got {len(data['data'])} books")
            print(f"  Response time: {duration:.0f}ms")
            print(f"  Cache status: {cache_status}")
            print(f"  Cache-Control: {cache_control}")
            
            return data['data']
        else:
            print(f"  Error: {response.status_code}")
            return []
    
    def get_book(self, book_id):
        """Get single book and show cache status"""
        print(f"\n[GET] Requesting book {book_id}...")
        
        start_time = time.time()
        response = self.session.get(f'{self.base_url}/api/books/{book_id}')
        duration = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            cache_status = response.headers.get('X-Cache-Status', 'UNKNOWN')
            cache_control = response.headers.get('Cache-Control', 'none')
            
            print(f"  Got book: {data['data']['title']}")
            print(f"  Response time: {duration:.0f}ms")
            print(f"  Cache status: {cache_status}")
            print(f"  Cache-Control: {cache_control}")
            
            return data['data']
        else:
            print(f"  Error: {response.status_code}")
            return None
    
    def create_book(self, title, author, isbn):
        """Create a book (this will clear the cache)"""
        print(f"\n[POST] Creating book: {title}")
        
        response = self.session.post(
            f'{self.base_url}/api/books',
            json={'title': title, 'author': author, 'isbn': isbn},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            data = response.json()
            cache_control = response.headers.get('Cache-Control', 'none')
            
            print(f"  Book created: {data['data']['title']}")
            print(f"  Cache-Control: {cache_control}")
            print("  Note: This cleared the server cache!")
            
            return data['data']
        else:
            print(f"  Error: {response.status_code}")
            return None
    
    def get_stats(self):
        """Get real-time stats (never cached)"""
        print(f"\n[GET] Getting real-time stats...")
        
        start_time = time.time()
        response = self.session.get(f'{self.base_url}/api/stats')
        duration = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            cache_control = response.headers.get('Cache-Control', 'none')
            
            print(f"  {data['message']}")
            print(f"  Response time: {duration:.0f}ms")
            print(f"  Cache-Control: {cache_control}")
            print(f"  Total books: {data['data']['total_books']}")
            print(f"  Available: {data['data']['available_books']}")
            
            return data['data']
        else:
            print(f"  Error: {response.status_code}")
            return None
    
    def show_cache_status(self):
        """Show what's in the server cache"""
        print(f"\n[GET] Checking server cache status...")
        
        response = self.session.get(f'{self.base_url}/api/cache/status')
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Cache items: {data['data']['cached_items']}")
            if data['data']['cache_keys']:
                print(f"  Cached: {', '.join(data['data']['cache_keys'])}")
            else:
                print("  Cache is empty")
        else:
            print(f"  Error: {response.status_code}")

def demo_simple_cache():
    print("="*60)
    print("VERSION 2: SIMPLE CACHEABLE DEMO")
    print("="*60)
    print("\nThis demo shows:")
    print("1. First GET request = slow (database)")
    print("2. Second GET request = fast (cache)")
    print("3. POST request = clears cache")
    print("4. Next GET request = slow again (fresh data)")
    print("="*60)
    
    client = SimpleCacheClient()
    
    if not client.check_server_health():
        print("\n⚠️  Please start the server first:")
        print("   cd version2 && python Server.py")
        return
    client.show_cache_status()
    
    print(f"\n{'='*60}")
    print("DEMONSTRATING CACHING")
    print("="*60)
    
    print("\n1. First request - should be MISS (from database)")
    books = client.get_books()
    
    print("\n2. Same request immediately - should be HIT (from cache)")
    books = client.get_books()
    
    print("\n3. Request single book - should be MISS first time")
    if books:
        book = client.get_book(books[0]['id'])
    
    print("\n4. Same book again - should be HIT (from cache)")
    if books:
        book = client.get_book(books[0]['id'])
    
    print("\n5. Create new book - this will clear cache")
    client.create_book("Cache Test Book", "Test Author", "1234567890")
    
    print("\n6. Request books again - should be MISS (cache was cleared)")
    books = client.get_books()
    
    print("\n7. Real-time stats - NEVER cached")
    client.get_stats()
    
    print("\n8. Stats again - still not cached")
    client.get_stats()
    
    client.show_cache_status()

if __name__ == '__main__':
    demo_simple_cache()