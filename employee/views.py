# employee/views.py
from core.models import CustomUser, Address, CollectionSchedule, Notification, SlotBooking
from .forms import UserCreationForm, AddressForm, ScheduleForm, NotificationForm,CollectionForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from core.models import Wallet


from functools import wraps

def verified_employee_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated and is a verified employee
        if request.user.is_authenticated and request.user.user_type == 2 and request.user.is_verified:
            return view_func(request, *args, **kwargs)
        
        # Show an error message and redirect if not verified
        messages.error(request, "You need to be a verified employee to access this page.")
        return redirect('employee:employee_dashboard')  # Redirect to a relevant page for unverified employees
    return _wrapped_view


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
    three_days_ago = current_date - timedelta(days=3)
    


    # Delete expired notifications and slot bookings
    SlotBooking.objects.filter(date__lt=three_days_ago).delete()
    threshold_date = timezone.now().date() - timedelta(days=2)

    # Delete notifications where the `date` is older than the threshold date and is not null
    Notification.objects.filter(date__lt=threshold_date, date__isnull=False).delete()
    

    customer_notifications = Notification.objects.filter(
        user__user_type=1, date__gte=current_date
    ).order_by('date')

    print(customer_notifications)

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
@verified_employee_required
def employee_dashboard(request):
    return render(request, 'employee/employee_dashboard.html')

@login_required
@verified_employee_required
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
        message = request.POST.get('message')
        manager = CustomUser.objects.filter(user_type=3).first()  # Assuming user_type=3 for Manager
        rvid= '5'
        Notification.objects.create(user=manager, message=message,rvid=rvid)
        messages.success(request, "Notification sent to manager.")
        return redirect('employee:employee_dashboard')
    return render(request, 'employee/send_notification.html')

def view_manager_notifications(request):
    # Fetch notifications sent by managers
    notifications = Notification.objects.filter(user=request.user)  # Adjust the filter as needed

    return render(request, 'employee/view_manager_notifications.html', {'notifications': notifications})



#qr 

@login_required
def scan_qr_code(request):
    return render(request, 'employee/scan_qr_code.html')

from django.shortcuts import render, get_object_or_404, redirect
from core.models import SlotBooking
from .forms import CollectionForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def collect(request, booking_id):
    try:
        booking = SlotBooking.objects.get(id=booking_id, customer__is_verified=True)
    except SlotBooking.DoesNotExist:
        # Render an error page if the booking is not found
        return render(request, 'employee/error_page.html', {
            'error_message': "The specified booking was not found or the customer is not verified."
        })
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            collected_weight = form.cleaned_data['collected_weight']
            booking.collected_weight = collected_weight
            booking.save()


            collection_schedule = CollectionSchedule.objects.filter(date=booking.date, employee=request.user).first()
            # Calculate the total amount to be transferred
            waste_type = collection_schedule.waste_type  # Assuming SlotBooking has a related CollectionSchedule
            price_per_kg = CollectionSchedule.PRICE_PER_KG[waste_type]
            total_amount = collected_weight * price_per_kg

            # Create notification for the manager
            manager = CustomUser.objects.filter(user_type=3).first()
            print(f"Customer Username: {booking.customer.username}")  # Assuming there's only one manager
            Notification.objects.create(
                user=manager,
                message=f"Transfer {total_amount} to {booking.customer.username}'s wallet for {collected_weight} kg of {waste_type} collected.",
                is_fund_transfer=True,
                amount=total_amount,
                rvid=booking.customer.id
            )

            messages.success(request, "Collection data submitted successfully. Notification sent to manager.")
            return redirect('employee:employee_dashboard')
    else:
        form = CollectionForm()

    return render(request, 'employee/collect_form.html', {'booking': booking, 'form': form})
