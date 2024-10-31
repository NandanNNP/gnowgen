from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Wallet, WalletTransaction, CustomUser
from django.db.models import Q
from decimal import Decimal

@login_required
def add_money_to_admin_wallet(request):
    if request.method == 'POST' and request.user.user_type == 4:  # Ensure user is Admin
        amount = Decimal(request.POST.get('amount'))
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += amount
        wallet.save()
        messages.success(request, f"Successfully added {amount} to your wallet.")
        return redirect('wallet:view_balance')
    return render(request, 'wallet/add_money_to_admin_wallet.html')

@login_required
def send_money(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        amount = Decimal(request.POST.get('amount'))
        sender_wallet, _ = Wallet.objects.get_or_create(user=request.user)
        
        try:
            receiver = CustomUser.objects.get(id=receiver_id)
            receiver_wallet, _ = Wallet.objects.get_or_create(user=receiver)
            
            # Check if sufficient balance
            if sender_wallet.balance >= amount:
                sender_wallet.balance -= amount
                receiver_wallet.balance += amount
                sender_wallet.save()
                receiver_wallet.save()
                
                transaction_type = determine_transaction_type(request.user, receiver)
                WalletTransaction.objects.create(sender=request.user, receiver=receiver, amount=amount, transaction_type=transaction_type)
                messages.success(request, f"Sent {amount} to {receiver.username}.")
            else:
                messages.error(request, "Insufficient balance.")
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid receiver.")
            
    users = CustomUser.objects.filter(
        Q(user_type=3) if request.user.user_type == 4 else Q(user_type=1)
    )  # Admin can send to Managers, Manager to Customers
    
    return render(request, 'wallet/send_money.html', {'users': users})

@login_required
def view_balance(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    return render(request, 'wallet/view_balance.html', {'wallet': wallet})

@login_required
def withdraw_money(request):
    if request.method == 'POST' and request.user.user_type == 1:  # Ensure user is Customer
        amount = Decimal(request.POST.get('amount'))
        wallet = Wallet.objects.get(user=request.user)
        
        if wallet.balance >= amount:
            wallet.balance -= amount
            wallet.save()
            # Add logic for bank transfer integration here
            WalletTransaction.objects.create(sender=request.user, receiver=None, amount=amount, transaction_type='withdrawal')
            messages.success(request, f"Successfully withdrew {amount} to your bank account.")
        else:
            messages.error(request, "Insufficient balance.")
            
    return redirect('wallet:view_balance')

def determine_transaction_type(sender, receiver):
    if sender.user_type == 4 and receiver.user_type == 4:
        return 'admin_to_admin'
    elif sender.user_type == 4 and receiver.user_type == 3:
        return 'admin_to_manager'
    elif sender.user_type == 3 and receiver.user_type == 1:
        return 'manager_to_customer'
    return 'unknown'
