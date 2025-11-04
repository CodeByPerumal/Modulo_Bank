# from rest_framework import generics, permissions
# from rest_framework.response import Response
# from rest_framework import status
# from django.shortcuts import get_object_or_404
# from django.db.models import Sum, Q


# from apps.accounts import models

# from .models import Transaction
# from .serializers import TransactionSerializer
# from apps.accounts.models import Account
# from apps.fraud.models import FraudAlert  # ✅ added for fraud detection


# class TransactionCreateView(generics.CreateAPIView):
#     """
#     Handle new money transfer transactions.
#     Automatically flags high-value transactions as potential fraud.
#     """
#     queryset = Transaction.objects.all()
#     serializer_class = TransactionSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         # Get the sender account from the authenticated user
#         sender_account = self.request.user.accounts.first()
#         # transaction = serializer.save(sender=sender_account)
#         transaction = serializer.save()


#         # --- Fraud Detection Logic ---
#         amount = transaction.amount
#         if amount > 50000:  # You can adjust this threshold later
#             FraudAlert.objects.create(
#                 transaction=transaction,
#                 reason=f"High-value transaction detected: ₹{amount}"
#             )


# class TransactionListView(generics.ListAPIView):
#     """
#     List all transactions related to the authenticated user.
#     """
#     serializer_class = TransactionSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return Transaction.objects.filter(sender__user=user) | Transaction.objects.filter(receiver__user=user)

# # apps/transactions/views.py
# from decimal import Decimal
# from django.db import transaction as db_transaction
# from rest_framework import generics, permissions, status
# from rest_framework.response import Response
# from apps.accounts.models import Account
# from apps.transactions.models import Transaction

# class DepositView(generics.CreateAPIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         account_id = request.data.get("account")
#         amount = request.data.get("amount")

#         try:
#             account = Account.objects.get(id=account_id, user=request.user)
#         except Account.DoesNotExist:
#             return Response({"error": "Invalid account."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             amount = Decimal(amount)
#         except:
#             return Response({"error": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

#         if amount <= 0:
#             return Response({"error": "Deposit amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)

#         with db_transaction.atomic():
#             account.balance += amount
#             account.save()

#             Transaction.objects.create(
#                 receiver=account,
#                 amount=amount,
#                 status="SUCCESS",
#                 transaction_type="DEPOSIT",
#                 description="Deposit to account"
#             )

#         return Response({"message": f"₹{amount} deposited successfully."}, status=status.HTTP_201_CREATED)


# class WithdrawView(generics.CreateAPIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         account_id = request.data.get("account")
#         amount = request.data.get("amount")

#         try:
#             account = Account.objects.get(id=account_id, user=request.user)
#         except Account.DoesNotExist:
#             return Response({"error": "Invalid account."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             amount = Decimal(amount)
#         except:
#             return Response({"error": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

#         if amount <= 0:
#             return Response({"error": "Withdrawal amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)

#         if account.balance < amount:
#             return Response({"error": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

#         with db_transaction.atomic():
#             account.balance -= amount
#             account.save()

#             Transaction.objects.create(
#                 sender=account,
#                 amount=amount,
#                 status="SUCCESS",
#                 transaction_type="WITHDRAWAL",
#                 description="Withdrawal from account"
#             )

#         return Response({"message": f"₹{amount} withdrawn successfully."}, status=status.HTTP_201_CREATED)

# from rest_framework.views import APIView
# from apps.fraud.models import FraudAlert
# from rest_framework.response import Response
# # from django.db.models import Sum, Q


# class TransactionDashboardView(APIView):
#     """
#     Summary dashboard of transactions and fraud alerts.
#     """
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         if user.is_staff:
#             total_transactions = Transaction.objects.count()
#             total_frauds = FraudAlert.objects.count()
#             total_amount = Transaction.objects.filter(status='SUCCESS').aggregate(total=Sum('amount'))['total'] or 0
#         else:
#             total_transactions = Transaction.objects.filter(
#                 sender__user=user
#             ).count() + Transaction.objects.filter(
#                 receiver__user=user
#             ).count()
#             total_frauds = FraudAlert.objects.filter(
#                 transaction__sender__user=user
#             ).count()
#             total_amount = Transaction.objects.filter(
#                 sender__user=user, status='SUCCESS'
#             ).aggregate(total=Sum('amount'))['total'] or 0

#         return Response({
#             "total_transactions": total_transactions,
#             "total_success_amount": total_amount,
#             "total_fraud_alerts": total_frauds
#         })

# from django.shortcuts import render

# def dashboard_page(request):
#     data = {
#         "total_transactions": Transaction.objects.count(),
#         "total_success_amount": Transaction.objects.filter(status="SUCCESS").aggregate(total=Sum("amount"))["total"] or 0,
#         "total_fraud_alerts": FraudAlert.objects.count(),
#     }
#     return render(request, "dashboard.html", data)


# apps/transactions/views.py
from decimal import Decimal
from django.db import transaction as db_transaction
from django.db.models import Sum, Q
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.accounts.models import Account
from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer
from apps.fraud.models import FraudAlert


# ------------------ API VIEWS ------------------ #

class TransactionCreateView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        sender_account = self.request.user.accounts.first()
        transaction = serializer.save()
        amount = transaction.amount

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


# ------------------ FRONTEND TEMPLATE VIEW ------------------ #

