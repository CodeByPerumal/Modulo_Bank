from django.db import models
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
    TRANSACTION_TYPES = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAWAL", "Withdrawal"),
        ("TRANSFER_IN", "Transfer In"),
        ("TRANSFER_OUT", "Transfer Out"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='sent_transactions',
        null=True, blank=True
    )
    receiver = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='received_transactions',
        null=True, blank=True
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    description = models.CharField(max_length=255, blank=True)
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPES, default="DEPOSIT"
    )

    def __str__(self):
        sender = self.sender.account_number if self.sender else "SYSTEM"
        receiver = self.receiver.account_number if self.receiver else "SYSTEM"
        return f"{sender} → {receiver} ({self.amount})"
