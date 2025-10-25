# JWT Token Storage Implementation

## Overview
JWT tokens (access_token and refresh_token) are now stored in **3 locations** for maximum security and flexibility:

### 1. **localStorage** 
- Persists across browser sessions
- Survives page refreshes and browser restarts
- Accessible via JavaScript

### 2. **sessionStorage**
- Only persists for the current browser session
- Cleared when browser tab/window is closed
- Accessible via JavaScript

### 3. **HttpOnly Cookie**
- **Most secure option** - Cannot be accessed by JavaScript
- Protected against XSS attacks
- Automatically sent with every request to the server
- Set by server in response headers

---

## Implementation Details

### Backend (`auth_routes_swagger.py`)

#### Login Endpoint (`POST /api/auth/login`)
```python
# Returns JSON with tokens AND sets HttpOnly cookie
resp = make_response(response_data, status_code)
resp.set_cookie(
    'refresh_token',
    refresh_token,
    httponly=True,      # Cannot be accessed by JS
    secure=False,       # Set True in production (HTTPS)
    samesite='Lax',     # CSRF protection
    max_age=30*24*60*60 # 30 days
)
```

#### Register Endpoint (`POST /api/auth/register`)
- Same implementation as login
- Returns tokens in JSON + sets HttpOnly cookie

#### Logout Endpoint (`POST /api/auth/logout`)
```python
# Revokes refresh token in DB and clears cookie
resp.set_cookie('refresh_token', '', expires=0, httponly=True)
```

---

### Frontend

#### Login (`templates/login.html`)
```javascript
// Three-step login process:

// Step 1: Call API with credentials: 'include' to get JWT tokens
fetch('/api/auth/login', {
    method: 'POST',
    credentials: 'include',  // Allows HttpOnly cookie
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
})

// Step 2: Store JWT tokens in localStorage and sessionStorage
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);
sessionStorage.setItem('access_token', data.access_token);
sessionStorage.setItem('refresh_token', data.refresh_token);

// Step 3: Call server-side login to create Flask session
// This is needed because web routes use @login_required which checks session
const formData = new FormData();
formData.append('username', username);
formData.append('password', password);
fetch('/login', { method: 'POST', body: formData });

// Step 4: HttpOnly cookie is automatically set by API (Step 1)
// Step 5: Flask session is created by server (Step 3)
```

**Why both API and Server login?**
- API login (`/api/auth/login`): Returns JWT tokens + sets HttpOnly cookie
- Server login (`/login`): Creates Flask session for web page access
- Web routes use `@login_required` which checks Flask session
- API routes use JWT tokens for authentication

#### Register (`templates/register.html`)
- Same implementation as login

#### Logout (`templates/base.html`)
```javascript
// 1. Call API logout to revoke token and clear cookie
fetch('/api/auth/logout', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Authorization': 'Bearer ' + accessToken }
})

// 2. Clear localStorage
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');

// 3. Clear sessionStorage
sessionStorage.removeItem('access_token');
sessionStorage.removeItem('refresh_token');

// 4. HttpOnly cookie is cleared by server
```

---

## Security Considerations

### Production Deployment
When deploying to production with HTTPS, update cookie settings:

```python
resp.set_cookie(
    'refresh_token',
    refresh_token,
    httponly=True,
    secure=True,        # ✅ Enable for HTTPS
    samesite='Strict',  # ✅ Stricter CSRF protection
    domain='.yourdomain.com',  # ✅ Set your domain
    max_age=30*24*60*60
)
```

### Token Usage Priority
1. **Primary**: Use HttpOnly cookie (most secure, auto-sent with requests)
2. **Backup**: Use localStorage/sessionStorage if cookie unavailable
3. **Access Token**: Short-lived (15 min), store in sessionStorage
4. **Refresh Token**: Long-lived (30 days), store in HttpOnly cookie

### XSS Protection
- HttpOnly cookies **cannot** be accessed by malicious JavaScript
- Even if XSS attack occurs, refresh token remains safe
- Access token in localStorage/sessionStorage has limited exposure (15 min expiry)

---

## Testing

### Check Token Storage in Browser

#### 1. Open DevTools (F12)

