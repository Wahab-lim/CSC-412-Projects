from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from .models import Wallet, Loan, Transaction
from .forms import RegisterForm, LoginForm, DepositForm, LoanForm, RepayLoanForm


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Wallet.objects.create(user=user, name='Primary Bank', balance=Decimal('0.00'))
            Wallet.objects.create(user=user, name='Secondary Bank', balance=Decimal('0.00'))
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    label = form.fields[field].label if field != '__all__' else ''
                    messages.error(request, f"{label}: {error}" if label else error)
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


def _process_overdue_loans(user):
    """
    Check for overdue loans and attempt to auto-deduct installments from wallets.
    Deducts from Primary Bank first, then Secondary Bank.
    Marks loan as overdue if insufficient funds.
    Marks loan as repaid if fully paid.
    """
    now = timezone.now()
    active_loans = Loan.objects.filter(user=user, status__in=['active', 'overdue'])
    wallets = list(Wallet.objects.filter(user=user).order_by('name'))

    for loan in active_loans:
        if not loan.next_payment_due:
            continue
        if now <= loan.next_payment_due:
            continue

        installment = loan.installment_amount
        collected = Decimal('0.00')

        for wallet in wallets:
            if collected >= installment:
                break
            needed = installment - collected
            if wallet.balance <= Decimal('0.00'):
                continue
            deduct = min(wallet.balance, needed)
            wallet.balance -= deduct
            wallet.save()
            collected += deduct
            Transaction.objects.create(
                user=user,
                wallet=wallet,
                loan=loan,
                amount=deduct,
                transaction_type='loan_deduction',
                description=f'Auto-deduction for Loan #{loan.id} installment'
            )

        if collected > Decimal('0.00'):
            loan.payments_made += collected

        if collected < installment:
            loan.status = 'overdue'
        else:
            loan.status = 'active'
            period_days = loan.get_period_days()
            loan.next_payment_due = loan.next_payment_due + timedelta(days=period_days)

        if loan.payments_made >= loan.total_repayable:
            loan.status = 'repaid'

        loan.save()


@login_required
def dashboard(request):
    _process_overdue_loans(request.user)

    wallets = Wallet.objects.filter(user=request.user)
    total_balance = sum(w.balance for w in wallets)

    active_loans = Loan.objects.filter(user=request.user, status__in=['active', 'overdue'])
    outstanding = sum(loan.remaining_balance() for loan in active_loans)

    next_payment = None
    for loan in active_loans.order_by('next_payment_due'):
        if loan.next_payment_due:
            next_payment = loan
            break

    recent_loans = Loan.objects.filter(user=request.user).order_by('-created_at')[:5]
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:8]

    context = {
        'wallets': wallets,
        'total_balance': total_balance,
        'outstanding_loans': outstanding,
        'next_payment_loan': next_payment,
        'recent_loans': recent_loans,
        'recent_transactions': recent_transactions,
        'active_loans_count': active_loans.count(),
    }
    return render(request, 'dashboard.html', context)


@login_required
def wallets(request):
    _process_overdue_loans(request.user)
    user_wallets = Wallet.objects.filter(user=request.user)
    wallet_data = []
    for wallet in user_wallets:
        txns = Transaction.objects.filter(wallet=wallet).order_by('-created_at')[:10]
        wallet_data.append({'wallet': wallet, 'transactions': txns})

    context = {
        'wallet_data': wallet_data,
        'deposit_form': DepositForm(),
    }
    return render(request, 'wallets.html', context)


@login_required
def deposit(request, wallet_id):
    wallet = get_object_or_404(Wallet, id=wallet_id, user=request.user)

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            wallet.balance += amount
            wallet.save()
            Transaction.objects.create(
                user=request.user,
                wallet=wallet,
                amount=amount,
                transaction_type='deposit',
                description=f'Deposit to {wallet.name}'
            )
            messages.success(request, f'${amount:,.2f} deposited to {wallet.name} successfully!')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
    else:
        messages.error(request, 'Invalid request.')

    return redirect('wallets')


