# 🚨 API Error Guide — All Edge Cases Explained

This guide explains every error you'll encounter and why it happens.

---

## 🔴 Authentication Errors (401, 403)

### 401 Unauthorized — No Token
**Error Response:**
```json
{ "detail": "Authentication credentials were not provided." }
```

**When it happens:**
- Missing `Authorization: Bearer <token>` header
- Token is invalid or expired
- Token is empty string

**Why:**
The endpoint requires authentication. All endpoints except `/sessions/` (list), `/sessions/<id>/` (detail), and `/health/` need a valid JWT token.

**Fix:**
```bash
# Include the Authorization header
curl -H "Authorization: Bearer eyJhbGc..." http://127.0.0.1:8000/api/v1/auth/profile/
```

**Postman:**
1. In the request, go to **Auth** tab
2. Select **Bearer Token**
3. Paste your `access` token from login response

---

### 401 Unauthorized — Invalid Token
**Error Response:**
```json
{ "detail": "Token is invalid or expired" }
```

**When it happens:**
- Token has been tampered with
- Token has expired (access tokens last 60 minutes)
- Token was blacklisted (after logout)
- Token string is malformed

**Why:**
JWT tokens are cryptographically signed. If any part is modified or the signature is invalid, Django rejects it.

**Fix:**
1. Get a new token:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"creator1","password":"creator123"}'
```

2. If token is expired, refresh it:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

---

### 403 Forbidden — Wrong Role
**Error Response:**
```json
{ "detail": "You must be a Creator to perform this action." }
```

**When it happens:**
- A regular **user** tries to:
  - Create a session
  - View `/sessions/mine/` (creator dashboard)
  - View `/bookings/creator/` (creator booking overview)
- A **creator** tries to book a session (they should only create)

**Why:**
The endpoint has role-based access control. Some endpoints are restricted to the `creator` role.

**Fix:**
1. If you're a user wanting to create sessions, switch roles:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/profile/role/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"role":"creator"}'
```

2. The response will include new tokens with the updated role claim. Use the new `access` token.

---

## 🔴 Validation Errors (400 Bad Request)

### 400 — Missing Required Field
**Error Response:**
```json
{
  "errors": [
    { "field": "title", "message": "This field is required." },
    { "field": "description", "message": "This field is required." }
  ]
}
```

**When it happens:**
- POST/PATCH request body is missing required fields
- Field values are null or empty when they shouldn't be

**Why:**
Django REST Framework validates serializer input before saving to database. Invalid data is rejected at the API layer.

**Fix:**
Include all required fields in the request body. For create session:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sessions/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Morning Yoga",
    "description": "60-minute yoga session",
    "price": "19.99",
    "duration_minutes": 60,
    "max_attendees": 10,
    "scheduled_at": "2026-08-01T08:00:00Z",
    "status": "published",
    "tags": ["yoga", "fitness"]
  }'
```

---

### 400 — Invalid Field Format
**Error Response:**
```json
{
  "errors": [
    { "field": "price", "message": "Ensure this value is greater than or equal to 0." }
  ]
}
```

**When it happens:**
- `price` is negative
- `max_attendees` is 0 or negative
- `scheduled_at` is not a valid ISO datetime
- `status` is not one of: `draft`, `published`, `cancelled`
- `role` is not one of: `user`, `creator`

**Why:**
Each field has validation rules. Negative prices don't make sense for bookings. Dates must be parseable.

**Fix:**
Check field types and valid values:

| Field | Type | Valid Values | Example |
|-------|------|--------------|---------|
| `price` | decimal | ≥ 0 | "19.99" |
| `max_attendees` | integer | ≥ 1 | 10 |
| `duration_minutes` | integer | ≥ 1 | 60 |
| `status` (session) | string | `draft`, `published`, `cancelled` | "published" |
| `status` (booking) | string | `pending`, `confirmed`, `cancelled`, `completed` | "confirmed" |
| `role` | string | `user`, `creator` | "creator" |
| `scheduled_at` | ISO datetime | RFC 3339 format | "2026-08-01T08:00:00Z" |

---

### 400 — Business Logic Violation
**Error Response:**
```json
{ "detail": "You have already booked this session." }
```

**When it happens:**
- User tries to book the same session twice
- User tries to cancel a booking that's already cancelled
- Creator tries to delete a session with confirmed bookings
- User tries to book a session that's full (max_attendees reached)
- User tries to book a cancelled session

**Why:**
The service layer enforces business rules. A user shouldn't be able to:
- Book twice and pay twice for the same session
- Cancel an already-cancelled booking (idempotence)
- Double-book when spots are full

**Fix:**
Check the session's `spots_remaining` before booking:

```bash
# Get session detail to check availability
curl http://127.0.0.1:8000/api/v1/sessions/2/

