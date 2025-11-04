# apps/fraud/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.transactions.models import Transaction
from apps.fraud.models import FraudAlert

@receiver(post_save, sender=Transaction)
def create_fraud_alert(sender, instance, created, **kwargs):
    if created and instance.amount > 50000:
        # Prevent duplicate alerts for the same transaction
        FraudAlert.objects.get_or_create(
            transaction=instance,
            defaults={"reviewed": False}  # only fields that exist in the model
        )