@login_required
def loans(request):
    _process_overdue_loans(request.user)
    user_loans = Loan.objects.filter(user=request.user)
    loan_form = LoanForm(user=request.user)
    repay_form = RepayLoanForm(user=request.user)

    context = {
        'loans': user_loans,
        'loan_form': loan_form,
        'repay_form': repay_form,
    }
    return render(request, 'loans.html', context)


@login_required
def apply_loan(request):
    if request.method == 'POST':
        form = LoanForm(user=request.user, data=request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            tenure_months = form.cleaned_data['tenure_months']
            payment_mode = form.cleaned_data['payment_mode']
            wallet = form.cleaned_data['wallet']

            annual_rate = Decimal('5.00')
            monthly_rate = annual_rate / 100 / 12
            total_repayable = amount * ((1 + monthly_rate) ** tenure_months)
            total_repayable = total_repayable.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            if payment_mode == 'weekly':
                num_periods = tenure_months * 4
                period_days = 7
            elif payment_mode == 'biweekly':
                num_periods = tenure_months * 2
                period_days = 14
            else:
                num_periods = tenure_months
                period_days = 30

            installment = (total_repayable / num_periods).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            now = timezone.now()
            due_date = now + timedelta(days=30 * tenure_months)
            next_payment_due = now + timedelta(days=period_days)

            loan = Loan.objects.create(
                user=request.user,
                wallet=wallet,
                amount=amount,
                interest_rate=annual_rate,
                tenure_months=tenure_months,
                payment_mode=payment_mode,
                status='active',
                total_repayable=total_repayable,
                installment_amount=installment,
                payments_made=Decimal('0.00'),
                due_date=due_date,
                next_payment_due=next_payment_due,
            )

            wallet.balance += amount
            wallet.save()

            Transaction.objects.create(
                user=request.user,
                wallet=wallet,
                loan=loan,
                amount=amount,
                transaction_type='loan_disbursement',
                description=f'Loan #{loan.id} disbursement to {wallet.name}'
            )

            messages.success(
                request,
                f'Loan of ${amount:,.2f} approved! Total repayable: ${total_repayable:,.2f} '
                f'at ${installment:,.2f} per {loan.get_period_label()}.'
            )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        messages.error(request, 'Invalid request.')

    return redirect('loans')


@login_required
def repay_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)

    if loan.status == 'repaid':
        messages.info(request, 'This loan is already fully repaid.')
        return redirect('loans')

    if request.method == 'POST':
        form = RepayLoanForm(user=request.user, data=request.POST)
        if form.is_valid():
            wallet = form.cleaned_data['wallet']
            amount = form.cleaned_data['amount']
            remaining = loan.remaining_balance()

            pay_amount = min(amount, remaining)
            pay_amount = pay_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            if wallet.balance < pay_amount:
                messages.error(request, f'Insufficient balance. {wallet.name} has ${wallet.balance:,.2f}.')
                return redirect('loans')

            wallet.balance -= pay_amount
            wallet.save()

            loan.payments_made += pay_amount

            if loan.payments_made >= loan.total_repayable:
                loan.status = 'repaid'
                messages.success(request, f'Congratulations! Loan #{loan.id} is fully repaid.')
            else:
                loan.status = 'active'
                if loan.next_payment_due and timezone.now() > loan.next_payment_due:
                    loan.next_payment_due = timezone.now() + timedelta(days=loan.get_period_days())
                rem = loan.remaining_balance() - pay_amount
                messages.success(
                    request,
                    f'Payment of ${pay_amount:,.2f} made from {wallet.name}. '
                    f'Remaining balance: ${loan.remaining_balance():,.2f}.'
                )

            loan.save()

            Transaction.objects.create(
                user=request.user,
                wallet=wallet,
                loan=loan,
                amount=pay_amount,
                transaction_type='loan_repayment',
                description=f'Repayment for Loan #{loan.id}'
            )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        messages.error(request, 'Invalid request.')

    return redirect('loans')
