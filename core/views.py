# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

# core/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user_type
                if user.user_type == 1:
                    return redirect('customer:customer_dashboard')  # Redirect to customer dashboard
                elif user.user_type == 2:
                    return redirect('employee:employee_dashboard')  # Redirect to employee dashboard
                elif user.user_type == 3:
                    return redirect('manager:manager_dashboard')  # Redirect to manager dashboard
                elif user.user_type == 4:
                    return redirect('admin_module:admin_dashboard')  # Redirect to custom admin dashboard
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


# In notifications/views.py
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Notification
from django.contrib.auth.decorators import login_required

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    if request.method == 'POST':
        notification.delete()
        messages.success(request, "Notification deleted successfully.")
    user=request.user
    if user.user_type == 1:
            return redirect('customer:notification')  
    elif user.user_type == 2:
            return redirect('employee:employee_dashboard')  
    elif user.user_type == 3:
            return redirect('manager:manager_dashboard') 
    elif user.user_type == 4:
            return redirect('admin_module:admin_dashboard')

    return redirect('login')  


