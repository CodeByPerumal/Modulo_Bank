from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from apps.accounts.models import Account
import uuid

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.sender.account_number} → {self.receiver.account_number} ({self.amount})"
