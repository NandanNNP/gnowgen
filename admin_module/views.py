from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import CustomUser, WalletTransaction, Wallet

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.models import Wallet  # Import your Wallet model

@login_required  # Ensures the user is logged in
def admin_dashboard(request):
    # Check if the user is an admin (assuming user_type 4 is for Admin)
    if request.user.user_type == 4:
        # Get the wallet associated with the logged-in admin user
        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            wallet = None  # Handle case where the wallet doesn't exist

        # Pass the user and wallet information to the template
        return render(request, 'admin_module/admin_dashboard.html', {
            'user': request.user,
            'wallet': wallet,
        })
    else:
        # Redirect to a different page if the user is not an admin
        return redirect('login')  # Change 'login' to your login URL name

