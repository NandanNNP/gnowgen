# employee/urls.py
from django.urls import path
from . import views

app_name = 'employee'

urlpatterns = [
    path('dashboard/', views.employee_dashboard, name='employee_dashboard'),  # Employee dashboard route
    path('create_user/', views.create_user, name='create_user'),
    
    path('verify_user/<int:user_id>/', views.verify_user, name='verify_user'),
    path('view_address/<int:user_id>/', views.view_address, name='view_address'),



    path('verify_user_list/', views.verify_user_list, name='verify_user_list'),
    path('view_schedule/', views.view_schedule, name='view_schedule'),
    path('notification_manager/', views.notification_manager, name='notification_manager'),#mamange notifaction between emp and cust
    path('send-notification/', views.send_notification_to_manager, name='send_notification_to_manager'),#snd notification to manger
    path('view-manager-notifications/', views.view_manager_notifications, name='view_manager_notifications'),

    
    path('collection_management/', views.collection_management, name='collection_management'),  # Add this line
    path('verified_users/', views.verified_user_list, name='verified_user_list'),
]