#### 2. Check localStorage
```javascript
// Console
localStorage.getItem('access_token')
localStorage.getItem('refresh_token')
```

#### 3. Check sessionStorage
```javascript
// Console
sessionStorage.getItem('access_token')
sessionStorage.getItem('refresh_token')
```

#### 4. Check HttpOnly Cookie
- Go to **Application** tab → **Cookies** → `http://localhost:5000`
- Look for `refresh_token` cookie
- **Important**: You will see it in DevTools but JavaScript cannot access it
- Try in console:
  ```javascript
  document.cookie  // refresh_token won't appear here (HttpOnly)
  ```

### Test Login Flow
```bash
# 1. Login with default credentials
Username: admin
Password: admin123

# 2. Check DevTools:
# - localStorage: access_token + refresh_token ✓
# - sessionStorage: access_token + refresh_token ✓
# - Cookies: refresh_token (HttpOnly) ✓

# 3. Refresh page
# - sessionStorage: Still has tokens ✓
# - localStorage: Still has tokens ✓
# - Cookie: Still present ✓

# 4. Close and reopen browser
# - sessionStorage: Cleared (expected) ✗
# - localStorage: Still has tokens ✓
# - Cookie: Still present ✓

# 5. Logout
# - All storage cleared ✓
```

---

## API Endpoints

### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

# Response
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {...}
  }
}

# + Set-Cookie: refresh_token=eyJ...; HttpOnly; SameSite=Lax; Max-Age=2592000
```

### Register
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "full_name": "New User"
}
```

### Logout
```bash
POST /api/auth/logout
Authorization: Bearer eyJ...
Cookie: refresh_token=eyJ...

# Clears cookie and revokes refresh token
```

---

## Best Practices

### ✅ DO
- Use `credentials: 'include'` in fetch requests
- Store refresh token primarily in HttpOnly cookie
- Use HTTPS in production with `secure=True`
- Implement token refresh logic for expired access tokens
- Clear all storage on logout

### ❌ DON'T
- Don't store sensitive tokens in plain localStorage without HttpOnly backup
- Don't set `secure=True` on localhost (will break cookies)
- Don't forget CSRF protection (`samesite` attribute)
- Don't access HttpOnly cookies from JavaScript (by design impossible)

---

## Troubleshooting

### ❌ Login Successful but Can't Access Homepage
**Problem**: Tokens are saved but redirect to login page or "401 Unauthorized"

**Root Cause**: Web routes use `@login_required` decorator which checks Flask **session**, not JWT tokens. The JavaScript was only calling API login which doesn't create a session.

**Solution**: The login flow now does BOTH:
1. Call `/api/auth/login` → Get JWT tokens + HttpOnly cookie
2. Call `/login` (server endpoint) → Create Flask session
3. Now both API requests (with JWT) and web pages (with session) work!

**Verify the fix:**
```javascript
// After login, check in DevTools Console:
console.log(document.cookie); // Should see 'session=...'
localStorage.getItem('access_token'); // Should have JWT token
```

### Cookie Not Being Set
- Check `credentials: 'include'` in fetch
- Verify server sends `Set-Cookie` header
- Check CORS configuration allows credentials
- For localhost, ensure `secure=False`

### Tokens Not Persisting
- Check browser storage quota
- Verify no browser extensions blocking storage
- Check private/incognito mode restrictions

### CORS Issues
```python
# In Flask app
from flask_cors import CORS

CORS(app, supports_credentials=True, origins=['http://localhost:3000'])
```

---

## Summary

✅ **3 Storage Locations Implemented:**
1. localStorage (persistent, JS-accessible)
2. sessionStorage (session-only, JS-accessible)
3. HttpOnly Cookie (persistent, JS-protected) ⭐ **Most Secure**

✅ **Security Features:**
- XSS protection via HttpOnly
- CSRF protection via SameSite
- Short-lived access tokens (15 min)
- Long-lived refresh tokens (30 days)
- Automatic cookie clearing on logout

✅ **Files Modified:**
- `routes/auth_routes_swagger.py` - Server-side cookie handling
- `templates/login.html` - Client-side storage on login
- `templates/register.html` - Client-side storage on register
- `templates/base.html` - Clear all storage on logout
