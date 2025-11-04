# from decimal import Decimal
# from django.utils import timezone
# from apps.fraud.models import FraudAlert

# class FraudDetectionService:
#     """
#     Handles detection and logging of potentially fraudulent transactions.
#     """

#     # @staticmethod
#     # def analyze_transaction(transaction):
#     #     """
#     #     Analyze a transaction for fraud patterns.
#     #     """
#     #     reasons = []

#     #     # Rule 1: Very high transaction amount
#     #     if transaction.amount > Decimal('100000'):
#     #         reasons.append("High-value transaction exceeds threshold")

#     #     # Rule 2: Self transfer (sender == receiver)
#     #     if transaction.sender == transaction.receiver:
#     #         reasons.append("Self transfer detected")

#     #     # Rule 3: Multiple rapid transactions (TODO: optional enhancement)
#     #     recent_transactions = transaction.sender.sent_transactions.filter(
#     #         timestamp__gte=timezone.now() - timezone.timedelta(minutes=1)
#     #     ).count()
#     #     if recent_transactions > 5:
#     #         reasons.append("Multiple transactions in a short period")

#     #     # If any rule triggered, create a FraudAlert
#     #     if reasons:
#     #         alert = FraudAlert.objects.create(
#     #             transaction=transaction,
#     #             reason=", ".join(reasons),
#     #             reviewed=False,
#     #         )
#     #         return alert

#     #     return None
#     def analyze_transaction(transaction):
#         if not transaction.sender:
#             # e.g., high deposit suspicious detection
#             if transaction.amount > 100000:
#                 FraudAlert.objects.create(
#                     transaction=transaction,
#                     reason=f"Unusually large deposit detected: ₹{transaction.amount}"
#                 )
#             return

# smart_Bank/apps/fraud/services.py
from datetime import timedelta
from django.utils import timezone
from .models import FraudAlert

class FraudDetectionService:
    @staticmethod
    def analyze_transaction(transaction):
        from apps.transactions.models import Transaction

        # ✅ Skip fraud detection for deposits or withdrawals
        if not transaction.sender:
            return

        # --- Rule 1: High-value transaction check ---
        if transaction.amount > 40000:
            FraudAlert.objects.create(
                transaction=transaction,
                reason=f"High-value transaction detected: ₹{transaction.amount}"
            )

        # --- Rule 2: Rapid multiple transfers ---
        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)

        recent_transactions = transaction.sender.sent_transactions.filter(
            timestamp__gte=one_hour_ago
        ).exclude(id=transaction.id)

        if recent_transactions.count() > 3:
            FraudAlert.objects.create(
                transaction=transaction,
                reason="Multiple rapid transfers from this account within the last hour."
            )
