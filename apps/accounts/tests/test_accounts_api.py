from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import Account

User = get_user_model()


class AccountAPITests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="customer1",
            email="cust1@example.com",
            password="testpass123",
            role="customer"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_account_success(self):
        """
        ✅ User should be able to create an account with valid data.
        """
        url = reverse('create-account')
        data = {
            "account_type": "SAVINGS",
            "balance": 500.00
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Account.objects.filter(user=self.user).exists())

    def test_create_account_minimum_balance_fail(self):
        """
        🚫 Should fail if initial deposit < 100.
        """
        url = reverse('create-account')
        data = {
            "account_type": "SAVINGS",
            "balance": 50.00
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Minimum initial deposit", str(response.data))

    def test_list_user_accounts(self):
        """
        ✅ User should be able to view their own accounts.
        """
        # Create one account for this user
        Account.objects.create(
            user=self.user,
            account_number="SA123456789",
            account_type="SAVINGS",
            balance=1000.00
        )

        url = reverse('list-accounts')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['account_type'], 'SAVINGS')
