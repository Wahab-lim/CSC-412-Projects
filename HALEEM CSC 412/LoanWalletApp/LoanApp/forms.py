from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Loan, Wallet


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-input'})
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last name'
        self.fields['email'].widget.attrs['placeholder'] = 'Email address'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'})
    )


class DepositForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter amount',
            'step': '0.01',
            'min': '1',
        })
    )


class LoanForm(forms.Form):
    PAYMENT_MODE_CHOICES = [
        ('monthly', 'Monthly'),
        ('biweekly', 'Bi-weekly (every 2 weeks)'),
        ('weekly', 'Weekly'),
    ]

    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Minimum $1,000',
            'step': '0.01',
            'min': '1000',
            'id': 'loan-amount',
        })
    )
    tenure_months = forms.IntegerField(
        min_value=3,
        max_value=60,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '3 to 60 months',
            'min': '3',
            'max': '60',
            'id': 'loan-tenure',
        })
    )
    payment_mode = forms.ChoiceField(
        choices=PAYMENT_MODE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'loan-payment-mode'})
    )
    wallet = forms.ModelChoiceField(
        queryset=Wallet.objects.none(),
        widget=forms.Select(attrs={'class': 'form-input'}),
        empty_label="Select wallet to receive funds"
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['wallet'].queryset = Wallet.objects.filter(user=user)


class RepayLoanForm(forms.Form):
    wallet = forms.ModelChoiceField(
        queryset=Wallet.objects.none(),
        widget=forms.Select(attrs={'class': 'form-input'}),
        empty_label="Select wallet to pay from"
    )
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Payment amount',
            'step': '0.01',
        })
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['wallet'].queryset = Wallet.objects.filter(user=user)
