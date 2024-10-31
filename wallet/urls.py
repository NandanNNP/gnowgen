from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('add-money/', views.add_money_to_admin_wallet, name='add_money_to_admin_wallet'),
    path('send-money/', views.send_money, name='send_money'),
    path('view-balance/', views.view_balance, name='view_balance'),
    path('withdraw/', views.withdraw_money, name='withdraw_money'),
]
