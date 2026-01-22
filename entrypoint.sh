#!/bin/sh
set -e

# Run database migrations
python manage.py migrate --noinput

# Optionally create a superuser 
if [ "${CREATE_SUPERUSER:-false}" = "true" ]; then
  python manage.py create_superuser \
    --username "${DJANGO_SUPERUSER_USERNAME:-admin}" \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" \
    --password "${DJANGO_SUPERUSER_PASSWORD:-admin}" || true
fi

# Hand off to the app server
gunicorn --bind 0.0.0.0:8000 --workers "${WORKERS:-4}" config.wsgi:application
