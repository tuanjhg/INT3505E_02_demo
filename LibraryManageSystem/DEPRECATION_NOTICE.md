# 🚨 DEPRECATION NOTICE: Library Management System API v1

**Affected**: All API v1 endpoints (`/api/*`)

---

## Summary

The Library Management System API v1 will be **sunset on May 11, 2026**. All developers must migrate to API v2 before this date.

## What's Changing?

### API Endpoints

All v1 endpoints under `/api/` will be removed. You must update your code to use `/api/v2/`.

| v1 Endpoint (Deprecated) | v2 Endpoint (New) |
|--------------------------|-------------------|
| `POST /api/auth/login` | `POST /api/v2/auth/token` |
| `GET /api/books` | `GET /api/v2/books` |
| `POST /api/books` | `POST /api/v2/books` |
| `GET /api/books/{id}` | `GET /api/v2/books/{id}` |
| `PUT /api/books/{id}` | `PUT /api/v2/books/{id}` |
| `DELETE /api/books/{id}` | `DELETE /api/v2/books/{id}` |
| `POST /api/borrows` | `POST /api/v2/borrows` |
| `POST /api/borrows/{id}/return` | `PATCH /api/v2/borrows/{id}` |
| `GET /api/borrows` | `GET /api/v2/borrows` |

### Breaking Changes

#### 1. Pagination Parameters

**v1** (deprecated):
```http
GET /api/books?page=1&per_page=10
```

**v2** (required):
```http
GET /api/v2/books?limit=10&offset=0
```

#### 2. Response Format

**v1** (deprecated):
```json
{
  "success": true,
  "data": {
    "books": [...]
  },
  "message": "Books retrieved successfully"
}
```

**v2** (required):
```json
{
  "status": "success",
  "data": [...],
  "meta": {
    "pagination": {...},
    "timestamp": "2025-11-11T10:00:00Z",
    "request_id": "abc-123"
  }
}
```

#### 3. Error Responses

**v1** (deprecated):
```json
{
  "success": false,
  "message": "Book not found"
}
```

**v2** (required):
```json
{
  "status": "error",
  "errors": [
    {
      "code": "RESOURCE_NOT_FOUND",
      "message": "Book with ID 123 not found",
      "field": "book_id"
    }
  ],
  "meta": {
    "request_id": "abc-123",
    "timestamp": "2025-11-11T10:00:00Z"
  }
}
```

#### 4. Authentication

**v1** (deprecated):
- Endpoint: `POST /api/auth/login`
- Token expiry: 24 hours
- No refresh tokens

**v2** (required):
- Endpoint: `POST /api/v2/auth/token`
- Token expiry: 1 hour
- Refresh tokens supported
- Response includes `access_token` and `refresh_token`

#### 5. Date/Time Format

**v2 requirement**: All dates must be ISO 8601 with timezone (UTC)

```json
{
  "borrow_date": "2025-11-11T10:00:00Z",
  "due_date": "2025-11-25T10:00:00Z"
}
```

#### 6. HTTP Methods

**v1**: Used POST for returns
```http
POST /api/borrows/123/return
```

**v2**: RESTful PATCH
```http
PATCH /api/v2/borrows/123
Content-Type: application/json

{
  "returned": true,
  "return_date": "2025-11-11T10:00:00Z"
}
```

---

## Action Required

### Immediate Actions (This Week)

1. **Review your integration**
   - Identify all v1 API calls in your codebase
   - Estimate migration effort
   - Plan your migration timeline

2. **Test in sandbox**
   - Access v2 sandbox: `https://api-sandbox.library.example.com/v2`
   - Use your existing API keys (they work with both versions)
   - Test critical workflows

3. **Update dependencies**
   - If using our SDK, upgrade to v2.x:
     ```bash
     pip install library-api-client==2.0.0
     # or
     npm install @library/api-client@2.0.0
     ```


4. **Complete migration**
   - Update all API calls to v2 endpoints
   - Update pagination logic
   - Handle new response formats
   - Test error handling with new structure

5. **Update monitoring/logging**
   - Update any hard-coded URLs
   - Update response parsers
   - Add `request_id` to your logs for debugging


6. **Remove v1 references**
   - Delete all v1 code paths
   - Update documentation
   - Verify 100% v2 usage

---

## Migration Resources

### Documentation

📚 **Migration Guide**: [`MIGRATION_GUIDE_V1_TO_V2.md`](./MIGRATION_GUIDE_V1_TO_V2.md)  
📖 **API Reference**: https://docs.library.example.com/api/v2  
📋 **Changelog**: https://docs.library.example.com/api/changelog  
🔧 **Postman Collection**: https://docs.library.example.com/postman/v2

### Code Examples

**Quick Migration Example (Python)**:

```python
# ❌ OLD (v1)
response = requests.get(
    "https://api.library.example.com/api/books",
    params={"page": 1, "per_page": 10},
    headers={"Authorization": f"Bearer {token}"}
)
books = response.json()["data"]["books"]

# ✅ NEW (v2)
response = requests.get(
    "https://api.library.example.com/api/v2/books",
    params={"limit": 10, "offset": 0},
    headers={"Authorization": f"Bearer {token}"}
)
books = response.json()["data"]
```

**JavaScript/Node.js**:

```javascript
// ❌ OLD (v1)
const response = await fetch(
  'https://api.library.example.com/api/books?page=1&per_page=10',
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const { data: { books } } = await response.json();

// ✅ NEW (v2)
const response = await fetch(
  'https://api.library.example.com/api/v2/books?limit=10&offset=0',
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const { data: books } = await response.json();
```

### Migration Tools

🛠️ **Migration Script**: Automated tool to help identify v1 calls
```bash
# Download migration scanner
curl -O https://tools.library.example.com/v1-scanner.sh
chmod +x v1-scanner.sh

# Scan your codebase
./v1-scanner.sh /path/to/your/project

# Output: List of files with v1 API calls
```

---


### v1 Endpoint Behavior

All v1 endpoints will return:

```http
HTTP/1.1 410 Gone
Content-Type: application/json

{
  "status": "error",
  "errors": [
    {
      "code": "API_VERSION_SUNSET",
      "message": "API v1 has been sunset as of May 11, 2026. Please migrate to v2.",
      "documentation_url": "https://docs.library.example.com/api/v2/migration"
    }
  ]
}
```


## FAQ

**Q: Will my API key stop working?**  
A: No, your API key works with both v1 and v2. Only the endpoints change.

**Q: Can I use v1 and v2 at the same time?**  
A: Yes, during the 6-month transition period (until May 11, 2026).

**Q: What if I miss the deadline?**  
A: Your application will break. v1 endpoints will return HTTP 410 Gone.

**Q: Is there a v2 SDK?**  
A: Yes:
- Python: `pip install library-api-client>=2.0.0`
- Node.js: `npm install @library/api-client@2.0.0`
- PHP: `composer require library/api-client:^2.0`

**Q: Are there new features in v2?**  
A: Yes:
- Refresh token support
- Better error handling
- Rate limiting headers
- Request tracing with `request_id`
- Improved filtering and sorting

**Q: How do I know when I've fully migrated?**  
A: Check your logs for v1 API calls. We also provide usage stats in your developer dashboard.

**Q: What about webhooks?**  
A: Webhook payloads will also change. See the migration guide for details.

---
