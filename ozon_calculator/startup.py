"""
Автоматическая загрузка категорий при старте приложения (для Render)
Выполняется только если категорий в базе нет.
"""

import os
from pathlib import Path
from unicodedata import normalize
from django.core.management import call_command


def load_categories_if_empty():
    """
    Автоматически загружает категории при старте приложения,
    если база данных пустая.
    """
    # Проверяем, что мы не в режиме миграций
    if os.environ.get('DJANGO_MIGRATE', '').lower() == 'true':
        return

    if os.environ.get('SKIP_CATEGORY_AUTOLOAD', '').lower() in {'1', 'true', 'yes'}:
        print("⏭️  Пропускаю автозагрузку категорий (SKIP_CATEGORY_AUTOLOAD).")
        return
    
    try:
        from categories.models import Category

        # Проверяем количество категорий
        count = Category.objects.count()

        if count == 0:
            print("📦 База данных пустая. Загружаю категории...")

            from django.conf import settings

            def _resolve_excel_file(base_dir: Path) -> Path | None:
                docs_dir = base_dir / 'docs'
                default_name = 'Таблица_категорий_для_расчёта_вознаграждения_10112025_1761297339.xlsx'
                name_variants = [
                    default_name,
                    normalize('NFC', default_name),
                    normalize('NFD', default_name),
                ]

                seen = set()
                for name in name_variants:
                    candidate = docs_dir / name
                    key = str(candidate)
                    if key in seen:
                        continue
                    seen.add(key)
                    if candidate.exists():
                        return candidate

                # Ищем любые excel-файлы с подходящим именем
                patterns = [
                    'Таблица*вознаграждения*.xlsx',
                    'table 1.xlsx',
                ]
                for pattern in patterns:
                    for candidate in docs_dir.glob(pattern):
                        key = str(candidate)
                        if key in seen:
                            continue
                        seen.add(key)
                        if candidate.exists():
                            return candidate
                return None

            base_dir = Path(settings.BASE_DIR)
            excel_file = _resolve_excel_file(base_dir)

            if excel_file:
                print(f"📁 Найден Excel файл: {excel_file}")
                print("📥 Загружаю категории из Excel файла...")
                print("⏳ Это может занять несколько минут (15,000+ категорий)...")

                try:
                    # Используем команду load_categories вместо прямой импорт
                    call_command('load_categories', test_only=False)

                    final_count = Category.objects.count()
                    print(f"✅ Категории успешно загружены! Всего: {final_count}")
                    if final_count == 0:
                        raise RuntimeError('Импорт завершился без ошибок, но категории не созданы')
                except Exception as e:
                    print(f"❌ Ошибка при загрузке из Excel: {e}")
                    import traceback
                    print(traceback.format_exc())
                    print("⚠️  Перехожу на тестовые категории.")
                    _create_test_categories(Category)
            else:
                print("⚠️  Excel файл с категориями не найден.")
                print("📝 Создаю тестовые категории...")
                _create_test_categories(Category)
        else:
            print(f"✅ Категории уже загружены ({count} шт.)")
    except Exception as e:
        # Игнорируем ошибки при старте (например, если база еще не готова)
        print(f"⚠️  Не удалось проверить категории: {e}")


def _create_test_categories(Category):
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

