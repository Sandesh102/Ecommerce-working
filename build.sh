#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running migrations..."
python manage.py migrate --verbosity 2

echo "==> Loading database fixtures..."
python manage.py loaddata data.json || echo "Warning: Failed to load fixtures (this may be okay if data already exists)"

echo "==> Creating superuser..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='sasa').exists():
    User.objects.create_superuser('sasa', 'sandeshsubedi103@gmail.com', 'Abcde12345*#')
    print("✅ Superuser created successfully")
else:
    print("ℹ️  Superuser already exists")
EOF

echo "==> Build completed successfully!"
