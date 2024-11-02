from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('add-money/', views.add_money_to_admin_wallet, name='add_money_to_admin_wallet'),
    path('send-money/', views.send_money, name='send_money'),
    path('view-balance/', views.view_balance, name='view_balance'),
    path('withdraw/', views.withdraw_money, name='withdraw_money'),
    path('manager-wallet/', views.manager_wallet, name='manager_wallet'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),  # New URL
    path('transfer_funds_to_customer/', views.transfer_funds_to_customer, name='transfer_funds_to_customer'),
    
]
