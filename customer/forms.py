from django import forms
from core.models import SlotBooking, Wallet

class SlotBookingForm(forms.ModelForm):
    class Meta:
        model = SlotBooking
        fields = ['date']  # Only date is needed now


class WalletWithdrawForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
