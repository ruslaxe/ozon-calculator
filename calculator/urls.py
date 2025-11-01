from django.urls import path
from .views import CalculateAPIView, CalculateExportAPIView

urlpatterns = [
    path('calculate/', CalculateAPIView.as_view(), name='calculate'),
    path('calculate/export/', CalculateExportAPIView.as_view(), name='calculate-export'),
]

