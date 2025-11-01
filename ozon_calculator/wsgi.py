"""
WSGI config for ozon_calculator project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ozon_calculator.settings')

application = get_wsgi_application()

# Автоматическая загрузка категорий при первом запуске
try:
    from ozon_calculator.startup import load_categories_if_empty
    load_categories_if_empty()
except Exception as e:
    # Игнорируем ошибки при старте (например, если база еще не готова)
    pass
