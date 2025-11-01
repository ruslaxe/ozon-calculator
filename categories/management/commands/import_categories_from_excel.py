"""
Management команда для импорта категорий из Excel файла.

Использование:
    python manage.py import_categories_from_excel path/to/file.xlsx

Формат Excel файла:
    - Первая строка (заголовок) пропускается
    - Колонка A: Название категории
    - Колонка B: Комиссия FBO (%)
    - Колонка C: Комиссия FBS (%)
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from categories.models import Category
import openpyxl
import os
from decimal import Decimal, InvalidOperation


class Command(BaseCommand):
    help = 'Импортирует категории товаров из Excel файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            type=str,
            help='Путь к Excel файлу с категориями'
        )
        parser.add_argument(
            '--skip-header',
            action='store_true',
            help='Пропустить первую строку (заголовок)',
            default=True
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Обновить существующие категории вместо пропуска',
            default=False
        )

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        skip_header = options['skip_header']
        update = options['update']

        # Проверка существования файла
        if not os.path.exists(excel_file):
            raise CommandError(f'Файл не найден: {excel_file}')

        # Открытие Excel файла
        try:
            workbook = openpyxl.load_workbook(excel_file, data_only=True)
        except Exception as e:
            raise CommandError(f'Ошибка при открытии файла: {str(e)}')

        # Получение активного листа
        worksheet = workbook.active

        # Подсчет строк
        total_rows = worksheet.max_row
        start_row = 2 if skip_header else 1

        if total_rows < start_row:
            raise CommandError('Файл не содержит данных для импорта')

        self.stdout.write(f'Начинаю импорт из файла: {excel_file}')
        self.stdout.write(f'Найдено строк для обработки: {total_rows - start_row + 1}')

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        # Импорт данных
        with transaction.atomic():
            for row_num in range(start_row, total_rows + 1):
                row = worksheet[row_num]
                
                # Извлечение данных из ячеек
                name_cell = row[0].value if len(row) > 0 else None
                fbo_cell = row[1].value if len(row) > 1 else None
                fbs_cell = row[2].value if len(row) > 2 else None

                # Пропуск пустых строк
                if not name_cell:
                    skipped_count += 1
                    continue

                # Преобразование названия в строку
                name = str(name_cell).strip()
                if not name:
                    skipped_count += 1
                    continue

                # Преобразование комиссий
                try:
                    # Пробуем преобразовать в Decimal
                    if isinstance(fbo_cell, (int, float)):
                        fbo_commission = Decimal(str(fbo_cell))
                    elif fbo_cell:
                        fbo_commission = Decimal(str(fbo_cell).replace(',', '.'))
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Строка {row_num}: отсутствует комиссия FBO для "{name}"'
                            )
                        )
                        error_count += 1
                        continue

                    if isinstance(fbs_cell, (int, float)):
                        fbs_commission = Decimal(str(fbs_cell))
                    elif fbs_cell:
                        fbs_commission = Decimal(str(fbs_cell).replace(',', '.'))
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Строка {row_num}: отсутствует комиссия FBS для "{name}"'
                            )
                        )
                        error_count += 1
                        continue

                    # Валидация значений комиссий
                    if fbo_commission < 0 or fbo_commission > 100:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Строка {row_num}: некорректная комиссия FBO ({fbo_commission}%) для "{name}"'
                            )
                        )
                        error_count += 1
                        continue

                    if fbs_commission < 0 or fbs_commission > 100:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Строка {row_num}: некорректная комиссия FBS ({fbs_commission}%) для "{name}"'
                            )
                        )
                        error_count += 1
                        continue

                except (InvalidOperation, ValueError) as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Строка {row_num}: ошибка преобразования комиссий для "{name}": {str(e)}'
                        )
                    )
                    error_count += 1
                    continue

                # Создание или обновление категории
                try:
                    category, created = Category.objects.update_or_create(
                        name=name,
                        defaults={
                            'fbo_commission': fbo_commission,
                            'fbs_commission': fbs_commission,
                        }
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Создана: {name} (FBO: {fbo_commission}%, FBS: {fbs_commission}%)'
                            )
                        )
                    elif update:
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'↻ Обновлена: {name} (FBO: {fbo_commission}%, FBS: {fbs_commission}%)'
                            )
                        )
                    else:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'⊘ Пропущена (существует): {name}'
                            )
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Строка {row_num}: ошибка при создании категории "{name}": {str(e)}'
                        )
                    )
                    error_count += 1
                    continue

        # Итоговая статистика
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('Импорт завершен!'))
        self.stdout.write(f'  Создано: {created_count}')
        if update:
            self.stdout.write(f'  Обновлено: {updated_count}')
        self.stdout.write(f'  Пропущено: {skipped_count}')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'  Ошибок: {error_count}'))
        self.stdout.write('=' * 60)








