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

    employee = models.ForeignKey(CustomUser, limit_choices_to={'user_type': 2}, on_delete=models.CASCADE)
    date = models.DateField()
    waste_type = models.CharField(max_length=20, choices=WASTE_TYPE_CHOICES, default='plastic')  # Set default value

    def __str__(self):
        return f"{self.date} - {self.waste_type}"
    
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} at {self.created_at}"
    




from django.db import models
from django.conf import settings

class SlotBooking(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_type': 1})
    date = models.DateField()
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking for {self.customer.username} on {self.date}"
    


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
