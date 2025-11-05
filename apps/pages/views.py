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


def home_page(request):
    return render(request, "home.html")


def about_page(request):
    return render(request, "about.html")


def contact_page(request):
    return render(request, "contact.html")


# ✅ Updated login_page (Render + Local support)
def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Dynamically choose the correct API base URL
        api_base = os.environ.get("API_BASE_URL", settings.API_BASE_URL)
        api_url = f"{api_base}/users/token/"

        try:
            response = requests.post(
                api_url,
                json={"username": username, "password": password},
                timeout=5  # avoid gunicorn hang
            )
        except requests.exceptions.RequestException as e:
            print("⚠️ Login API error:", e)
            messages.error(request, "Unable to connect to the authentication server.")
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


# ✅ Updated register_page (Render + Local support)
def register_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "❌ Passwords do not match.")
            return redirect("register")

        api_base = os.environ.get("API_BASE_URL", settings.API_BASE_URL)
        api_url = f"{api_base}/users/register/"

        data = {
            "username": username,
            "email": email,
            "phone": phone,
            "password": password,
            "password2": confirm_password
        }

        try:
            response = requests.post(api_url, json=data, timeout=5)
            response_data = response.json()
        except requests.exceptions.RequestException:
            messages.error(request, "🚫 Unable to connect to the registration API.")
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
    response = redirect("login")
    response.delete_cookie("access")
    response.delete_cookie("refresh")
    messages.success(request, "You have been logged out successfully.")
    return response


@login_required(login_url="/login/")
def dashboard_page(request):
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


@login_required(login_url="/login/")
def accounts_list_page(request):
    token = request.COOKIES.get("access")
    if not token:
        return redirect("login")

    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{settings.API_BASE_URL}/accounts/", headers=headers, timeout=5)
        accounts = response.json() if response.status_code == 200 else []
    except Exception as e:
        print("Error fetching accounts:", e)
        accounts = []

    return render(request, "accounts/list.html", {"accounts": accounts})


@login_required(login_url="/login/")
def transactions_page(request):
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
