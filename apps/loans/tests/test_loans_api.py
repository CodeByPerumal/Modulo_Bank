from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import Account
from apps.loans.models import Loan

User = get_user_model()


class LoanAPITests(APITestCase):
    def setUp(self):
        # Create normal user and admin user
        self.user = User.objects.create_user(
            username="testuser", password="password123", email="user@example.com"
        )
        self.admin = User.objects.create_superuser(
            username="admin", password="adminpass", email="admin@example.com"
        )

        # Create an account for the user
        self.account = Account.objects.create(
            user=self.user,
            account_number="ACC12345",
            account_type="SAVINGS",
            balance=1000.00
        )

        # Namespaced URL patterns
        self.apply_url = reverse("loans:loan-apply")
        self.my_loans_url = reverse("loans:my-loans")
        self.all_loans_url = reverse("loans:all-loans")

    def test_user_can_apply_for_loan(self):
        """Ensure authenticated user can apply for a loan"""
        self.client.force_authenticate(self.user)

        data = {
            "account": self.account.id,
            "loan_type": "Home Loan",
            "principal_amount": 50000,
            "interest_rate": 8.5,
            "tenure_months": 12
        }
        response = self.client.post(self.apply_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loan.objects.count(), 1)
        self.assertEqual(Loan.objects.first().user, self.user)

    def test_non_admin_cannot_see_all_loans(self):
        """Regular users should not access admin loan list"""
        self.client.force_authenticate(self.user)
        response = self.client.get(self.all_loans_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_all_loans(self):
        """Admin should be able to see all loans"""
        self.client.force_authenticate(self.admin)

        # Create a loan for testing
        Loan.objects.create(
            user=self.user,
            account=self.account,
            loan_type="Personal Loan",
            principal_amount=20000,
            interest_rate=10.0,
            tenure_months=6
        )

        response = self.client.get(self.all_loans_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_admin_can_approve_loan(self):
        """Ensure admin can approve a pending loan and credit amount"""
        loan = Loan.objects.create(
            user=self.user,
            account=self.account,
            loan_type="Car Loan",
            principal_amount=10000,
            interest_rate=9.0,
            tenure_months=12,
            status="PENDING"
        )

        self.client.force_authenticate(self.admin)
        approve_url = reverse("loans:loan-approve", args=[loan.id])
        response = self.client.patch(approve_url, {"status": "APPROVED"})
        loan.refresh_from_db()
        self.account.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(loan.status, "APPROVED")
        self.assertGreater(self.account.balance, 1000.00)
