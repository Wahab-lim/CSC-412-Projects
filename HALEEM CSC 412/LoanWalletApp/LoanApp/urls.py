from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('wallets/', views.wallets, name='wallets'),
    path('wallets/<int:wallet_id>/deposit/', views.deposit, name='deposit'),
    path('loans/', views.loans, name='loans'),
    path('loans/apply/', views.apply_loan, name='apply_loan'),
    path('loans/<int:loan_id>/repay/', views.repay_loan, name='repay_loan'),
]
