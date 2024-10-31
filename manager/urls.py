from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [
    path('dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('create-employee/', views.create_employee, name='create_employee'),
    path('verify-employee-list/', views.employee_list, name='verify_employee_list'),
    path('verify-employee/<int:employee_id>/', views.verify_employee, name='verify_employee'),
    
    path('employee-list/', views.employee_list, name='employee_list'),
    path('verified-employee-list/', views.view_verified_employees, name='verified_employee_list'),
    path('manage-employees/', views.manage_employees, name='manage_employees'), 
    path('notifications/', views.manager_notifications, name='manager_notifications'),
    path('send-notification/', views.send_notification_to_employee, name='send_notification_to_employee'),
]
