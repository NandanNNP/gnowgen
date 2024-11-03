from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Wallet, WalletTransaction, CustomUser,Notification,SlotBooking,WithdrawRequest
from django.db.models import Q
from decimal import Decimal
from datetime import date

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

from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
import qrcode
from core.models import WithdrawRequest

import os

from django.conf import settings
import os

@login_required
def withdraw_money(request):
    if request.method == 'POST' and request.user.user_type == 1:  # Ensure user is Customer
        amount = Decimal(request.POST.get('amount'))
        upi_id = request.POST.get('upi_id')
        
        # Validate UPI ID and amount
        if amount <= 0:
            messages.error(request, "Invalid amount.")
            return redirect('wallet:withdraw_money')
        if not upi_id or len(upi_id) < 5:
            messages.error(request, "Invalid UPI ID.")
            return redirect('wallet:withdraw_money')
        
        wallet = Wallet.objects.get(user=request.user)
        if wallet.balance < amount:
            messages.error(request, "Insufficient balance.")
            return redirect('wallet:withdraw_money')
        
        # Deduct amount and save the request
        wallet.balance -= amount
        wallet.save()

        # Generate QR code with UPI details
        qr_data = f"upi://pay?pa={upi_id}&am={amount}&cu=INR"
        qr_img = qrcode.make(qr_data)
        
        # Save QR code to the media directory
        qr_path = os.path.join(settings.MEDIA_ROOT, f"withdraw_qr_codes/{request.user.username}_{amount}.png")
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)  # Ensure the directory exists
        qr_img.save(qr_path)

        # Create a WithdrawRequest entry with the relative path
        withdraw_request = WithdrawRequest.objects.create(
            customer=request.user,
            amount=amount,
            upi_id=upi_id,
            qr_code=f"withdraw_qr_codes/{request.user.username}_{amount}.png",
            status='pending'
        )

        # Notify the manager
        manager = CustomUser.objects.filter(user_type=3).first()
        Notification.objects.create(
            user=manager,
            message=f"New withdrawal request: {amount} INR from {request.user.username}.",
        )
        
        messages.success(request, f"Withdrawal request for {amount} INR created successfully. Awaiting manager confirmation.")
        return redirect('wallet:withdraw_money')

    # Retrieve wallet and transactions for display
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = WithdrawRequest.objects.filter(customer_id=request.user,status="completed").order_by('-created_at')
    print(transactions)
    return render(request, 'wallet/withdraw_money.html', {'wallet': wallet, 'transactions': transactions})




@login_required
def approve_withdrawals(request):
    if request.method == 'POST':
        withdraw_id = request.POST.get('withdraw_id')
        action = request.POST.get('action')
        withdraw_request = WithdrawRequest.objects.get(id=withdraw_id)

        if action == 'approve':
            # Approve and complete the withdrawal
            withdraw_request.status = 'completed'
            withdraw_request.save()
            messages.success(request, f"Withdrawal of {withdraw_request.amount} INR approved and confirmed.")
        
        elif action == 'cancel':
            # Cancel the withdrawal and refund the customer's wallet
            wallet = Wallet.objects.get(user=withdraw_request.customer)
            wallet.balance += withdraw_request.amount
            wallet.save()

            # Update request status and send notification
            withdraw_request.status = 'cancelled'
            withdraw_request.save()
            Notification.objects.create(
                user=withdraw_request.customer,
                message=f"Your withdrawal request of {withdraw_request.amount} INR has been cancelled due to an error. The amount has been credited back to your wallet."
            )
            messages.info(request, f"Withdrawal request of {withdraw_request.amount} INR was cancelled and refunded.")

        return redirect('wallet:withdraw_approval')

    # Retrieve pending withdrawals for display
    pending_withdrawals = WithdrawRequest.objects.filter(status='pending')
    return render(request, 'wallet/approve_withdrawals.html', {'pending_withdrawals': pending_withdrawals})



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
    rtransactions = WalletTransaction.objects.filter(receiver=request.user,).order_by('-created_at')
    stransactions = WalletTransaction.objects.filter(sender=request.user,).order_by('-created_at')
    return render(request, 'wallet/manager_wallet.html', {'wallet': wallet, 'transactions': rtransactions,'tran':stransactions})



@login_required
def transaction_history(request):
    # Fetch all transactions for the logged-in user
    transactions = WalletTransaction.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-created_at')
    return render(request, 'wallet/transaction_history.html', {'transactions': transactions})

@login_required
def transfer_funds_to_customer(request):
    # Get receiver_id and amount from query parameters if available
    receiver_id = request.GET.get('receiver_id')
    amount = request.GET.get('amount')

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

                transaction_type = 'manager_to_customer'
                WalletTransaction.objects.create(sender=request.user, receiver=receiver, amount=amount, transaction_type=transaction_type)

                messages.success(request, f"Successfully transferred {amount} to {receiver.username}'s wallet.")

                # Mark the fund transfer notification as processed
                Notification.objects.filter(user=request.user, is_fund_transfer=True, amount=amount).update(is_fund_transfer=False)

                # Confirm the booking for today's date for the receiver
                today = date.today()
                SlotBooking.objects.filter(customer=receiver, date=today, is_confirmed=False).update(is_confirmed=True)

                return redirect('manager:manager_notifications')
            else:
                messages.error(request, "Insufficient balance in manager's wallet.")
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid receiver.")
            
    # Retrieve customers for selection if needed
    customers = CustomUser.objects.filter(user_type=1)  # Assuming user_type=1 is for customers
    return render(request, 'wallet/transfer_funds_to_customer.html', {'customers': customers, 'receiver_id': receiver_id, 'amount': amount})