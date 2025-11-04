# apps/loans/tests/test_loan_services.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.accounts.models import Account
from apps.loans.models import Loan
from apps.loans.services import LoanService

User = get_user_model()


class LoanServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.account = Account.objects.create(
            user=self.user,
            account_number="1234567890",
            balance=Decimal("5000.00"),
        )

    def test_create_loan_request(self):
        loan = LoanService.create_loan_request(
            user=self.user,
            account=self.account,
            principal_amount=Decimal("10000.00"),
            interest_rate=Decimal("10.0"),
            term_months=12,
            loan_type="Personal Loan",
        )
        self.assertEqual(loan.status, "PENDING")
        self.assertEqual(loan.principal_amount, Decimal("10000.00"))
        self.assertEqual(loan.remaining_balance, Decimal("10000.00"))
        self.assertEqual(loan.user, self.user)

    def test_approve_loan(self):
        loan = LoanService.create_loan_request(
            user=self.user,
            account=self.account,
            principal_amount=Decimal("5000.00"),
            interest_rate=Decimal("10.0"),
            term_months=6,
        )
        approved_loan = LoanService.approve_loan(loan)
        self.assertEqual(approved_loan.status, "APPROVED")
        self.assertEqual(self.account.balance, Decimal("10000.00"))

    def test_repayment_updates_balance(self):
        loan = LoanService.create_loan_request(
            user=self.user,
            account=self.account,
            principal_amount=Decimal("6000.00"),
            interest_rate=Decimal("10.0"),
            term_months=12,
        )
        LoanService.approve_loan(loan)
        updated_loan = LoanService.make_repayment(loan, Decimal("1000.00"))
        self.assertEqual(updated_loan.remaining_balance, Decimal("5000.00"))
        self.assertEqual(updated_loan.status, "APPROVED")

    def test_full_repayment_marks_loan_paid(self):
        loan = LoanService.create_loan_request(
            user=self.user,
            account=self.account,
            principal_amount=Decimal("4000.00"),
            interest_rate=Decimal("8.0"),
            term_months=6,
        )
        LoanService.approve_loan(loan)
        LoanService.make_repayment(loan, Decimal("4000.00"))
        loan.refresh_from_db()
        self.assertEqual(loan.remaining_balance, Decimal("0.00"))
        self.assertEqual(loan.status, "CLOSED")
