# Smart Football Center

Django web application for managing a football center with teams, bookings, and training sessions.

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

Visit: http://127.0.0.1:8000/
Admin: http://127.0.0.1:8000/admin/

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
- `bookings` - Session bookings and payments
- `training` - Training session management
- `matches` - Match scheduling
- `reservations` - Facility reservations