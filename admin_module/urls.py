# admin_module/urls.py

from django.urls import path
from . import views

app_name = 'admin_module'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
]
