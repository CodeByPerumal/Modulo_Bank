from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.transactions.models import Transaction
from apps.fraud.services import FraudDetectionService

@receiver(post_save, sender=Transaction)
def detect_fraud_on_transaction(sender, instance, created, **kwargs):
    """
    Run fraud detection after a transaction is created.
    """
    if created:
        FraudDetectionService.analyze_transaction(instance)
