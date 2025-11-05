import os
import requests
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.db import transaction as db_transaction
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required, user_passes_test

from apps.accounts.models import Account
from apps.transactions.models import Transaction
from apps.loans.models import Loan
from apps.notifications.models import Notification
from apps.fraud.models import FraudAlert
from apps.audit.models import AuditLog
from apps.users.models import User


# ============================================================
# HELPER — Auto-detect API base (Render-safe)
# ============================================================

def get_api_base_url():
    """
    Dynamically returns API base URL.
    On Render: use localhost to avoid HTTPS self-call timeout.
    Locally: use API_BASE_URL from settings or .env.
    """
    if "RENDER" in os.environ:
        return "http://127.0.0.1:8000/api/v1"
    return os.environ.get("API_BASE_URL", getattr(settings, "API_BASE_URL", "http://127.0.0.1:8000/api/v1"))


# ============================================================
# STATIC PAGES
# ============================================================

def home_page(request):
    return render(request, "home.html")


def about_page(request):
    return render(request, "about.html")


def contact_page(request):
    return render(request, "contact.html")


# ============================================================
# AUTHENTICATION PAGES
# ============================================================

def login_page(request):
    """User login via API"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        api_base = get_api_base_url()
        api_url = f"{api_base}/users/token/"

        try:
            response = requests.post(api_url, json={"username": username, "password": password}, timeout=5)
        except requests.exceptions.RequestException as e:
            print("⚠️ Login API error:", e)
            messages.error(request, "Unable to connect to authentication server.")
            return redirect("login")

        if response.status_code == 200:
            data = response.json()
            access = data.get("access")
            refresh = data.get("refresh")

            res = redirect("dashboard")
            res.set_cookie("access", access, httponly=True)
            res.set_cookie("refresh", refresh, httponly=True)
            messages.success(request, f"Welcome back, {username}!")
            return res
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "users/login.html")


def register_page(request):
    """User registration via API"""
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "❌ Passwords do not match.")
            return redirect("register")

        api_base = get_api_base_url()
        api_url = f"{api_base}/users/register/"

        data = {
            "username": username,
            "email": email,
            "phone": phone,
            "password": password,
            "password2": confirm_password,
        }

        try:
            response = requests.post(api_url, json=data, timeout=5)
            response_data = response.json()
        except requests.exceptions.RequestException:
            messages.error(request, "🚫 Unable to connect to registration API.")
            return redirect("register")
        except ValueError:
            messages.error(request, "⚠️ Invalid server response.")
            return redirect("register")

        if response.status_code == 201:
            messages.success(request, "✅ Account created successfully! Please log in.")
            return redirect("login")
        else:
            error_message = response_data.get("detail") or response_data
            messages.error(request, f"Registration failed: {error_message}")
            return redirect("register")

    return render(request, "users/register.html")


def logout_page(request):
    """Clear cookies and log user out"""
    response = redirect("login")
    response.delete_cookie("access")
    response.delete_cookie("refresh")
    messages.success(request, "You have been logged out successfully.")
    return response


# ============================================================
# DASHBOARD
# ============================================================

@login_required(login_url="/login/")
def dashboard_page(request):
    """Main dashboard page"""
    user = request.user

    total_accounts = Account.objects.filter(user=user).count()
    total_balance = Account.objects.filter(user=user).aggregate(total=Sum("balance"))["total"] or 0
    user_accounts = Account.objects.filter(user=user)
    fraud_alerts = FraudAlert.objects.filter(
        Q(transaction__sender__in=user_accounts) | Q(transaction__receiver__in=user_accounts)
    ).distinct().count()

    recent_transactions = Transaction.objects.filter(
        Q(sender__user=user) | Q(receiver__user=user)
    ).order_by("-timestamp")[:5]

    pending_loans = []
    if user.is_staff:
        pending_loans = Loan.objects.filter(status="PENDING").order_by("-created_at")

    all_notifications = Notification.objects.filter(user=user).order_by("-created_at")
    unread_count = all_notifications.filter(is_read=False).count()
    notifications = all_notifications[:5]

    return render(
        request,
        "dashboard.html",
        {
            "total_accounts": total_accounts,
            "total_balance": total_balance,
            "fraud_alerts": fraud_alerts,
            "recent_transactions": recent_transactions,
            "pending_loans": pending_loans,
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


# ============================================================
# ACCOUNTS
# ============================================================

@login_required(login_url="/login/")
def accounts_list_page(request):
    """List all user accounts"""
    token = request.COOKIES.get("access")
    if not token:
        return redirect("login")

    headers = {"Authorization": f"Bearer {token}"}
    api_base = get_api_base_url()

    try:
        response = requests.get(f"{api_base}/accounts/", headers=headers, timeout=5)
        accounts = response.json() if response.status_code == 200 else []
    except Exception as e:
        print("Error fetching accounts:", e)
        accounts = []

    return render(request, "accounts/list.html", {"accounts": accounts})


@login_required(login_url="/login/")
def accounts_create_page(request):
    """Create a new bank account"""
    access_token = request.COOKIES.get("access")
    if not access_token:
        messages.error(request, "Please log in first.")
        return redirect("login")

    if request.method == "POST":
        account_type = request.POST.get("account_type", "SAVINGS")
        api_base = get_api_base_url()
        api_url = f"{api_base}/accounts/create/"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"account_type": account_type}

        try:
            response = requests.post(api_url, json=data, headers=headers, timeout=5)
        except requests.exceptions.RequestException:
            messages.error(request, "Unable to connect to account service.")
            return redirect("accounts-create")

        if response.status_code == 201:
            messages.success(request, "✅ Account created successfully!")
            return redirect("accounts-list")
        else:
            messages.error(request, f"⚠️ Failed: {response.text}")
            return redirect("accounts-create")

    return render(request, "accounts/create.html")


# ============================================================
# TRANSACTIONS
# ============================================================

@login_required(login_url="/login/")
def transactions_page(request):
    """Handle fund transfers"""
    user = request.user
    accounts = Account.objects.filter(user=user, is_active=True)

    if request.method == "POST":
        from_id = request.POST.get("from_account")
        to_id = request.POST.get("to_account")
        amount = request.POST.get("amount")

        if from_id == to_id:
            messages.error(request, "Cannot transfer to the same account.")
        else:
            try:
                amount = Decimal(amount)
                if amount <= 0:
                    raise ValueError
            except:
                messages.error(request, "Invalid amount.")
            else:
                from_account = accounts.filter(id=from_id).first()
                to_account = Account.objects.filter(id=to_id, is_active=True).first()

                if not from_account or not to_account:
                    messages.error(request, "Invalid account selection.")
                elif from_account.balance < amount:
                    messages.error(request, "Insufficient balance.")
                else:
                    with db_transaction.atomic():
                        from_account.balance -= amount
                        from_account.save()
                        to_account.balance += amount
                        to_account.save()

                        Transaction.objects.create(
                            sender=from_account,
                            receiver=to_account,
                            amount=amount,
                            status="SUCCESS",
                            transaction_type="TRANSFER_OUT",
                            description=f"Transfer from {from_account.account_number} to {to_account.account_number}",
                        )
                    messages.success(request, f"₹{amount} transferred successfully!")

    transactions = Transaction.objects.filter(
        Q(sender__user=user) | Q(receiver__user=user)
    ).order_by("-timestamp")

    return render(
        request,
        "transactions/transactions.html",
        {"accounts": accounts, "transactions": transactions},
    )


# ============================================================
# LOANS
# ============================================================

@login_required(login_url="/login/")
def loan_apply_page(request):
    """Apply for a loan"""
    user = request.user
    accounts = Account.objects.filter(user=user, is_active=True)

    if request.method == "POST":
        account_id = request.POST.get("account")
        loan_type = request.POST.get("loan_type")
        principal_amount = request.POST.get("principal_amount")
        interest_rate = request.POST.get("interest_rate")
        term_months = request.POST.get("term_months")

        try:
            principal_amount = Decimal(principal_amount)
            interest_rate = Decimal(interest_rate)
            term_months = int(term_months)
            if principal_amount <= 0 or interest_rate <= 0 or term_months <= 0:
                raise ValueError
        except:
            messages.error(request, "Invalid input values.")
        else:
            account = accounts.filter(id=account_id).first()
            if not account:
                messages.error(request, "Invalid account selected.")
            else:
                loan = Loan.objects.create(
                    user=user,
                    account=account,
                    loan_type=loan_type,
                    principal_amount=principal_amount,
                    interest_rate=interest_rate,
                    term_months=term_months,
                )
                messages.success(request, f"✅ Loan applied successfully! EMI: ₹{loan.emi}")

    return render(request, "loans/loans_apply.html", {"accounts": accounts})


@login_required(login_url="/login/")
def my_loans_page(request):
    """List all loans of the current user"""
    user = request.user
    loans = Loan.objects.filter(user=user).order_by("-created_at")
    return render(request, "loans/my_loans.html", {"loans": loans})


@login_required(login_url="/login/")
def loan_approval_action(request, loan_id):
    """Approve or reject loans (admin only)"""
    if not request.user.is_staff:
        messages.error(request, "Unauthorized access.")
        return redirect("dashboard")

    if request.method == "POST":
        action = request.POST.get("action")  # APPROVE or REJECT
        loan = Loan.objects.filter(id=loan_id, status="PENDING").first()
        if loan:
            if action == "APPROVE":
                loan.status = "APPROVED"
                loan.account.balance += loan.principal_amount
                loan.account.save()
            elif action == "REJECT":
                loan.status = "REJECTED"
            loan.save()
            messages.success(request, f"Loan {action}D successfully!")
        else:
            messages.error(request, "Loan not found or already processed.")

    return redirect("dashboard")


# ============================================================
# ADMIN / AUDIT
# ============================================================

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_staff)
def audit_logs_page(request):
    """Display recent audit logs"""
    audit_logs = AuditLog.objects.all().order_by("-created_at")[:100]
    return render(request, "audit/audit_logs.html", {"audit_logs": audit_logs})


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_staff)
def admin_users_page(request):
    """Admin user management"""
    users = User.objects.all().order_by("-date_joined")
    return render(request, "users/admin_users.html", {"users": users})
