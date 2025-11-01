from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'fbo_commission', 'fbs_commission', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at', 'updated_at']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name',)
        }),
        ('Комиссии', {
            'fields': ('fbo_commission', 'fbs_commission')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
