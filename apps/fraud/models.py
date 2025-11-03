import uuid
from django.db import models
from apps.transactions.models import Transaction

class FraudAlert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='fraud_alert')
    reason = models.CharField(max_length=255)
    flagged_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"Fraud Alert - {self.transaction.id} ({self.reason})"
