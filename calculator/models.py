from django.db import models
from categories.models import Category


class Calculation(models.Model):
    """
    Модель для сохранения истории расчетов юнит-экономики
    """
    # Связь с категорией
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория товара'
    )
    
    # Основные параметры товара
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена товара (руб.)'
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name='Вес товара (кг)'
    )
    volume = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name='Объем товара (л)'
    )
    
    # Габариты (опционально)
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Длина (см)'
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Ширина (см)'
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Высота (см)'
    )
    
    # Параметры для расчета
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Налог на прибыль (%)'
    )
    buyout_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Выкуп (%)'
    )
    delivery_time = models.IntegerField(
        verbose_name='Время доставки (часы)'
    )
    ad_costs_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Доля рекламных расходов (%)'
    )
    
    # Затраты
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Себестоимость за 1 шт (руб.)'
    )
    other_costs = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Прочие затраты на 1 шт (руб.)'
    )
    monthly_sales = models.IntegerField(
        verbose_name='Количество продаж в месяц (шт)'
    )
    
    # Результаты расчета (JSON)
    calculation_results = models.JSONField(
        verbose_name='Результаты расчета',
        help_text='Результаты расчета для FBO и FBS в формате JSON'
    )
    
    # Метаданные
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Расчет'
        verbose_name_plural = 'Расчеты'
        ordering = ['-created_at']

    def __str__(self):
        return f"Расчет #{self.id} - {self.category.name} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"
