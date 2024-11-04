from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('book-slot/', views.book_slot_view, name='slot_booking'),
    
    path('notifications/', views.notifications_view, name='notifications'),
    path('success/', views.success_page, name='success_page'),
    path('view-bookings/', views.view_bookings, name='view_bookings'),
]
