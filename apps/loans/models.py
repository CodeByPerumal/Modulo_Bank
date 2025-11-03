import uuid
from django.db import models
from django.conf import settings
from apps.accounts.models import Account

class Loan(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=50)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.FloatField(help_text="Annual interest rate in %")
    tenure_months = models.PositiveIntegerField()
    emi = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_emi(self):
        P = float(self.principal_amount)
        r = float(self.interest_rate) / (12 * 100)
        n = self.tenure_months
        emi = (P * r * ((1 + r) ** n)) / (((1 + r) ** n) - 1)
        return round(emi, 2)

    def save(self, *args, **kwargs):
        if not self.emi:
            self.emi = self.calculate_emi()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.loan_type} - {self.user.username} - {self.status}"
