from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EmployeeCreationForm, FundTransferForm
from core.models import CustomUser, Wallet,Notification

@login_required
def manager_dashboard(request):
    return render(request, 'manager/manager_dashboard.html')

@login_required
def create_employee(request):
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.user_type = 2  # Set as Employee
            employee.set_password(form.cleaned_data['password'])
            employee.save()
            messages.success(request, "Employee created successfully.")
            return redirect('manager:employee_list')
    else:
        form = EmployeeCreationForm()
    return render(request, 'manager/create_employee.html', {'form': form})

@login_required
def verify_employee(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id, user_type=2)
    employee.is_verified = True
    employee.save()
    messages.success(request, f"Employee {employee.username} verified.")
    return redirect('manager:employee_list')


@login_required
def employee_list(request):
    employees = CustomUser.objects.filter(user_type=2)
    return render(request, 'manager/employee_list.html', {'employees': employees})

@login_required
def view_verified_employees(request):
    verified_employees = CustomUser.objects.filter(user_type=2, is_verified=True)
    return render(request, 'manager/verified_employee_list.html', {'employees': verified_employees})

@login_required
def manage_employees(request):
    # Query all employees in the system
    employees = CustomUser.objects.filter(user_type=2)  # Assuming user_type 2 indicates Employee
    return render(request, 'manager/manage_employees.html', {'employees': employees})

@login_required
def manager_notifications(request):
    # Display all notifications received by the manager from employees
    notifications = Notification.objects.filter(is_fund_transfer=1).order_by('-created_at')
    noti = Notification.objects.filter(is_fund_transfer=0,rvid=5).order_by('-created_at')  
    return render(request, 'manager/manager_notifications.html', {'notifications': notifications,'noti':noti})


@login_required
def transfer_funds(request, notification_id):
    # Get the notification details
    notification = get_object_or_404(Notification, id=notification_id)
    
    # Assuming the message format is: "Transfer {amount} to {customer.username}'s wallet for {weight} kg of {waste_type} collected."
    message_parts = notification.message.split(" ")
    amount = float(message_parts[1])  # Extract the amount from the notification message
    customer_username = message_parts[5]  # Extract the customer username

    # Handle the fund transfer logic
    if request.method == 'POST':
        wallet, created = Wallet.objects.get_or_create(user__username=customer_username)
        wallet.balance += amount  # Add the amount to the wallet
        wallet.save()

        # Optionally, you can delete the notification after handling it
        notification.delete()

        messages.success(request, f"Successfully transferred {amount} to {customer_username}'s wallet.")
        return redirect('manager:manager_notifications')

    return render(request, 'manager/transfer_funds.html', {
        'notification': notification,
        'amount': amount,
        'customer_username': customer_username
    })

@login_required
def send_notification_to_employee(request):
    # Send a notification to a specific employee
    if request.method == 'POST':
        message = request.POST.get('message')
        employee_id = request.POST.get('employee_id')
        employee = CustomUser.objects.get(id=employee_id, user_type=2)  # user_type=2 for Employee
        Notification.objects.create(user=employee, message=message)
        messages.success(request, "Notification sent to employee.")
        return redirect('manager:manager_notifications')
    employees = CustomUser.objects.filter(user_type=2)  # All employees
    return render(request, 'manager/send_notification.html', {'employees': employees})



