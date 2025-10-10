# RESTful Architecture Evolution - Library Management System

## Overview

This project demonstrates the **progressive evolution of REST constraints** through a simple library management system. Each version builds upon the previous one, showing how REST constraints work together to create better APIs.

## Version Evolution

### Version 1: Client-Server (Base)
- **Location**: `version1/` (originally `client-server/`)
- **Constraint**: Client-Server separation
- **What it does**: Basic API with client and server separation
- **Key concepts**: Separation of concerns, independent evolution

### Version 2: + Cacheable  
- **Location**: `version2/`
- **Constraint**: Client-Server + Cacheable
- **What it does**: Adds simple HTTP caching to Version 1
- **Key concepts**: Cache-Control headers, GET responses cached, POST clears cache

### Version 3: + Uniform Interface
- **Location**: `version3/`  
- **Constraint**: Client-Server + Cacheable + Uniform Interface
- **What it does**: Adds standard HTTP methods and HATEOAS links to Version 2
- **Key concepts**: GET/POST/PUT/DELETE, HATEOAS links, better error messages

### Version 4: + Stateless
- **Location**: `version4/`
- **Constraint**: Client-Server + Cacheable + Uniform Interface + Stateless
- **What it does**: Adds stateless authentication to Version 3
- **Key concepts**: API keys, no server sessions, self-contained requests

## Quick Start

### Run Any Version
```bash
# Choose a version (1, 2, 3, or 4)
cd version4

# Start the server
python Server.py

# In another terminal, run the client demo
python Client.py
```

## Key Learning Points

### Version 1 → 2: Adding Caching
- **Problem**: Every request hits the database (slow)
- **Solution**: Cache GET responses, clear cache on data changes
- **Result**: Faster responses, less server load

### Version 2 → 3: Adding Uniform Interface  
- **Problem**: Inconsistent API behavior
- **Solution**: Standard HTTP methods, HATEOAS links, better errors
- **Result**: Predictable API, self-documenting through links

### Version 3 → 4: Adding Stateless
- **Problem**: Server sessions don't scale well
- **Solution**: API keys with every request, no server session storage
- **Result**: Better scalability, simpler load balancing

## Simple Examples

### Version 1: Basic Client-Server
```python
# Server provides API endpoints
@app.route('/api/books', methods=['GET'])
def get_books():
    return jsonify({'data': books})

# Client consumes API
response = requests.get('http://server/api/books')
```

### Version 2: + Caching
```python
# Server adds caching
if 'books' in cache:
    return cached_response  # Fast!
else:
    return fresh_response   # Slower, but cached for next time
```

### Version 3: + Uniform Interface
```python
# Server adds HATEOAS links
{
  "data": {...},
  "_links": {
    "update": {"href": "/api/books/1", "method": "PUT"},
    "delete": {"href": "/api/books/1", "method": "DELETE"}
  }
}
```

### Version 4: + Stateless
```python
# Every request includes authentication
headers = {'Authorization': 'Bearer api_key_here'}
response = requests.get('/api/books', headers=headers)
# Server extracts user from token (no session lookup)
```

## Prerequisites
```bash
pip install Flask Flask-SQLAlchemy requests
```

## Testing Examples

### Version 4 (Full REST)
```bash
# Start server
cd version4
python Server.py

# Test with client
python Client.py

# Manual testing
curl http://127.0.0.1:5001/api/auth/token -X POST
curl http://127.0.0.1:5001/api/books -H "Authorization: Bearer YOUR_TOKEN"
```