# core/urls.py
from django.urls import path
from .views import register, login_view,index
from.import views
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    path('register/', register, name='register'),
    path('',index , name='home'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:login'), name='logout'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    
   
]
