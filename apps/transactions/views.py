from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Transaction
from .serializers import TransactionSerializer
from apps.accounts.models import Account
from apps.fraud.models import FraudAlert  # ✅ added for fraud detection


class TransactionCreateView(generics.CreateAPIView):
    """
    Handle new money transfer transactions.
    Automatically flags high-value transactions as potential fraud.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Get the sender account from the authenticated user
        sender_account = self.request.user.accounts.first()
        transaction = serializer.save(sender=sender_account)

        # --- Fraud Detection Logic ---
        amount = transaction.amount
        if amount > 50000:  # You can adjust this threshold later
            FraudAlert.objects.create(
                transaction=transaction,
                reason=f"High-value transaction detected: ₹{amount}"
            )


class TransactionListView(generics.ListAPIView):
    """
    List all transactions related to the authenticated user.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(sender__user=user) | Transaction.objects.filter(receiver__user=user)
