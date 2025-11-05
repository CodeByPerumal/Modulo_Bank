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
