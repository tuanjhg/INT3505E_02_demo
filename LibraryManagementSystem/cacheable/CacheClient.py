"""
Cacheable Client Demo

Demonstrates how clients can leverage HTTP caching for better performance:
- Cache-Control headers
- ETags for validation
- Conditional requests
"""

import requests
import time
from datetime import datetime

class CacheAwareClient:
    """
    Client that respects HTTP caching headers
    """
    
    def __init__(self, base_url='http://127.0.0.1:5003'):
        self.base_url = base_url
        self.cache = {}  # Simple client-side cache
    
    def get(self, endpoint, use_cache=True):
        """
        Make GET request with cache awareness
        """
        url = f'{self.base_url}{endpoint}'
        
        # Check client-side cache
        if use_cache and url in self.cache:
            cached_entry = self.cache[url]
            
            # Check if cache is still fresh
            if time.time() < cached_entry['expires']:
                print(f"  [CLIENT CACHE] Using cached response")
                print(f"  Age: {int(time.time() - cached_entry['cached_at'])}s")
                return cached_entry['data'], True  # From cache
            
            # Cache expired, but we can validate with ETag
            if 'etag' in cached_entry:
                print(f"  [VALIDATION] Checking if cache is still valid (ETag: {cached_entry['etag'][:8]}...)")
                headers = {'If-None-Match': cached_entry['etag']}
                
                try:
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 304:
                        # Cache is still valid, update expiry
                        print(f"  ✓ 304 Not Modified - Cache still valid!")
                        max_age = self._parse_max_age(response.headers.get('Cache-Control', ''))
                        cached_entry['expires'] = time.time() + max_age
                        return cached_entry['data'], True
                except Exception as e:
                    print(f"  ✗ Validation failed: {e}")
        
        # Make fresh request
        print(f"  [REQUEST] {endpoint}")
        try:
            start_time = time.time()
            response = requests.get(url)
            duration = (time.time() - start_time) * 1000
            
            print(f"  Response time: {duration:.0f}ms")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check caching headers
                cache_control = response.headers.get('Cache-Control', '')
                etag = response.headers.get('ETag')
                x_cache = response.headers.get('X-Cache', 'N/A')
                age = response.headers.get('Age', '0')
                
                print(f"  Cache-Control: {cache_control}")
                print(f"  ETag: {etag[:8] + '...' if etag else 'None'}")
                print(f"  X-Cache: {x_cache}")
                print(f"  Age: {age}s")
                
                # Store in client cache if cacheable
                if 'no-store' not in cache_control and 'no-cache' not in cache_control:
                    max_age = self._parse_max_age(cache_control)
                    if max_age > 0:
                        self.cache[url] = {
                            'data': data,
                            'etag': etag,
                            'cached_at': time.time(),
                            'expires': time.time() + max_age
                        }
                        print(f"  [CLIENT CACHE] Stored for {max_age}s")
                
                return data, False  # Fresh from server
            else:
                print(f"  ✗ Error: {response.status_code}")
                return None, False
        except Exception as e:
            print(f"  ✗ Request failed: {e}")
            return None, False
    
    def post(self, endpoint, data):
        """POST request (not cacheable)"""
        url = f'{self.base_url}{endpoint}'
        print(f"  [POST] {endpoint}")
        
        try:
            response = requests.post(url, json=data)
            
            # POST responses should not be cached
            cache_control = response.headers.get('Cache-Control', '')
            print(f"  Cache-Control: {cache_control}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"  ✗ Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"  ✗ Request failed: {e}")
            return None
    
    def put(self, endpoint, data):
        """PUT request (not cacheable)"""
        url = f'{self.base_url}{endpoint}'
        print(f"  [PUT] {endpoint}")
        
        try:
            response = requests.put(url, json=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  ✗ Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"  ✗ Request failed: {e}")
            return None
    
    def _parse_max_age(self, cache_control):
        """Extract max-age from Cache-Control header"""
        for directive in cache_control.split(','):
            directive = directive.strip()
            if directive.startswith('max-age='):
                return int(directive.split('=')[1])
        return 0
    
    def clear_client_cache(self):
        """Clear client-side cache"""
        self.cache.clear()
        print("  [CLIENT CACHE] Cleared")
    
    def get_cache_stats(self):
        """Get client cache statistics"""
        return {
            'entries': len(self.cache),
            'urls': list(self.cache.keys())
        }


