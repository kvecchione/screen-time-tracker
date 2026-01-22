#!/bin/bash

# Screen Time Tracker - Local Database Initialization Script

echo "🚀 Screen Time Tracker - Initializing Local SQLite Database"
echo "============================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Create superuser
echo "👤 Creating superuser account..."
python manage.py create_superuser --username admin --email admin@example.com --password admin 2>/dev/null || echo "⊘ Superuser already exists or creation failed"

# Collect static files
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎉 Quick Start:"
echo "   1. Activate environment: source venv/bin/activate"
echo "   2. Run server: python manage.py runserver"
echo "   3. Visit: http://localhost:8000"
echo "   4. Admin: http://localhost:8000/admin (admin/admin)"
echo ""
