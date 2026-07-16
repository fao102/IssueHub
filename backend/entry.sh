#!/bin/sh

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting server..."
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 1
