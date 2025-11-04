# apps/fraud/tests/test_fraud_api.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.users.models import User
from apps.accounts.models import Account
from apps.transactions.models import Transaction
from apps.fraud.models import FraudAlert


class FraudAlertTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass123", role="user")
        # self.admin = User.objects.create_user(username="admin1", password="admin123", role="admin")
        self.admin = User.objects.create_user(username="admin1", password="admin123", role="admin", is_staff=True, is_superuser=True)


        self.acc1 = Account.objects.create(user=self.user, account_type="SAVINGS", balance=100000)
        self.acc2 = Account.objects.create(user=self.user, account_type="CHECKING", balance=50000)

    def test_high_value_transaction_triggers_fraud(self):
        """
        Ensure a high-value transaction triggers a fraud alert.
        """
        Transaction.objects.create(sender=self.acc1, receiver=self.acc2, amount=60000)
        alerts = FraudAlert.objects.all()
        self.assertTrue(alerts.exists())

    def test_admin_can_view_fraud_alerts(self):
        """
        Ensure admin can retrieve fraud alerts via API.
        """
        transaction = Transaction.objects.create(sender=self.acc1, receiver=self.acc2, amount=60000)

        # Avoid duplicate creation — only create if not already existing
        FraudAlert.objects.get_or_create(transaction=transaction, defaults={"reason": "High-value test alert"})

        self.client.force_authenticate(self.admin)

        # Correct namespace: 'fraud' must be in your apps/fraud/urls.py include path in main urls.py
        url = reverse("fraud:fraud-alert-list")  # e.g., /api/fraud/alerts/

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
