from django import forms
from core.models import CustomUser, Wallet

class EmployeeCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        widgets = {'password': forms.PasswordInput()}

class FundTransferForm(forms.Form):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.filter(user_type=1))  # Only customers
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