def demo_cacheable():
    """Demonstrate caching behavior"""
    print("="*70)
    print("CACHEABLE ARCHITECTURE DEMONSTRATION")
    print("="*70)
    
    client = CacheAwareClient()
    
    # Test 1: Cacheable GET request
    print("\n[Test 1] First request - should cache")
    print("-" * 70)
    data, from_cache = client.get('/api/books')
    if data:
        print(f"  Retrieved {len(data['data'])} books")
    
    # Test 2: Immediate second request - should use cache
    print("\n[Test 2] Immediate second request - should use client cache")
    print("-" * 70)
    data, from_cache = client.get('/api/books')
    if from_cache:
        print("  ✓ Served from client cache - NO network request!")
    
    # Test 3: Third request - still cached
    print("\n[Test 3] Third request - still in cache window")
    print("-" * 70)
    time.sleep(1)
    data, from_cache = client.get('/api/books')
    
    # Test 4: Non-cacheable request
    print("\n[Test 4] Real-time stats - NOT cacheable")
    print("-" * 70)
    client.get('/api/stats/realtime')
    
    print("\n[Test 5] Immediate repeat of stats - NOT cached")
    print("-" * 70)
    client.get('/api/stats/realtime')
    print("  Notice: Same request again, but not cached (no-store)")
    
    # Test 6: Modify data (invalidates cache)
    print("\n[Test 6] Create new book - invalidates server cache")
    print("-" * 70)
    client.post('/api/books', {
        'title': 'Test Book',
        'author': 'Test Author',
        'isbn': '1234567890123'
    })
    
    # Test 7: Cached endpoint after modification
    print("\n[Test 7] Request books again - cache was invalidated")
    print("-" * 70)
    client.clear_client_cache()  # Clear client cache to test server cache
    data, from_cache = client.get('/api/books', use_cache=False)
    print("  Server had to regenerate response (cache was invalidated)")
    
    # Test 8: Cache validation with ETag
    print("\n[Test 8] Wait for cache to expire, then validate")
    print("-" * 70)
    print("  (In production, this would wait for cache expiry)")
    print("  Simulating: Server validates cache with ETag...")
    # Clear client cache and make request - server may return 304
    time.sleep(2)
    data, from_cache = client.get('/api/books/1')
    
    # Summary
    print("\n" + "="*70)
    print("PERFORMANCE BENEFITS:")
    print("="*70)
    print("\n1. CACHEABLE Endpoints (GET /api/books):")
    print("   - First request: Full response from server")
    print("   - Subsequent requests: Served from cache")
    print("   - Result: Reduced latency, bandwidth, server load")
    print("\n2. NON-CACHEABLE Endpoints (POST, Real-time data):")
    print("   - Every request hits server")
    print("   - Ensures data freshness")
    print("   - Appropriate for write operations")
    print("\n3. Cache Validation (ETags):")
    print("   - Avoids transferring unchanged data")
    print("   - 304 Not Modified responses are tiny")
    print("   - Bandwidth savings while ensuring freshness")
    
    # Show cache stats
    client_stats = client.get_cache_stats()
    print(f"\nClient Cache: {client_stats['entries']} entries")
    
    print("\n" + "="*70)
    print("REST CACHING BEST PRACTICES:")
    print("="*70)
    print("✓ Use Cache-Control headers to mark cacheability")
    print("✓ Cache GET requests for read-only data")
    print("✓ Never cache POST/PUT/DELETE (write operations)")
    print("✓ Use ETags for cache validation")
    print("✓ Set appropriate max-age based on data volatility")
    print("✓ Invalidate cache when data changes")
    print("="*70)


if __name__ == '__main__':
    demo_cacheable()
