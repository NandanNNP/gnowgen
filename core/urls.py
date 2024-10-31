# core/urls.py
from django.urls import path
from .views import register, login_view
from.import views



urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    
   
]
