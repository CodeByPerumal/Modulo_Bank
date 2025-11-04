from django.test import TestCase
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.accounts.models import Account
from apps.transactions.models import Transaction
from apps.fraud.models import FraudAlert
from apps.fraud.services import FraudDetectionService

User = get_user_model()

class FraudDetectionServiceTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")
        self.acc1 = Account.objects.create(user=self.user1, balance=Decimal("500000"))
        self.acc2 = Account.objects.create(user=self.user2, balance=Decimal("100000"))

    def test_high_value_transaction_flags_fraud(self):
        txn = Transaction.objects.create(
            sender=self.acc1,
            receiver=self.acc2,
            amount=Decimal("200000"),
            transaction_type="TRANSFER_OUT",
            status="SUCCESS"
        )
        alert = FraudAlert.objects.first()
        self.assertIsNotNone(alert)
        self.assertIn("High-value transaction", alert.reason)

    def test_self_transfer_flags_fraud(self):
        txn = Transaction.objects.create(
            sender=self.acc1,
            receiver=self.acc1,
            amount=Decimal("1000"),
            transaction_type="TRANSFER_OUT",
            status="SUCCESS"
        )
        alert = FraudAlert.objects.first()
        self.assertIsNotNone(alert)
        self.assertIn("Self transfer", alert.reason)

    def test_normal_transaction_not_flagged(self):
        txn = Transaction.objects.create(
            sender=self.acc1,
            receiver=self.acc2,
            amount=Decimal("500"),
            transaction_type="TRANSFER_OUT",
            status="SUCCESS"
        )
        alert = FraudAlert.objects.first()
        self.assertIsNone(alert)
