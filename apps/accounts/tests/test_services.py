from django.test import TestCase
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.accounts.models import Account
from apps.accounts.services import AccountService

User = get_user_model()

class AccountServiceTests(TestCase):
    def setUp(self):
        # Create users properly
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")

        # Create accounts linked to those users
        self.acc1 = Account.objects.create(user=self.user1, balance=Decimal('1000.00'))
        self.acc2 = Account.objects.create(user=self.user2, balance=Decimal('500.00'))

    def test_deposit_success(self):
        AccountService.deposit(self.acc1, Decimal('200.00'))
        self.acc1.refresh_from_db()
        self.assertEqual(self.acc1.balance, Decimal('1200.00'))

    def test_withdraw_success(self):
        AccountService.withdraw(self.acc1, Decimal('300.00'))
        self.acc1.refresh_from_db()
        self.assertEqual(self.acc1.balance, Decimal('700.00'))

    def test_withdraw_insufficient_balance(self):
        with self.assertRaises(Exception):
            AccountService.withdraw(self.acc2, Decimal('1000.00'))

    def test_transfer_success(self):
        AccountService.transfer(self.acc1, self.acc2, Decimal('400.00'))
        self.acc1.refresh_from_db()
        self.acc2.refresh_from_db()
        self.assertEqual(self.acc1.balance, Decimal('600.00'))
        self.assertEqual(self.acc2.balance, Decimal('900.00'))
