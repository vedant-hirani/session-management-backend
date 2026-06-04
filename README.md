# Sessions Marketplace

A modern, production-grade 1:1 session booking marketplace platform. Sessions Marketplace allows creators (mentors, architects, and developers) to configure and host custom slots, and allows users to search, filter, and book live sessions.

---

## 🏗️ System Architecture

The application is built as a decoupled Client-Server architecture:

1. **Frontend Client**: React Single Page Application (SPA) built with **Vite**, utilizing custom CSS (no external utility frameworks) for performance and complete control, React Router v6 for clean path navigation, and Axios interceptors for JWT token lifecycle and automated refresh.
2. **Backend API**: **Django REST Framework (DRF)** RESTful API, employing the service-layer and selector-layer design patterns to separate business logic and database queries.
3. **Database Layer**: **Postgres** (fully remote-ready, compatible with Supabase and connection pooling).
4. **Gateway**: **Nginx** acting as a unified gateway/reverse proxy on port `80` during containerized deployments.

---

## ⚡ Key Technical Features & Enhancements

* **Secure Authentication**: Fully environment-driven JSON Web Tokens (JWT) using `djangorestframework-simplejwt` (access token lifespan of 60 mins and refresh token lifespan of 7 days). Includes social Google and GitHub OAuth flow integration that resolves session-cookie and browser-isolation challenges (`AuthStateMissing`) by issuing tokens directly on redirect callback.
* **Premium Interactive UI**: Premium dashboard catalog with search logic, asymmetric responsive grids, learn outcomes agenda builders, participant reviews, and a sticky booking sidebar.
* **Mobile-Responsive Optimization**:
  * **Unified Grid Filters**: The session filter bar adapts from a wide flex layout to a balanced `2x2` grid on mobile viewports.
  * **Dynamic Viewport Height**: The sidebar drawer uses dynamic viewport styling (`100dvh`) to prevent address bars from truncating the logout buttons on iOS Safari and mobile Chrome.
  * **Showcase Responsiveness**: Left showcase decorative panels slide out of view (`display: none`) below `768px` to focus user signup immediately.
  * **Role Selector Cards**: Custom, interactive role cards replace generic select dropdowns during registration.

---

## 🛠️ Local Development Setup

### Project Requirements
* **Runtime**: Node.js v18+ and Python v3.10+
* **Package Managers**: `pnpm` (or `npm`) & `pip`
* **Services**: Postgres DB (local instance or Supabase URL)

### 1. Database & Backend Configuration

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements/dev.txt
   ```
4. Copy the environment template and configure environment variables (verify no credentials are hardcoded):
   ```bash
   cp .env.example .env
   ```
5. Apply database migrations:
   ```bash
   python manage.py migrate
   ```
6. Create an administrator account:
   ```bash
   python manage.py createsuperuser
   ```
7. Fire up the API development server:
   ```bash
   python manage.py runserver
   ```
   *The API will run at `http://127.0.0.1:8000/api/v1/`.*

### 2. Frontend Configuration

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install npm dependencies:
   ```bash
   pnpm install  # or npm install
   ```
3. Create a `.env` file to configure the API base url:
   ```bash
   echo "VITE_API_BASE_URL=http://127.0.0.1:8000" > .env
   ```
4. Start the Vite hot-reloaded development server:
   ```bash
   pnpm run dev  # or npm run dev
   ```
   *The client application will run at `http://localhost:5173/`.*

---

## 🐳 Running with Docker Compose (inside `backend` directory)

To spin up the entire application stack (Backend API, React Client, and Local Postgres DB) with Nginx proxying, execute from this `backend` directory:

```bash
docker-compose up --build
```
*After running, open `http://localhost` in your browser. Nginx acts as the reverse-proxy, routing API calls to the Django container and web pages to the Vite container.*

---

## 🔐 Environment Variables Blueprint

All credentials, endpoints, and secrets are fully environment-driven. The following parameters should be populated in production:

### Backend Environments (`backend/.env`)
* `DJANGO_SETTINGS_MODULE`: Set to `config.settings.prod` for secure checks.
* `DJANGO_SECRET_KEY`: Long, random cryptographic key.
* `DATABASE_URL`: Connection string for Postgres (Supabase).
* `POSTGRES_SSLMODE`: Set to `require` for encrypted remote database connections.
* `FRONTEND_URL`: URL of the deployed React application (e.g. `https://app.sessions.com`).
* `CORS_ALLOWED_ORIGINS`: Comma-separated list of origins permitted to request resource sharing.
* `CLOUDINARY_URL`: Cloudinary environment integration URL for profile & session file storage.
* `GOOGLE_OAUTH2_CLIENT_ID` & `GOOGLE_OAUTH2_CLIENT_SECRET`: Credentials for social sign-on.

### Frontend Environments (`frontend/.env`)
* `VITE_API_BASE_URL`: Full base domain of the backend API (e.g. `https://api.sessions.com`).

