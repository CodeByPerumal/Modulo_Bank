from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
import random

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
    # Ensure valid balance
        if self.balance < 0:
            raise ValueError("Account balance cannot be negative.")

        # Auto-generate a truly unique account number if missing
        if not self.account_number:
            self.account_number = self._generate_unique_account_number()

        super().save(*args, **kwargs)


    def _generate_unique_account_number(self):
        """Generate a unique 12-digit account number with prefix."""
        prefix = self.account_type[:2].upper() if self.account_type else "AC"
        while True:
            # Combine prefix + random 10-digit number
            number = f"{prefix}{random.randint(10**9, 10**10 - 1)}"
            if not Account.objects.filter(account_number=number).exists():
                return number