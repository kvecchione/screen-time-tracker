# Screen Time Tracker

A Django-based screen time tracking application for children with daily goals that can be tracked on a mobile interface.

## Features

- **Multiple Children Support**: Track screen time for multiple children
- **Daily Goals**: Set specific screen time goals for each child
- **Weekly Tracking**: Goals reset at a baseline amount each Monday
- **Goal Status Tracking**: Mark goals as earned or not earned
- **Mobile-Friendly API**: RESTful API designed for mobile interfaces
- **Weekly Allocations**: Track earned vs. remaining screen time each week
- **Admin Interface**: Manage children, goals, and tracking through Django admin

## Quick Start

### Prerequisites
- Python 3.9+
- pip
- virtualenv (recommended)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd screen-time-tracker
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser account**
```bash
python manage.py create_superuser --username admin --email admin@example.com --password admin
# Or use Django's default prompt:
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## API Endpoints

### Authentication
All API endpoints require authentication via token or session authentication.

### Children
- `GET /api/children/` - List all children
- `POST /api/children/` - Create a new child
- `GET /api/children/{id}/` - Get child details with goals
- `GET /api/children/{id}/daily_summary/` - Get today's tracking summary
- `GET /api/children/{id}/weekly_summary/` - Get current week's summary

### Screen Time Goals
- `GET /api/goals/` - List all goals
- `POST /api/goals/` - Create a new goal (requires `child_id`)
- `GET /api/goals/?child_id={id}` - List goals for a child
- `PATCH /api/goals/{id}/` - Update a goal

### Daily Tracking
- `GET /api/daily-tracking/` - List all daily trackings
- `POST /api/daily-tracking/` - Create new tracking entry
- `GET /api/daily-tracking/?goal_id={id}&date={date}` - Get tracking by goal and date
- `PATCH /api/daily-tracking/{id}/` - Update tracking status and earned minutes
- `POST /api/daily-tracking/bulk_update/` - Bulk update multiple trackings

### Weekly Allocations
- `GET /api/weekly-allocations/` - List all allocations
- `GET /api/weekly-allocations/?goal_id={id}&start_date={date}` - Get allocations for a goal

## Management Commands

### Reset Weekly Allocations
Run every Monday to create new weekly allocations:
```bash
python manage.py reset_weekly_allocations
```

Can be scheduled with a cron job or Celery beat task.

## Data Model

### Child
- `name`: Child's name

### ScreenTimeGoal
- `child`: Reference to Child
- `name`: Goal name (e.g., "Math Practice")
- `description`: Optional goal description
- `target_minutes`: Daily screen time goal in minutes
- `baseline_weekly_minutes`: Weekly baseline allocated each Monday
- `is_active`: Whether this goal is currently active

### DailyTracking
- `goal`: Reference to ScreenTimeGoal
- `date`: Date of tracking
- `status`: pending/earned/not_earned
- `minutes_earned`: Minutes earned if status is "earned"
- `notes`: Optional notes

### WeeklyAllocation
- `goal`: Reference to ScreenTimeGoal
- `start_date`: Monday of the week
- `end_date`: Sunday of the week
- `baseline_minutes`: Starting allocation
- `earned_minutes`: Minutes earned so far
- `remaining_minutes`: Minutes left to earn

## Admin Interface

Access the Django admin at `/admin/` with your superuser credentials to:
- Create and manage children
- Set up screen time goals
- View and manage daily tracking
- Monitor weekly allocations

## Development

### Running Tests
```bash
python manage.py test
```

### Database
The project uses SQLite by default for development. Switch to PostgreSQL in production:

Update `config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'screentime_tracker',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Production Deployment

1. Set `DEBUG = False` in settings
2. Configure `ALLOWED_HOSTS` and `SECRET_KEY`
3. Use PostgreSQL or MySQL instead of SQLite
4. Configure CORS for your frontend domain
5. Use environment variables for sensitive data
6. Run `python manage.py collectstatic` before deployment
7. Use a production WSGI server (Gunicorn, uWSGI)
8. Set up scheduled tasks for weekly resets

## Mobile Frontend Integration

The API is designed for mobile apps. Example requests:

```javascript
// Create a child
POST /api/children/
{
  "name": "Emma"
}

// Create a goal
POST /api/goals/
{
  "child_id": 1,
  "name": "Math Practice",
  "target_minutes": 30,
  "baseline_weekly_minutes": 150
}

// Track today's progress
POST /api/daily-tracking/
{
  "goal": 1,
  "date": "2024-01-21",
  "status": "earned",
  "minutes_earned": 30,
  "notes": "Great work!"
}

// Get today's summary
GET /api/children/1/daily_summary/
```

## License

MIT
