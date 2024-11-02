from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SlotBookingForm
from core.models import SlotBooking, Notification,Wallet
from django.contrib.auth.decorators import login_required


@login_required
def customer_dashboard(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    return render(request, 'customer/customer_dashboard.html',{'wallet':wallet})

from .forms import SlotBookingForm  # Assume this form has been created
from core.models import CollectionSchedule
from datetime import datetime, timedelta
from django.utils import timezone
import json


# customer/views.py
import json
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import SlotBooking, CollectionSchedule, Notification

@login_required
def book_slot_view(request):
    schedules = CollectionSchedule.objects.filter(date__gte=timezone.now()).values('date', 'waste_type')
    schedule_data = [
        {'title': schedule['waste_type'], 'start': schedule['date'].strftime('%Y-%m-%d'), 'className': schedule['waste_type'].replace(' ', '-').lower()}
        for schedule in schedules
    ]

    if request.method == "POST":
        selected_date = request.POST.get('date')

        if selected_date:
            booking = SlotBooking(customer=request.user, date=selected_date)
            booking.save()  # Save to get an ID before generating QR code
            booking.generate_qr_code()  # Generate and save QR code
            

            messages.success(request, "Your booking has been confirmed with a QR code.")
            return redirect('customer:success_page')
        else:
            messages.error(request, "No date was selected. Please try again.")
    
    return render(request, 'customer/book_slot.html', {
        'schedules': json.dumps(schedule_data)
    })



@login_required
def view_bookings(request):
    # Retrieve all booking slots for the logged-in customer
    bookings = SlotBooking.objects.filter(customer=request.user).order_by('-date')
    return render(request, 'customer/view_bookings.html', {'bookings': bookings})

# customer/views.py






# customer/views.py

@login_required
def success_page(request):
    latest_booking = SlotBooking.objects.filter(customer=request.user).order_by('-id').first()

    if latest_booking:
        schedule = CollectionSchedule.objects.filter(date=latest_booking.date).first()
        if schedule:
            Notification.objects.create(
                user=request.user,
                message=f"New booking by {request.user.username} on {latest_booking.date} for {schedule.waste_type}.",
                date=latest_booking.date
            )

    return render(request, 'customer/success_page.html', {'booking': latest_booking})



# Notifications view
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'customer/notifications.html', {'notifications': notifications})


def report(request):
    # You can add your report logic here
    return render(request, 'customer/report.html')