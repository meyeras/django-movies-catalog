#!/bin/bash

set -e  # Exit on any error

echo "Applying database migrations..."
python manage.py migrate --noinput

# Check if CREATE_SUPERUSER is set to "true"
if [ "$CREATE_SUPERUSER" = "true" ]; then
  echo "CREATE_SUPERUSER is set to true. Attempting to create superuser..."

  # Check for required superuser environment variables
  if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Superuser environment variables are set. Creating superuser..."
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created successfully.')
else:
    print('Superuser already exists.')
EOF
  else
    echo "Missing one or more superuser environment variables:"
    if [ -z "$DJANGO_SUPERUSER_USERNAME" ]; then echo "- DJANGO_SUPERUSER_USERNAME is not set"; fi
    if [ -z "$DJANGO_SUPERUSER_EMAIL" ]; then echo "- DJANGO_SUPERUSER_EMAIL is not set"; fi
    if [ -z "$DJANGO_SUPERUSER_PASSWORD" ]; then echo "- DJANGO_SUPERUSER_PASSWORD is not set"; fi
    echo "Skipping superuser creation."
  fi
fi

echo "Populate database with movies"
python manage.py populate_db movies_sample.json

echo "Starting Django application..."
exec "$@"
