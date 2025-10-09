# Code-On-Demand

## RESTful Constraint #6: Code-On-Demand (Optional)

### Overview
Code-on-demand is the **only optional constraint** in REST architecture. It allows the server to extend client functionality by transferring executable code that the client can execute. This reduces the complexity of clients by allowing features to be downloaded after deployment.

### Key Principles
1. **Optional**: Unlike other constraints, this is not required for REST
2. **Dynamic Code Transfer**: Server sends executable code to client
3. **Runtime Extension**: Client functionality extended at runtime
4. **Reduced Pre-Implementation**: Client doesn't need all features upfront

### Common Examples

#### 1. JavaScript for Web Browsers
The most common example of code-on-demand:
```html
<!-- Client loads JavaScript from server -->
<script src="/api/validation/isbn.js"></script>
```

Server sends executable code that runs in the browser:
```javascript
// This code comes from the server
function validateISBN(isbn) {
    // Validation logic can be updated on server
    // without changing client
    return isbn.length === 13 || isbn.length === 10;
}
```

#### 2. Applets and Plugins
- Java applets (historical)
- Flash applications (historical)
- WebAssembly modules (modern)

#### 3. Dynamic UI Components
```javascript
// Server sends React/Vue components
fetch('/api/widgets/book-card.js')
    .then(response => response.text())
    .then(code => eval(code));  // Execute server code
```

#### 4. Business Logic Updates
```javascript
// Server can update calculation logic
fetch('/api/rules/late-fee-calculator.js')
    .then(response => response.text())
    .then(code => {
        // Client now has updated late fee logic
        // without app update
    });
```

### Benefits

#### 1. Reduced Client Complexity
- Client starts with minimal code
- Features loaded on-demand
- Smaller initial download

#### 2. Flexibility
- Server controls client behavior
- Update logic without client updates
- A/B testing of features
- Feature flags implementation

#### 3. Extensibility
- Add new features without client deployment
- Platform-specific optimizations
- Dynamic feature discovery

#### 4. Centralized Updates
- Fix bugs by updating server code
- All clients get updates automatically
- No app store approval needed (web)

### Drawbacks

#### 1. Security Concerns
- Executing server-provided code is risky
- Code injection vulnerabilities
- Trust required in server

#### 2. Visibility Reduction
- Harder to see what client is doing
- Dynamic behavior is less predictable
- Debugging complexity

#### 3. Dependency on Network
- Requires connectivity to get code
- May fail if server unavailable
- Offline functionality limited

### Why It's Optional

REST works perfectly fine without code-on-demand:
- **Most REST APIs don't use it**: Traditional REST APIs are code-on-demand free
- **Not always appropriate**: Many use cases don't need it
- **Security concerns**: Some environments prohibit executable code download
- **Complexity trade-off**: Can make systems more complex

### Implementation Examples

#### Example 1: Client-Side Validation
**Server endpoint** (`/api/validation/isbn.js`):
```javascript
function validateISBN(isbn) {
    // Server-controlled validation logic
    isbn = isbn.replace(/[-\s]/g, '');
    if (isbn.length === 13) {
        // ISBN-13 validation logic
        return validateISBN13(isbn);
    }
    // ...more validation
}
```

**Client usage**:
```html
<script src="/api/validation/isbn.js"></script>
<script>
    // Use server-provided validation
    const result = validateISBN(userInput);
</script>
```

#### Example 2: Dynamic UI Widget
**Server endpoint** (`/api/widgets/book-card.js`):
```javascript
class BookCard {
    render(book) {
        // Server controls presentation
        return `
            <div class="book">
                <h3>${book.title}</h3>
                <p>${book.author}</p>
            </div>
        `;
    }
}
```

**Client usage**:
```javascript
// Load widget from server
await loadScript('/api/widgets/book-card.js');

// Use server-provided component
const widget = new BookCard();
widget.render(bookData);
```

### Security Considerations

#### Best Practices:
1. **Content Security Policy (CSP)**: Restrict what code can execute
2. **Code Signing**: Verify code authenticity
3. **Sandboxing**: Isolate execution environment
4. **HTTPS Only**: Ensure secure transmission
5. **Validation**: Verify code before execution

#### Dangerous:
```javascript
// NEVER DO THIS - Direct eval of server response
fetch('/api/code')
    .then(r => r.text())
    .then(code => eval(code));  // UNSAFE!
```

#### Better:
```javascript
// Use script tags with proper CSP
const script = document.createElement('script');
script.src = '/api/code';
script.integrity = 'sha384-...';  // Subresource Integrity
document.head.appendChild(script);
```

### When to Use Code-On-Demand

#### ✓ Good Use Cases:
- Web applications (JavaScript naturally fits)
- Frequently changing business rules
- A/B testing different implementations
- Platform-specific optimizations
- Dynamic form validation
- UI component updates

#### ✗ Poor Use Cases:
- Mobile native apps (security restrictions)
- High-security environments
- Offline-first applications
- Simple CRUD APIs
- When visibility is critical

### Alternatives to Code-On-Demand

If you don't want code-on-demand but need flexibility:

1. **Configuration Data**:
```json
{
    "validation": {
        "isbn": {
            "minLength": 10,
            "maxLength": 13,
            "pattern": "^[0-9X]+$"
        }
    }
}
```

2. **Declarative Rules**:
```json
{
    "rules": [
        {"field": "isbn", "required": true},
        {"field": "isbn", "length": [10, 13]}
    ]
}
```

3. **Server-Side Execution**:
```javascript
// Instead of client executing code,
// send data to server for processing
POST /api/validate-isbn
Body: {"isbn": "1234567890"}
```

### How to Run

1. **Start the Code-On-Demand Server:**
```bash
python DynamicLoader.py
```
Server runs on http://127.0.0.1:5006

2. **Open in Browser:**
```
http://127.0.0.1:5006
```

3. **Observe Code Loading:**
- Open browser console (F12)
- Watch JavaScript load from server
- See dynamic validation and UI rendering

### Code Endpoints

- `GET /` - Interactive demo page
- `GET /api/validation/isbn.js` - Validation logic (executable)
- `GET /api/widgets/book-card.js` - UI widget (executable)
- `GET /api/books` - Standard REST endpoint

### Real-World Examples

#### 1. Modern Web Applications
- React/Vue components loaded on-demand
- Code-splitting for performance
- Dynamic imports in JavaScript

#### 2. Google Maps API
```html
<script src="https://maps.googleapis.com/maps/api/js"></script>
<!-- Google sends code that extends your app -->
```

#### 3. Payment Gateways
```html
<script src="https://js.stripe.com/v3/"></script>
<!-- Stripe sends code for payment processing -->
```

#### 4. Analytics
```html
<script src="https://www.google-analytics.com/analytics.js"></script>
<!-- Google sends tracking code -->
```

### Summary

Code-on-demand:
- ✓ Is the only **optional** REST constraint
- ✓ Allows server to send executable code
- ✓ Reduces client complexity
- ✓ Enables dynamic feature updates
- ✓ Most common in web browsers (JavaScript)
- ✗ Has security implications
- ✗ Reduces visibility
- ✗ Not suitable for all environments

**Most REST APIs work perfectly well without it!**
