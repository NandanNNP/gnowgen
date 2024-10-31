from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SlotBookingForm
from core.models import SlotBooking, Notification
from django.contrib.auth.decorators import login_required


@login_required
def customer_dashboard(request):
    return render(request, 'customer/customer_dashboard.html')

from .forms import SlotBookingForm  # Assume this form has been created
from core.models import CollectionSchedule
from datetime import datetime, timedelta
from django.utils import timezone
import json


def book_slot_view(request):
    # Retrieve collection schedules
    schedules = CollectionSchedule.objects.filter(date__gte=timezone.now()).values('date', 'waste_type')

    # Format schedules for FullCalendar
    schedule_data = []
    for schedule in schedules:
        schedule_data.append({
            'title': schedule['waste_type'],
            'start': schedule['date'].strftime('%Y-%m-%d'),
            'className': schedule['waste_type'].replace(' ', '-').lower(),
        })

    if request.method == "POST":
        # Get the selected date directly from the POST request
        selected_date = request.POST.get('date')  # Make sure this matches the name in your hidden input

        if selected_date:
            # Create the SlotBooking instance and assign values
            booking = SlotBooking(customer=request.user, date=selected_date)
            booking.save()  # Save the booking to the database

            return redirect('customer:success_page')  # Redirect to the success page or relevant page
        else:
            # Handle the case where no date was provided (should not happen with your current setup)
            print("No date was selected.")
    
    # GET request handling
    return render(request, 'customer/book_slot.html', {
        'schedules': json.dumps(schedule_data)
    })


# customer/views.py






def success_page(request):
    # Retrieve the latest booking for the current customer
    latest_booking = SlotBooking.objects.filter(customer=request.user).order_by('-id').first()
    
    if latest_booking:
        # Get the related collection schedule details (assuming a schedule exists for each booking)
        schedule = CollectionSchedule.objects.filter(date=latest_booking.date).first()
        
        # Find the employee assigned to this schedule
        if schedule:
            # Create a notification for the assigned employee
            Notification.objects.create(
                user=request.user,
                message=f"New booking by {request.user.username} on {latest_booking.date} for {schedule.waste_type}.",
                date=latest_booking.date
            )
    
    # Render the success page
    return render(request, 'customer/success_page.html')




# Notifications view
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'customer/notifications.html', {'notifications': notifications})


def report(request):
    # You can add your report logic here
    return render(request, 'customer/report.html')