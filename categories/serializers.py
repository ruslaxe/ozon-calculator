from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer для модели Category
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_group', 'fbo_commission', 'fbs_commission']
        read_only_fields = ['id']






