#!/bin/sh
set -e

# Usage:
#   ./scripts/load_db.sh [path/to/fixture.json]
#   ./scripts/load_db.sh --compose [path/in/repo]
# Defaults to ./current_data.json

FILE=${2:-${1:-current_data.json}}
USE_COMPOSE=0
if [ "${1}" = "--compose" ]; then
  USE_COMPOSE=1
  FILE=${2:-current_data.json}
fi

if [ ! -f "$FILE" ]; then
  echo "Fixture file not found: $FILE"
  exit 1
fi

if [ "$USE_COMPOSE" -eq 1 ]; then
  echo "Loading $FILE into Django via docker-compose (web service)"
  docker-compose exec web python manage.py loaddata "/app/$(basename "$FILE")"
else
  echo "Loading $FILE into local Django environment"
  python manage.py loaddata "$FILE"
fi

echo "Done."
