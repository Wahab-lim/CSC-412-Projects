from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Wallet(models.Model):
    WALLET_NAMES = [
        ('Primary Bank', 'Primary Bank'),
        ('Secondary Bank', 'Secondary Bank'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    name = models.CharField(max_length=100, choices=WALLET_NAMES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name} (${self.balance})"

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['name']


class Loan(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('monthly', 'Monthly'),
        ('biweekly', 'Bi-weekly (every 2 weeks)'),
        ('weekly', 'Weekly'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('overdue', 'Overdue'),
        ('repaid', 'Repaid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5.00'))
    tenure_months = models.IntegerField(default=12)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='monthly')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    total_repayable = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    installment_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payments_made = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    due_date = models.DateTimeField(null=True, blank=True)
    next_payment_due = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def remaining_balance(self):
        return max(Decimal('0.00'), self.total_repayable - self.payments_made)

    def progress_percent(self):
        if self.total_repayable and self.total_repayable > 0:
            pct = (self.payments_made / self.total_repayable) * 100
            return min(100, int(pct))
        return 0

    def is_overdue_now(self):
        return self.status == 'active' and self.next_payment_due and timezone.now() > self.next_payment_due

    def days_until_next_payment(self):
        if self.next_payment_due:
            delta = self.next_payment_due - timezone.now()
            return delta.days
        return None

    def get_period_days(self):
        if self.payment_mode == 'weekly':
            return 7
        elif self.payment_mode == 'biweekly':
            return 14
        return 30

    def get_period_label(self):
        if self.payment_mode == 'weekly':
            return 'week'
        elif self.payment_mode == 'biweekly':
            return '2 weeks'
        return 'month'

    def __str__(self):
        return f"Loan #{self.id} - {self.user.username} - ${self.amount} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('loan_disbursement', 'Loan Disbursement'),
        ('loan_repayment', 'Loan Repayment'),
        ('loan_deduction', 'Loan Auto-Deduction'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    loan = models.ForeignKey(Loan, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - ${self.amount} ({self.user.username})"

    class Meta:
        ordering = ['-created_at']
