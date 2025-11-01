from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Category
from .serializers import CategorySerializer


class CategoryPagination(PageNumberPagination):
    """
    Пагинация для списка категорий
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для работы с категориями товаров
    
    Поддерживает:
    - Получение списка категорий
    - Поиск категорий по типу товара (name) и категории (category_group)
    - Получение конкретной категории по ID
    
    Примечание: SQLite не поддерживает регистронезависимый поиск для кириллицы,
    поэтому мы ищем по обоим вариантам (с заглавной и строчной буквы).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'category_group', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """
        Переопределяем queryset для корректного поиска по кириллице в SQLite.
        SQLite не поддерживает регистронезависимый поиск для кириллицы,
        поэтому ищем по всем вариантам регистра.
        """
        queryset = Category.objects.all()
        search_query = self.request.query_params.get('search', None)
        
        if search_query:
            # Генерируем варианты поиска для обхода ограничений SQLite с кириллицей
            search_variants = [
                search_query,  # Оригинал
                search_query.lower(),  # все строчные
                search_query.upper(),  # все заглавные
                search_query.capitalize(),  # Заглавная первая
                search_query.title(),  # Заглавная Каждая
            ]
            
            # Создаем Q-объекты для всех вариантов
            q_objects = Q()
            for variant in search_variants:
                q_objects |= Q(name__icontains=variant)
                q_objects |= Q(category_group__icontains=variant)
            
            queryset = queryset.filter(q_objects).distinct()
        
        return queryset
