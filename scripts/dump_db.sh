#!/bin/sh
set -e

# Usage:
#   ./scripts/dump_db.sh [--compose] [output.json]
# Examples:
#   ./scripts/dump_db.sh               # writes fixtures/current_data.json using local manage.py
#   ./scripts/dump_db.sh output.json   # writes output.json
#   ./scripts/dump_db.sh --compose     # runs inside docker-compose web service

USE_COMPOSE=0
ARG1=${1:-}
ARG2=${2:-}

if [ "$ARG1" = "--compose" ]; then
  USE_COMPOSE=1
  OUT=${ARG2:-fixtures/current_data.json}
else
  OUT=${ARG1:-fixtures/current_data.json}
fi

mkdir -p "$(dirname "$OUT")"

echo "Creating Django fixture -> $OUT"

if [ "$USE_COMPOSE" -eq 1 ]; then
  # Run dumpdata in the web service and capture output to host file
  docker-compose exec web python manage.py dumpdata --natural-primary --natural-foreign --indent 2 > "$OUT"
else
  python manage.py dumpdata --natural-primary --natural-foreign --indent 2 > "$OUT"
fi

echo "Done."
