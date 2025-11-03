from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('SAVINGS', 'Savings'),
        ('CURRENT', 'Current'),
        ('FD', 'Fixed Deposit'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.account_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        # Auto-generate account number if not set
        if not self.account_number:
            prefix = self.account_type[:2].upper()
            self.account_number = f"{prefix}{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)
