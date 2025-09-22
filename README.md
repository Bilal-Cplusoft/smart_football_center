# Smart Football Center

Django REST API application for managing a football center with teams, bookings, training sessions, and user management.

## Features

- **User Management**: Custom user roles (admin, coach, player, parent, child)
- **Team Management**: Create teams, assign coaches, manage players
- **Session Booking**: Book training sessions, manage capacity and pricing
- **Memberships & Bundles**: Flexible payment options
- **REST API**: Full API with authentication and documentation
- **Admin Interface**: Django admin for backend management

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Admin User
```bash
python manage.py createsuperuser
```

### 4. Run Server
```bash
python manage.py runserver
```

### 5. Setup Test Data (Optional)
```bash
python setup_test_data.py
```

Visit: http://127.0.0.1:8000/api/ (API Root)
Admin: http://127.0.0.1:8000/admin/
API Docs: http://127.0.0.1:8000/api/docs/ (Swagger UI)

## API Endpoints

### Authentication
```bash
# Register new user
POST /api/auth/register/
{
  "username": "player1",
  "email": "player@example.com",
  "password": "secure123",
  "password_confirm": "secure123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "player"
}

# Login
POST /api/auth/login/
{
  "username": "player1",
  "password": "secure123"
}

# Logout
POST /api/auth/logout/
```

### Core Resources
```bash
# Users
GET    /api/users/          # List users
POST   /api/users/          # Create user
GET    /api/users/{id}/     # Get user details
PUT    /api/users/{id}/     # Update user
DELETE /api/users/{id}/     # Delete user
GET    /api/users/me/       # Get current user profile

# Teams
GET    /api/teams/          # List teams
POST   /api/teams/          # Create team
GET    /api/teams/{id}/     # Get team details
PUT    /api/teams/{id}/     # Update team
DELETE /api/teams/{id}/     # Delete team
POST   /api/teams/{id}/add_players/    # Add players to team
POST   /api/teams/{id}/remove_players/ # Remove players from team

# Sessions
GET    /api/sessions/       # List sessions
POST   /api/sessions/       # Create session
GET    /api/sessions/{id}/  # Get session details
PUT    /api/sessions/{id}/  # Update session
DELETE /api/sessions/{id}/  # Delete session
GET    /api/sessions/upcoming/     # Get upcoming sessions
GET    /api/sessions/available/    # Get available sessions

# Bookings
GET    /api/bookings/       # List bookings
POST   /api/bookings/       # Create booking
GET    /api/bookings/{id}/  # Get booking details
DELETE /api/bookings/{id}/  # Cancel booking
POST   /api/bookings/book_session/ # Book session for current user
GET    /api/bookings/my_bookings/  # Get current user's bookings

# Memberships & Bundles
GET    /api/memberships/    # List memberships
POST   /api/memberships/    # Create membership
GET    /api/bundles/        # List bundles
POST   /api/bundles/        # Create bundle

# Discounts (Admin only)
GET    /api/discounts/      # List discounts
POST   /api/discounts/      # Create discount
POST   /api/discounts/apply/ # Apply discount code
```

### API Usage Examples

```bash
# Create a team (requires authentication)
curl -X POST http://127.0.0.1:8000/api/teams/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Arsenal FC",
    "coach_id": 2
  }'

# Book a session
curl -X POST http://127.0.0.1:8000/api/bookings/book_session/ \
  -H "Content-Type: application/json" \
  -d '{
    "session": 1
  }'

# Get my profile
curl http://127.0.0.1:8000/api/users/me/
```

## API Documentation

- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **ReDoc**: http://127.0.0.1:8000/api/redoc/
- **OpenAPI Schema**: http://127.0.0.1:8000/api/schema/

## Database Configuration

**PostgreSQL (Production):**
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smart_football',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**SQLite (Development - Current):**
Uses `db.sqlite3` file (no setup required)

## Making Migrations

When you modify models:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Apps Structure

- `accounts` - User management (admin, coach, player, parent, child roles)
- `teams` - Team and player management
- `bookings` - Session bookings, memberships, bundles, and discounts
- `training` - Training session management
- `matches` - Match scheduling
- `reservations` - Facility reservations

## Testing the API

### Automated Testing
Run the included test script:
```bash
python test_api.py
```

### Setup Test Data
Create sample users, teams, sessions, and bookings:
```bash
python setup_test_data.py
```

**Default Test Users:**
- Admin: `admin` / `password123`
- Coach: `coach_john` / `password123`
- Player: `player1` / `password123`

### Manual Testing
```bash
# Test API root
curl http://127.0.0.1:8000/api/

# Register a user
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123","password_confirm":"test123","role":"player","first_name":"Test","last_name":"User"}'

# Login with test user
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"player1","password":"password123"}'

# Get teams (authenticated)
curl -b cookies.txt http://127.0.0.1:8000/api/teams/
```

## Tech Stack

- **Django 4.2**: Web framework
- **Django REST Framework**: API framework
- **SQLite/PostgreSQL**: Database
- **drf-spectacular**: API documentation
- **django-cors-headers**: CORS support
- **django-filter**: Advanced filtering

## API Features

- **Authentication**: Session-based authentication with login/logout
- **Permissions**: Role-based access control (admin, coach, player, parent, child)
- **Pagination**: Automatic pagination for list endpoints
- **Filtering**: Advanced filtering and search capabilities
- **Documentation**: Auto-generated API documentation with Swagger UI
- **CORS**: Configured for frontend integration
- **Validation**: Comprehensive input validation and error handling
