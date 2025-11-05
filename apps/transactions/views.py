from decimal import Decimal
from django.db import transaction as db_transaction
from django.db.models import Sum, Q
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from apps.accounts.models import Account
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from apps.accounts.models import Account
from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer
from apps.fraud.models import FraudAlert

class TransactionCreateView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        from_account = self.request.data.get("from_account")
        to_account = self.request.data.get("to_account")

        # Fetch actual account objects
        from_account_obj = Account.objects.filter(id=from_account).first()
        to_account_obj = Account.objects.filter(id=to_account).first()

        if not from_account_obj or not to_account_obj:
            raise serializers.ValidationError("Invalid account selected.")

        # Save transaction with both accounts
        transaction = serializer.save(from_account=from_account_obj, to_account=to_account_obj)

        amount = transaction.amount

        # Fraud detection
        if amount > 50000:
            FraudAlert.objects.create(
                transaction=transaction,
                reason=f"High-value transaction detected: ₹{amount}"
            )


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(Q(sender__user=user) | Q(receiver__user=user))


class DepositView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        account_id = request.data.get("account")
        amount = request.data.get("amount")

        try:
            account = Account.objects.get(id=account_id, user=request.user)
        except Account.DoesNotExist:
            return Response({"error": "Invalid account."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
        except:
            return Response({"error": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Deposit amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            account.balance += amount
            account.save()

            Transaction.objects.create(
                receiver=account,
                amount=amount,
                status="SUCCESS",
                transaction_type="DEPOSIT",
                description="Deposit to account"
            )

        return Response({"message": f"₹{amount} deposited successfully."}, status=status.HTTP_201_CREATED)


class WithdrawView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        account_id = request.data.get("account")
        amount = request.data.get("amount")

        try:
            account = Account.objects.get(id=account_id, user=request.user)
        except Account.DoesNotExist:
            return Response({"error": "Invalid account."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
        except:
            return Response({"error": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Withdrawal amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)

        if account.balance < amount:
            return Response({"error": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            account.balance -= amount
            account.save()

            Transaction.objects.create(
                sender=account,
                amount=amount,
                status="SUCCESS",
                transaction_type="WITHDRAWAL",
                description="Withdrawal from account"
            )

        return Response({"message": f"₹{amount} withdrawn successfully."}, status=status.HTTP_201_CREATED)


class TransactionDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_staff:
            total_transactions = Transaction.objects.count()
            total_frauds = FraudAlert.objects.count()
            total_amount = Transaction.objects.filter(status='SUCCESS').aggregate(total=Sum('amount'))['total'] or 0
        else:
            total_transactions = (
                Transaction.objects.filter(sender__user=user).count() +
                Transaction.objects.filter(receiver__user=user).count()
            )
            total_frauds = FraudAlert.objects.filter(transaction__sender__user=user).count()
            total_amount = Transaction.objects.filter(
                sender__user=user, status='SUCCESS'
            ).aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            "total_transactions": total_transactions,
            "total_success_amount": total_amount,
            "total_fraud_alerts": total_frauds
        })


class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Transaction.objects.all().order_by("-timestamp")
        return Transaction.objects.filter(account__user=user).order_by("-timestamp")

    def perform_create(self, serializer):
        account_id = self.request.data.get("account_id")
        account = Account.objects.get(id=account_id, user=self.request.user)

        amount = serializer.validated_data['amount']
        ttype = serializer.validated_data['transaction_type']

        if ttype == "DEPOSIT":
            account.balance += amount
        elif ttype == "WITHDRAWAL":
            if amount > account.balance:
                raise ValueError("Insufficient balance")
            account.balance -= amount

        account.save()
        serializer.save(account=account, balance_after=account.balance)

@login_required(login_url='/login/')
def transactions_page(request):
    user = request.user
    transactions = Transaction.objects.filter(
        Q(sender__user=user) | Q(receiver__user=user)
    ).order_by('-timestamp')

    return render(request, 'transactions/transactions.html', {
        'transactions': transactions
    })
