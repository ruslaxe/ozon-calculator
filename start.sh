#!/bin/bash
# Скрипт запуска для Render
# Применяет миграции и запускает gunicorn

set -e  # Остановить при ошибке

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting gunicorn..."
exec gunicorn ozon_calculator.wsgi:application --bind 0.0.0.0:$PORT

