from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Wallet, WalletTransaction, CustomUser,Notification,SlotBooking
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
            # Here you could add logic for actual bank transfer integration if needed.
            WalletTransaction.objects.create(sender=request.user, receiver=None, amount=amount, transaction_type='withdrawal')
            messages.success(request, f"Successfully withdrew {amount} to your bank account.")
        else:
            messages.error(request, "Insufficient balance.")
            
    # Retrieve the wallet and transactions for display
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = WalletTransaction.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, 'wallet/withdraw_money.html', {'wallet': wallet, 'transactions': transactions})

def determine_transaction_type(sender, receiver):
    if sender.user_type == 4 and receiver.user_type == 4:
        return 'admin_to_admin'
    elif sender.user_type == 4 and receiver.user_type == 3:
        return 'admin_to_manager'
    elif sender.user_type == 3 and receiver.user_type == 1:
        return 'manager_to_customer'
    return 'unknown'

from django.shortcuts import render, get_object_or_404

from core.models import Wallet, WalletTransaction



@login_required
def manager_wallet(request):
    # Get or create the wallet for the logged-in manager
    wallet, created = Wallet.objects.get_or_create(user=request.user, defaults={'balance': 0.0})
    # Fetch recent transactions for the manager
    transactions = WalletTransaction.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'wallet/manager_wallet.html', {'wallet': wallet, 'transactions': transactions})



@login_required
def transaction_history(request):
    # Fetch all transactions for the logged-in user
    transactions = WalletTransaction.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-created_at')
    return render(request, 'wallet/transaction_history.html', {'transactions': transactions})

@login_required
def transfer_funds_to_customer(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        amount = Decimal(request.POST.get('amount'))
        manager_wallet, _ = Wallet.objects.get_or_create(user=request.user)

        try:
            receiver = CustomUser.objects.get(id=receiver_id, user_type=1)  # Ensure the receiver is a customer
            receiver_wallet, _ = Wallet.objects.get_or_create(user=receiver)

            # Check if sufficient balance
            if manager_wallet.balance >= amount:
                manager_wallet.balance -= amount
                receiver_wallet.balance += amount
                manager_wallet.save()
                receiver_wallet.save()

                transaction_type = 'manager_to_customer'  # Define the transaction type
                WalletTransaction.objects.create(sender=request.user, receiver=receiver, amount=amount, transaction_type=transaction_type)

                messages.success(request, f"Successfully transferred {amount} to {receiver.username}'s wallet.")


                # Assuming 'amount' is already defined and you're checking notifications for the manager with ID 5
                Notification.objects.filter(user_id=5, is_fund_transfer=True, amount=amount).update(is_fund_transfer=False)

                from datetime import date

                # Get today's date or the specific date for the booking
                today = date.today()

                # Update the is_confirmed field for bookings on the same date NOOOOOOTE IT
                SlotBooking.objects.filter(customer=receiver, date=today, is_confirmed=False).update(is_confirmed=True)



            else:
                messages.error(request, "Insufficient balance in manager's wallet.")
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid receiver.")
            
    # Retrieve customers for selection
    customers = CustomUser.objects.filter(user_type=1)  # Assuming user_type=1 is for customers
    return render(request, 'wallet/transfer_funds_to_customer.html', {'customers': customers})
