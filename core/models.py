# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Customer'),
        (2, 'Employee'),
        (3, 'Manager'),
        (4, 'Admin'),
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    

#booking and Notification section

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.postal_code}"

class CollectionSchedule(models.Model):
    WASTE_TYPE_CHOICES = [
        ('plastic', 'Plastic'),
        ('iron', 'Iron'),
        ('paper', 'Paper'),
        ('e-waste', 'E-Waste'),
        ('aluminum', 'Aluminum'),
        ('glass', 'Glass'),
    ]

    # Price per kg for each waste type
    PRICE_PER_KG = {
        'plastic': 10,   # Example price
        'iron': 20,
        'paper': 5,
        'e-waste': 50,
        'aluminum': 30,
        'glass': 15,
    }

    employee = models.ForeignKey(CustomUser, limit_choices_to={'user_type': 2}, on_delete=models.CASCADE)
    date = models.DateField()
    waste_type = models.CharField(max_length=20, choices=WASTE_TYPE_CHOICES, default='plastic')

    def __str__(self):
        return f"{self.date} - {self.waste_type}"
    
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_fund_transfer = models.BooleanField(default=False)
    amount=models.FloatField(default=0.00,null=True) 
    rvid=models.TextField(null=True)

    def __str__(self):
        return f"Notification for {self.user.username} at {self.created_at}"
    






# core/models.py
from django.db import models
from django.conf import settings
import qrcode  # Add the qrcode library in your project (install with pip install qrcode[pil])
from io import BytesIO
from django.core.files import File

# core/models.py

class SlotBooking(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_type': 1})
    date = models.DateField()
    is_confirmed = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    collected_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # New field

    def __str__(self):
        return f"Booking for {self.customer.username} on {self.date}"

    def generate_qr_code(self):
        qr_data = f"Customer: {self.customer.username}, Date: {self.date}, Booking ID: {self.id}"  # Include booking ID
        qr = qrcode.make(qr_data)

        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        qr_image_file = File(buffer, name=f'qr_code_{self.id}.png')

        self.qr_code.save(qr_image_file.name, qr_image_file, save=True)


    
    


# wallet section

# core/models.py
from django.db import models
from django.conf import settings

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.user.username}'s Wallet"

class WalletTransaction(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions_sent')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20)  # Options: 'admin_to_admin', 'admin_to_manager', 'manager_to_customer', 'withdrawal'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} sent {self.amount} to {self.receiver.username} on {self.created_at}"
    
from django.db import models
from django.conf import settings
from decimal import Decimal

class WithdrawRequest(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    upi_id = models.CharField(max_length=50)
    qr_code = models.ImageField(upload_to='withdraw_qr_codes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Withdraw request by {self.customer.username} for {self.amount} INR"

