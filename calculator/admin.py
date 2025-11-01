from django.contrib import admin
from .models import Calculation


@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'price', 'volume', 'monthly_sales', 'created_at']
    search_fields = ['category__name']
    list_filter = ['category', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Категория', {
            'fields': ('category',)
        }),
        ('Параметры товара', {
            'fields': ('price', 'weight', 'volume', 'length', 'width', 'height')
        }),
        ('Параметры расчета', {
            'fields': ('tax_rate', 'buyout_rate', 'delivery_time', 'ad_costs_rate')
        }),
        ('Затраты', {
            'fields': ('cost_price', 'other_costs', 'monthly_sales')
        }),
        ('Результаты', {
            'fields': ('calculation_results',)
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
