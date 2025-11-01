"""
Management команда для загрузки категорий товаров Ozon.

Использование:
    python manage.py load_categories

Попытается загрузить из Excel файла, если доступен.
Иначе создаст несколько тестовых категорий для работы.
"""

from django.core.management.base import BaseCommand
from categories.models import Category
import os
from pathlib import Path
from django.conf import settings


class Command(BaseCommand):
    help = 'Загружает категории товаров Ozon в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--excel-file',
            type=str,
            help='Путь к Excel файлу с категориями (опционально)',
            default=None
        )
        parser.add_argument(
            '--test-only',
            action='store_true',
            help='Создать только тестовые категории (без импорта из Excel)',
            default=False
        )

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        test_only = options['test_only']

        # Проверяем, есть ли уже категории
        existing_count = Category.objects.count()
        if existing_count > 0 and not test_only:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  В базе уже есть {existing_count} категорий. '
                    'Будут обновлены существующие и добавлены новые.'
                )
            )

        # Пытаемся загрузить из Excel, если файл указан или найден
        if not test_only:
            # Ищем Excel файлы в проекте
            base_dir = Path(settings.BASE_DIR)
            excel_files = [
                base_dir / 'docs' / 'Таблица_категорий_для_расчёта_вознаграждения_10112025_1761297339.xlsx',
                base_dir / 'docs' / 'table 1.xlsx',
            ]
            
            if excel_file:
                excel_files.insert(0, Path(excel_file))

            for file_path in excel_files:
                if file_path.exists():
                    self.stdout.write(self.style.SUCCESS(f'📁 Найден Excel файл: {file_path}'))
                    try:
                        # Используем существующую команду импорта
                        from django.core.management import call_command
                        self.stdout.write('📥 Загружаю категории из Excel файла...')
                        self.stdout.write('⏳ Это может занять несколько минут (15,000+ категорий)...')
                        
                        # Вызываем команду импорта
                        call_command(
                            'import_ozon_categories',
                            str(file_path),
                            clear=False,  # Не очищать существующие категории
                            update=True   # Обновлять существующие
                        )
                        
                        total_count = Category.objects.count()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'\n✅ Категории успешно загружены!\n'
                                f'📊 Всего категорий в базе: {total_count}'
                            )
                        )
                        return
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'\n❌ Ошибка при загрузке из Excel: {e}')
                        )
                        import traceback
                        self.stdout.write(traceback.format_exc())
                        self.stdout.write(self.style.WARNING('\n⚠️  Продолжаю с тестовыми категориями...'))
                        break
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Файл не найден: {file_path}')
                    )

        # Если не удалось загрузить из Excel - создаем тестовые категории
        self.stdout.write('Создаю тестовые категории...')
        
        test_categories = [
            {"name": "Шарф", "fbo_commission": 14.0, "fbs_commission": 12.0, "category_group": "Аксессуары"},
            {"name": "3D-очки", "fbo_commission": 15.0, "fbs_commission": 13.0, "category_group": "VR-устройства и аксессуары"},
            {"name": "Футболка", "fbo_commission": 15.0, "fbs_commission": 12.0, "category_group": "Одежда"},
            {"name": "Книга", "fbo_commission": 10.0, "fbs_commission": 8.0, "category_group": "Книги"},
            {"name": "Наушники", "fbo_commission": 18.0, "fbs_commission": 15.0, "category_group": "Электроника"},
            {"name": "Смартфон", "fbo_commission": 20.0, "fbs_commission": 17.0, "category_group": "Электроника"},
            {"name": "Ноутбук", "fbo_commission": 12.0, "fbs_commission": 10.0, "category_group": "Электроника"},
            {"name": "Кроссовки", "fbo_commission": 16.0, "fbs_commission": 13.0, "category_group": "Обувь"},
            {"name": "Часы", "fbo_commission": 17.0, "fbs_commission": 14.0, "category_group": "Аксессуары"},
            {"name": "Рюкзак", "fbo_commission": 15.0, "fbs_commission": 12.0, "category_group": "Сумки и чемоданы"},
        ]

        created_count = 0
        for cat_data in test_categories:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                category_group=cat_data.get("category_group"),
                defaults={
                    "fbo_commission": cat_data["fbo_commission"],
                    "fbs_commission": cat_data["fbs_commission"],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✅ Создана: {category.name}')

        total_count = Category.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Готово! Создано новых категорий: {created_count}. '
                f'Всего в базе: {total_count}'
            )
        )

