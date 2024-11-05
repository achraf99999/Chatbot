from django.urls import path
from . import views

from django.urls import path
from .views import generate_codes_view, index , handle_excel_upload

urlpatterns = [
    path('api/generate/', views.generate_codes_view, name='generate_code'),  # Endpoint for code generation
    path('api/download_excel/', views.download_excel_view, name='download_excel'),  # Endpoint for Excel download
    path('api/download_txt/', views.download_txt_view, name='download_txt'),  # Endpoint for text download
    path('generator/api/upload_excel/', handle_excel_upload, name='upload_excel'),

    path('', views.index, name='index')  # Default view for the app
]
