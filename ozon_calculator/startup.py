"""
Автоматическая загрузка категорий при старте приложения (для Render)
Выполняется только если категорий в базе нет.
"""

import os
from pathlib import Path
from django.core.management import call_command


def load_categories_if_empty():
    """
    Автоматически загружает категории при старте приложения,
    если база данных пустая.
    """
    # Проверяем, что мы не в режиме миграций
    if os.environ.get('DJANGO_MIGRATE', '').lower() == 'true':
        return
    
    try:
        from categories.models import Category
        
        # Проверяем количество категорий
        count = Category.objects.count()
        
        if count == 0:
            print("📦 База данных пустая. Загружаю категории...")
            
            # Ищем Excel файл
            from django.conf import settings
            base_dir = Path(settings.BASE_DIR)
            excel_file = base_dir / 'docs' / 'Таблица_категорий_для_расчёта_вознаграждения_10112025_1761297339.xlsx'
            
            if excel_file.exists():
                print(f"📁 Найден Excel файл: {excel_file}")
                print("📥 Загружаю категории из Excel файла...")
                print("⏳ Это может занять несколько минут (15,000+ категорий)...")
                
                try:
                    # Используем команду load_categories вместо прямой импорт
                    call_command('load_categories', test_only=False)
                    
                    final_count = Category.objects.count()
                    print(f"✅ Категории успешно загружены! Всего: {final_count}")
                except Exception as e:
                    print(f"❌ Ошибка при загрузке из Excel: {e}")
                    import traceback
                    print(traceback.format_exc())
                    print("⚠️  Приложение запустится без категорий.")
            else:
                print(f"⚠️  Excel файл не найден: {excel_file}")
                print("📝 Создаю тестовые категории...")
                
                # Создаем тестовые категории
                test_categories = [
                    {"name": "Шарф", "fbo_commission": 14.0, "fbs_commission": 12.0, "category_group": "Аксессуары"},
                    {"name": "3D-очки", "fbo_commission": 15.0, "fbs_commission": 13.0, "category_group": "VR-устройства и аксессуары"},
                    {"name": "Футболка", "fbo_commission": 15.0, "fbs_commission": 12.0, "category_group": "Одежда"},
                    {"name": "Книга", "fbo_commission": 10.0, "fbs_commission": 8.0, "category_group": "Книги"},
                    {"name": "Наушники", "fbo_commission": 18.0, "fbs_commission": 15.0, "category_group": "Электроника"},
                ]
                
                for cat_data in test_categories:
                    Category.objects.get_or_create(
                        name=cat_data["name"],
                        category_group=cat_data.get("category_group"),
                        defaults={
                            "fbo_commission": cat_data["fbo_commission"],
                            "fbs_commission": cat_data["fbs_commission"],
                        }
                    )
                
                print(f"✅ Создано тестовых категорий: {Category.objects.count()}")
        else:
            print(f"✅ Категории уже загружены ({count} шт.)")
    except Exception as e:
        # Игнорируем ошибки при старте (например, если база еще не готова)
        print(f"⚠️  Не удалось проверить категории: {e}")

