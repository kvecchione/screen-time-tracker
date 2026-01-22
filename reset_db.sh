#!/bin/bash

# Screen Time Tracker - Database Reset Script
# WARNING: This will delete all data and recreate the database

read -p "⚠️  This will delete all data. Are you sure? (yes/no): " -r
echo ""

if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "🗑️  Removing old database..."
    rm -f db.sqlite3
    
    echo "🗄️  Running migrations..."
    python manage.py migrate
    
    echo "👤 Creating new superuser..."
    python manage.py create_superuser --username admin --email admin@example.com --password admin
    
    echo "✅ Database reset complete!"
else
    echo "❌ Cancelled"
fi
