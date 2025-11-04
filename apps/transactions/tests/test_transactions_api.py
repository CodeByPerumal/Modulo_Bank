from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import Account
from apps.transactions.models import Transaction

User = get_user_model()

class TransactionTests(APITestCase):
    def setUp(self):
        # Create two users with accounts
        self.user1 = User.objects.create_user(username="alice", email="alice@example.com", password="testpass")
        self.user2 = User.objects.create_user(username="bob", email="bob@example.com", password="testpass")

        self.account1 = Account.objects.create(user=self.user1, account_type="SAVINGS", balance=10000)
        self.account2 = Account.objects.create(user=self.user2, account_type="SAVINGS", balance=5000)

        self.client.force_authenticate(user=self.user1)

    def test_successful_transfer(self):
        """✅ User should be able to transfer money to another account."""
        url = reverse('transfer-create')
        data = {
            "receiver": str(self.account2.id),
            "amount": 1000.00,
            "description": "Rent payment"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(float(self.account1.balance), 9000.00)
        self.assertEqual(float(self.account2.balance), 6000.00)

    def test_insufficient_balance(self):
        """🚫 Should fail if sender doesn't have enough balance."""
        url = reverse('transfer-create')
        data = {
            "receiver": str(self.account2.id),
            "amount": 20000.00,
            "description": "Big purchase"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_cannot_transfer_to_self(self):
        """🚫 Should fail if sender and receiver are same."""
        url = reverse('transfer-create')
        data = {
            "receiver": str(self.account1.id),
            "amount": 100,
            "description": "Invalid transfer"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_list_transactions(self):
        """✅ User should see their own sent and received transactions."""
        # Create one outgoing and one incoming transaction
        Transaction.objects.create(sender=self.account1, receiver=self.account2, amount=500, status='SUCCESS')
        Transaction.objects.create(sender=self.account2, receiver=self.account1, amount=300, status='SUCCESS')

        url = reverse('transaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