---

## 📑 API Endpoints Documentation

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

---

## 🧪 Testing

### Run backend tests
From the `backend` directory, run:
```bash
pytest
```

---

## 📁 Project Structure

```
backend/
├── apps/
│   ├── accounts/      # User authentication, profiles, and metadata
│   ├── sessions/      # Session creation, search filters, and slots
│   ├── bookings/      # Booking logs and cancellations
│   └── common/        # Shared pagination and middlewares
├── config/
│   ├── settings/
│   │   ├── base.py    # Common configurations
│   │   ├── dev.py     # Local database settings
│   │   └── prod.py    # Production settings
│   └── urls.py        # Routing roots
├── core/              # Global permissions and OAuth callbacks
├── requirements/      # pip configurations
├── docker-compose.yml # Prod container runner
├── docker-compose.dev.yml # Dev DB-only container runner
├── nginx.conf         # Gateway config
├── manage.py
└── README.md          # Unified project documentation
```

---

## 🏛️ Design Patterns Used

* **Service Layer Pattern**: All business logic (e.g. creating bookings, cancelling sessions) is contained inside standalone `services.py` modules.
* **Selector Layer Pattern**: Database reads and complex filter/sorting queries are isolated in `selectors.py` modules.
* **Middlewares**: Custom request logging and CORS controls.
* **Serializers**: Request/response validation mapping DB models.

---

## 🔑 Social OAuth Setup Guide

To enable Google and GitHub social logins, configure OAuth credentials in the respective developer consoles and update your `.env` variables.

### 1. Google OAuth2 Setup
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to **APIs & Services > Credentials**.
4. Click **Configure Consent Screen**, choose **External**, fill in the application details, and add the scopes `.../auth/userinfo.email` and `.../auth/userinfo.profile`.
5. Under **Credentials**, click **Create Credentials > OAuth client ID**.
6. Select **Web application** as the Application Type.
7. Add **Authorized Javascript Origins**:
   * Development: `http://localhost:3000` (Vite dev server)
8. Add **Authorized Redirect URIs**:
   * Development: `http://127.0.0.1:8000/social/complete/google-oauth2/`
   * Production: `https://<your-backend-domain>/social/complete/google-oauth2/`
9. Save and copy the **Client ID** and **Client Secret** into your `backend/.env` file:
   ```env
   GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
   GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
   ```

### 2. GitHub OAuth Setup
1. Log in to GitHub and go to **Settings > Developer Settings > OAuth Apps**.
2. Click **New OAuth App**.
3. Set **Homepage URL**:
   * Development: `http://localhost:3000`
4. Set **Authorization callback URL**:
   * Development: `http://127.0.0.1:8000/social/complete/github/`
   * Production: `https://<your-backend-domain>/social/complete/github/`
5. Register the application, then generate a new **Client Secret**.
6. Copy both keys into your `backend/.env` file:
   ```env
   GITHUB_CLIENT_ID=your-github-client-id
   GITHUB_CLIENT_SECRET=your-github-client-secret
   ```

---

## 🏁 Example Demo Flow Walkthrough

Follow this workflow to verify the end-to-end lifecycle of the Sessions Marketplace platform:

### Step 1: User & Creator Registrations
1. Open the React frontend client at `http://localhost:3000`.
2. Go to the **Register** page.
3. Register a creator user:
   * Select the **Creator** card.
   * Sign up with username `john_mentor`, email `john@example.com`, and a password.
4. Open an incognito browser window or log out, then register a general attendee user:
   * Select the **User / Attendee** card.
   * Sign up with username `jane_learner`, email `jane@example.com`, and a password.

### Step 2: Create a Session (As Creator)
1. Log in as `john_mentor` (Creator).
2. Go to the **Creator Dashboard** (or click "Create Session").
3. Create a new session slot:
   * **Title**: "1:1 Software Architecture & Scalability Deep-Dive"
   * **Description**: "A personalized session focusing on Docker, system design patterns, and Django backend scalability."
   * **Category**: "Software Engineering"
   * **Price**: `$150`
   * **Time Slot**: Select an upcoming date/time.
4. Save to publish the session. It is now live in the global catalog.

### Step 3: Browse and Book (As Attendee)
1. Log in as `jane_learner` (User / Attendee) in your second browser window.
2. Go to the **Explore Catalog** page.
3. Search for "Architecture" or filter by the "Software Engineering" category.
4. Locate John's session and click **View Details**.
5. Select the configured slot from the booking sidebar and click **Book Session**.
6. Once completed, check the **My Bookings** page to see the active status and details.

### Step 4: Manage Bookings (As Creator)
1. Switch back to the `john_mentor` session window.
2. Navigate to **Creator Bookings** (My Sessions).
3. Observe Jane's active booking listed under your session.
4. (Optional) Test booking/session cancellation behavior using the **Cancel Session** or **Cancel Booking** actions.

