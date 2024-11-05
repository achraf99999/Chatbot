"""
URL configuration for code_generator project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# Assuming your views are defined in a 'views.py' file within 'code_generator'
from django.conf import settings

from django.urls import path , include  
from generator import views  # Import views from your app

urlpatterns = [
    path('generator/', include('generator.urls')),  # Includes the app's URLs
    path('api/download_excel/', views.download_excel_view, name='download_excel'),  # Endpoint for Excel download
    path('api/download_txt/', views.download_txt_view, name='download_txt'),  # Endpoint for text download
    path('api/generate/', views.generate_codes_view, name='generate_code'),  # Endpoint for code generation
    path('', views.index, name='home'),  # Landing page view
]