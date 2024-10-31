from django import forms
from django.contrib.auth import get_user_model
from core.models import Address, CollectionSchedule, Notification

User = get_user_model()

class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'user_type']
        widgets = {
            'user_type': forms.HiddenInput(attrs={'value': '1'}),  # Set default to Customer
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].initial = 1  # Default to Customer type

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'postal_code']  # Adjust fields to match the Address model
        widgets = {
            'street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
        }

from django import forms
from core.models import CollectionSchedule

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = CollectionSchedule
        fields = ['date', 'waste_type']  # Ensure only 'date' and 'waste_type' are included

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter notification message'}),
        }
