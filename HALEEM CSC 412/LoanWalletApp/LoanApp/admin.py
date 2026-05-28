from django.contrib import admin
from .models import Wallet, Loan, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'balance', 'created_at')
    list_filter = ('name',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'payment_mode', 'tenure_months', 'created_at')
    list_filter = ('status', 'payment_mode')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet', 'amount', 'transaction_type', 'created_at')
    list_filter = ('transaction_type',)
