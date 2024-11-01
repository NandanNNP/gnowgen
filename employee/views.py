# employee/views.py
from core.models import CustomUser, Address, CollectionSchedule, Notification, SlotBooking
from .forms import UserCreationForm, AddressForm, ScheduleForm, NotificationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from core.models import Wallet

@login_required
def create_user(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        address_form = AddressForm(request.POST)
        if user_form.is_valid() and address_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = 1  # Set as Customer
            user.save()
            address = address_form.save(commit=False)
            address.user = user
            address.save()
            messages.success(request, f"User {user.username} has been created successfully.")
            return redirect('user_list')
    else:
        user_form = UserCreationForm()
        address_form = AddressForm()
    return render(request, 'employee/create_user.html', {'user_form': user_form, 'address_form': address_form})

@login_required
def verify_user(request, user_id):
    if request.user.user_type != 2:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')

    user_to_verify = get_object_or_404(CustomUser, id=user_id, user_type=1)

    if request.method == 'POST':
        user_to_verify.is_verified = True
        user_to_verify.save()

        # Automatically create a wallet if one does not exist
        Wallet.objects.get_or_create(user=user_to_verify, defaults={'balance': 0.0})

        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = user_to_verify
            address.save()
            messages.success(request, f"User {user_to_verify.username} has been verified, wallet created, and address added successfully.")
            return redirect('employee:verify_user_list')
    else:
        address_form = AddressForm()

    return render(request, 'employee/verify_user.html', {'user': user_to_verify, 'address_form': address_form})


@login_required
def verify_user_list(request):
    if request.user.user_type != 2:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')

    unverified_users = CustomUser.objects.filter(is_verified=False, user_type=1)
    return render(request, 'employee/verify_user_list.html', {'unverified_users': unverified_users})

@login_required
def verified_user_list(request):
    if request.user.user_type != 2:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')

    verified_users = CustomUser.objects.filter(is_verified=True).prefetch_related('address_set')
    return render(request, 'employee/verified_user_list.html', {'verified_users': verified_users})

@login_required
def notification_manager(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee:notification_manager')
    else:
        form = NotificationForm()

    current_date = timezone.now().date()

    # Delete expired notifications and slot bookings
    SlotBooking.objects.filter(date__lt=current_date).delete()
    Notification.objects.filter(user__slotbooking__date__lt=current_date,date__isnull=False).delete()

    customer_notifications = Notification.objects.filter(
        user__user_type=1, date__gte=current_date
    ).order_by('date')

    return render(request, 'employee/notification_manager.html', {
        'form': form,
        'customer_notifications': customer_notifications
    })

@login_required
def view_address(request, user_id):
    if request.user.user_type != 2:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')

    user = get_object_or_404(CustomUser, id=user_id, is_verified=True, user_type=1)
    address = user.address_set.first()

    return render(request, 'employee/view_address.html', {'user': user, 'address': address})

@login_required
def employee_dashboard(request):
    return render(request, 'employee/employee_dashboard.html')

@login_required
def collection_management(request):
    if request.method == 'POST':
        date = request.POST['date']
        waste_type = request.POST['waste_type']
        employee = request.user

        new_schedule = CollectionSchedule(
            employee=employee,
            date=date,
            waste_type=waste_type,
        )
        new_schedule.save()

        return redirect('employee:collection_management')

    collections = CollectionSchedule.objects.filter(employee=request.user)
    return render(request, 'employee/collection_management.html', {'collections': collections})

@login_required
def view_schedule(request):
    # Calculate the date one month ago
    one_month_ago = timezone.now() - timedelta(days=30)

    # Delete collection schedules older than one month
    CollectionSchedule.objects.filter(date__lt=one_month_ago.date()).delete()
    schedules = CollectionSchedule.objects.all()

    schedule_data = [
        {
            'title': schedule.waste_type.title(),
            'start': schedule.date.isoformat(),
            'className': schedule.waste_type.lower()
        } for schedule in schedules
    ]

    return render(request, 'employee/view_schedule.html', {'schedules': schedule_data})


@login_required
def send_notification_to_manager(request):
    # Employee sends notification to manager after completing waste collection
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        amount = request.POST.get('amount')
        message = f"Collected waste from {customer_name}. Transfer amount {amount} to customer's account."
        manager = CustomUser.objects.filter(user_type=3).first()  # Assuming user_type=3 for Manager
        Notification.objects.create(user=manager, message=message)
        messages.success(request, "Notification sent to manager.")
        return redirect('employee:employee_dashboard')
    return render(request, 'employee/send_notification.html')

def view_manager_notifications(request):
    # Fetch notifications sent by managers
    notifications = Notification.objects.filter(user=request.user)  # Adjust the filter as needed

    return render(request, 'employee/view_manager_notifications.html', {'notifications': notifications})

