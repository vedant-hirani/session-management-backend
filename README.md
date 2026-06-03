# Sessions Marketplace - Backend API

A Django REST Framework API for a marketplace where creators can host live sessions and users can book them.

## Features

- **User Authentication**
  - JWT-based authentication (access + refresh tokens)
  - Username/password registration and login
  - OAuth support (Google, GitHub)
  - Role-based access control (User, Creator)
  - Profile management and role switching

- **Sessions Management**
  - Create, update, delete sessions (Creator only)
  - Public session listing with search and filters
  - Tag-based categorization
  - Price range filtering
  - Session scheduling and status management
  - Automatic spots tracking

- **Bookings**
  - Book sessions (User only)
  - View booking history
  - Cancel bookings
  - Creator dashboard to view bookings on their sessions
  - Prevent double-booking

## Tech Stack

- **Framework:** Django 5.0.6 + Django REST Framework 3.15.2
- **Database:** PostgreSQL (remote-ready, Supabase compatible)
- **Authentication:** JWT (djangorestframework-simplejwt)
- **OAuth:** Google, GitHub (social-auth-app-django)
- **CORS:** django-cors-headers

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/vedant-hirani/session-management-backend.git
cd session-management-backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements/dev.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

**Required variables:**
```
DJANGO_SECRET_KEY=your-secret-key-here
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-db-password
POSTGRES_HOST=db.your-project.supabase.co
POSTGRES_PORT=5432
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/v1/`

## API Documentation

### Authentication Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/auth/register/` | POST | None | Register a new user |
| `/auth/token/` | POST | None | Login (get JWT tokens) |
| `/auth/token/refresh/` | POST | None | Refresh access token |
| `/auth/profile/` | GET/PATCH | Required | View/update profile |
| `/auth/profile/role/` | POST | Required | Switch role (user ↔ creator) |
| `/auth/logout/` | POST | Required | Logout (blacklist token) |
| `/auth/health/` | GET | None | Health check |

### Sessions Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/sessions/` | GET | None | List all published sessions |
| `/sessions/` | POST | Creator | Create a new session |
| `/sessions/{id}/` | GET | None | Get session detail |
| `/sessions/{id}/` | PATCH | Creator | Update session |
| `/sessions/{id}/` | DELETE | Creator | Delete session |
| `/sessions/{id}/cancel/` | POST | Creator | Cancel session |
| `/sessions/mine/` | GET | Creator | Get my sessions |

### Bookings Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/bookings/` | GET | User | Get my bookings |
| `/bookings/` | POST | User | Book a session |
| `/bookings/{id}/` | GET | User | Get booking detail |
| `/bookings/{id}/cancel/` | POST | User | Cancel booking |
| `/bookings/creator/` | GET | Creator | View bookings on my sessions |

## Testing

### Run tests
```bash
pytest
```

### API Testing with Postman

Import the `Sessions_Marketplace.postman_collection.json` file into Postman.

**Test accounts:**
- Creator: `creator1` / `creator123`
- User: `testuser` / `user123`

## Deployment

### Environment Variables for Production

Set these in your hosting platform (Render, Railway, etc.):

```
DJANGO_SETTINGS_MODULE=config.settings.prod
DJANGO_SECRET_KEY=<generate-a-long-random-string>
POSTGRES_HOST=<your-db-host>
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<your-db-password>
POSTGRES_SSLMODE=require
ALLOWED_HOSTS=your-app.onrender.com
FRONTEND_URL=https://your-frontend.vercel.app
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Deployment Commands

```bash
# Install production dependencies
pip install -r requirements/prod.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Project Structure

```
backend/
├── apps/
│   ├── accounts/      # User authentication, profiles
│   ├── sessions/      # Session management
│   ├── bookings/      # Booking management
│   └── common/        # Shared utilities
├── config/
│   ├── settings/
│   │   ├── base.py    # Base settings
│   │   ├── dev.py     # Development settings
│   │   └── prod.py    # Production settings
│   ├── urls.py        # Root URL config
│   └── wsgi.py        # WSGI config
├── core/              # Core utilities (JWT, permissions)
├── requirements/      # Dependencies
├── manage.py
└── README.md
```

## Architecture

- **Service Layer Pattern:** Business logic in `services.py`
- **Selector Layer:** Query logic in `selectors.py`
- **Permissions:** Custom permissions for role-based access
- **Serializers:** Request/response validation
- **Pagination:** Standardized pagination across endpoints

## License

MIT

## Support

For issues or questions, open an issue on GitHub.