# Response includes:
# "spots_remaining": 5,
# "is_available": true
```

If `is_available` is `false` or `spots_remaining` is 0, the session is full.

---

## 🔴 Not Found Errors (404)

### 404 — Resource Not Found
**Error Response:**
```json
{ "detail": "Not found." }
```

**When it happens:**
- Accessing `/api/v1/sessions/99999/` (session doesn't exist)
- Accessing `/api/v1/bookings/99999/` (booking doesn't exist)
- Accessing `/api/v1/auth/profile/999/` (profile doesn't exist)

**Why:**
The database query returned no results. The resource ID doesn't exist or was deleted.

**Fix:**
1. Verify the resource exists:
```bash
# List sessions to find valid IDs
curl http://127.0.0.1:8000/api/v1/sessions/

# Response shows IDs in results
```

2. Use a valid ID from the response

---

## 🔴 Server Errors (500)

### 500 — Unhandled Exception
**Error Response:**
```json
{ "detail": "An unexpected error occurred. Please try again later." }
```

**When it happens:**
- Database connection failure
- Serializer raises unexpected exception
- Custom code in services.py throws unhandled error

**Why:**
An exception wasn't caught and handled gracefully. The error is logged server-side.

**Fix:**
1. Check server logs:
```bash
# If using our dev setup, look at Django console output
# Errors are printed there with full traceback
```

2. Common causes:
   - Database is down: `docker ps` and check `sessions_db` status
   - Invalid data type in request
   - Broken relationship (e.g., booking to non-existent session)

---

## ✅ Success Responses

### 200 OK
**When:** GET request succeeds, data retrieved

**Example:**
```bash
curl http://127.0.0.1:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer <token>"

# Response:
{
  "id": 1,
  "email": "creator@test.com",
  "username": "creator1",
  "role": "creator",
  "first_name": "Creator",
  "last_name": "One",
  "bio": "Full stack dev",
  "avatar": null,
  "date_joined": "2026-06-03T06:27:02.710644Z"
}
```

---

### 201 Created
**When:** POST request creates new resource

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/sessions/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"...","description":"...","price":"19.99",...}'

# Response (201 status):
{
  "id": 5,
  "title": "New Session",
  "description": "...",
  "status": "published",
  "created_at": "2026-06-03T07:00:00Z",
  ...
}
```

---

### 204 No Content
**When:** DELETE request succeeds, no body returned

**Example:**
```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/sessions/5/ \
  -H "Authorization: Bearer <token>"

# Response (204 status, empty body)
```

---

## 📊 Pagination Errors

### Pagination Response Format
All list endpoints return paginated data:

```json
{
  "pagination": {
    "count": 25,
    "total_pages": 3,
    "current_page": 1,
    "next": "http://127.0.0.1:8000/api/v1/sessions/?page=2",
    "previous": null
  },
  "results": [
    { "id": 1, "title": "..." },
    ...
  ]
}
```

**Pagination parameters:**
- `?page=1` — page number (default: 1)
- `?page_size=10` — items per page (default: 20, max: 100)

---

## 📋 Common Scenarios & Solutions

### Scenario: "My token keeps expiring"
**Problem:** Access token expires after 60 minutes

**Solution:** Use refresh token to get a new access token:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token_from_login>"}'
```

Refresh tokens last 7 days.

---

### Scenario: "I can't book a session"
**Possible reasons:**
1. ❌ Session is full: Check `is_available` and `spots_remaining`
2. ❌ Already booked: 400 error says "already booked"
3. ❌ Session cancelled: `status` is `cancelled`
4. ❌ Not authenticated: Include `Authorization` header

**Debug:**
```bash
# Get session detail
curl http://127.0.0.1:8000/api/v1/sessions/<id>/

# Check:
# - "is_available": true/false
# - "spots_remaining": number
# - "status": "published" (only this status is bookable)
# - "creator": check creator isn't you (creators book too, but it's unusual)
```

---

### Scenario: "I see my booking but can't cancel it"
**Possible reasons:**
1. ❌ Already cancelled: 400 error says "already cancelled"
2. ❌ Wrong user: Only the booking owner can cancel
3. ❌ Wrong token: Make sure you're using your own token, not someone else's

**Check:**
```bash
curl http://127.0.0.1:8000/api/v1/bookings/<id>/ \
  -H "Authorization: Bearer <your_token>"

# If 403: not your booking
# If 400: booking already cancelled
```

---

## 🧪 Testing Checklist

- [ ] Can login with `username` and `password`
- [ ] Can get profile with valid token
- [ ] 401 error when token missing
- [ ] 403 error when user tries to create session
- [ ] 403 error when user tries to view `/sessions/mine/`
- [ ] Can book a session as user
- [ ] 400 error when booking same session twice
- [ ] Can list bookings with pagination
- [ ] Can cancel own booking
- [ ] Creator can view all bookings on their sessions
- [ ] Can search sessions by title, tag, price
- [ ] Can update profile
- [ ] Can switch roles
- [ ] 404 on invalid session/booking ID
- [ ] Missing required fields return 400 with error list
- [ ] Negative price returns 400 validation error
