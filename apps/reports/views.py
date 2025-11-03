from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from apps.accounts.models import Account
from apps.transactions.models import Transaction
from apps.loans.models import Loan
from datetime import datetime, timedelta

class DashboardSummaryView(APIView):
    """
    Provides a summary of user's banking data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Account Summary
        accounts = Account.objects.filter(user=user)
        total_balance = accounts.aggregate(total=Sum('balance'))['total'] or 0

        # Loan Summary
        loans = Loan.objects.filter(user=user)
        active_loans = loans.filter(status='APPROVED').count()
        total_loan_amount = loans.filter(status='APPROVED').aggregate(total=Sum('principal_amount'))['total'] or 0

        # Recent Transactions (last 5)
        transactions = Transaction.objects.filter(sender__user=user).order_by('-timestamp')[:5]

        # Monthly Transaction Trend (last 30 days)
        one_month_ago = datetime.now() - timedelta(days=30)
        monthly_total = Transaction.objects.filter(
            sender__user=user,
            timestamp__gte=one_month_ago
        ).aggregate(total=Sum('amount'))['total'] or 0

        data = {
            "account_summary": {
                "total_accounts": accounts.count(),
                "total_balance": total_balance,
            },
            "loan_summary": {
                "total_loans": loans.count(),
                "active_loans": active_loans,
                "total_loan_amount": total_loan_amount
            },
            "transactions": [
                {
                    "id": t.id,
                    "amount": t.amount,
                    "receiver": str(t.receiver.account_number),
                    "status": t.status,
                    "timestamp": t.timestamp
                } for t in transactions
            ],
            "monthly_transaction_total": monthly_total
        }

        return Response(data)

from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

class AdminDashboardView(APIView):
    """
    Provides an overall system summary for Bank Admins.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != "admin":
            return Response(
                {"detail": "Access denied. Admins only."},
                status=status.HTTP_403_FORBIDDEN
            )

        # General stats
        total_users = User.objects.count()
        total_accounts = Account.objects.count()
        total_balance = Account.objects.aggregate(total=Sum('balance'))['total'] or 0

        total_transactions = Transaction.objects.count()
        total_volume = Transaction.objects.aggregate(total=Sum('amount'))['total'] or 0

        total_loans = Loan.objects.count()
        pending_loans = Loan.objects.filter(status="PENDING").count()
        approved_loans = Loan.objects.filter(status="APPROVED").count()

        data = {
            "user_summary": {
                "total_users": total_users,
            },
            "account_summary": {
                "total_accounts": total_accounts,
                "total_balance": total_balance
            },
            "transaction_summary": {
                "total_transactions": total_transactions,
                "total_volume": total_volume
            },
            "loan_summary": {
                "total_loans": total_loans,
                "pending_loans": pending_loans,
                "approved_loans": approved_loans
            }
        }

        return Response(data)
