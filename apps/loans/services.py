# apps/loans/services.py

from django.db import transaction
from decimal import Decimal
from apps.loans.models import Loan


class LoanService:
    @staticmethod
    @transaction.atomic
    def create_loan_request(user, account, principal_amount, interest_rate, term_months, loan_type="Personal Loan"):
        """
        Creates a new loan request for the given user and account.
        """
        loan = Loan.objects.create(
            user=user,
            account=account,
            loan_type=loan_type,
            principal_amount=Decimal(principal_amount),
            interest_rate=Decimal(interest_rate),
            term_months=term_months,
            remaining_balance=Decimal(principal_amount),
            status="PENDING",
        )
        return loan

    @staticmethod
    @transaction.atomic
    def approve_loan(loan):
        """
        Approves the loan and credits the principal amount to the user's account.
        """
        account = loan.account
        account.balance += loan.principal_amount
        account.save()

        loan.status = "APPROVED"
        loan.remaining_balance = loan.principal_amount
        loan.save()

        return loan

    @staticmethod
    @transaction.atomic
    def make_repayment(loan, amount):
        """
        Handles repayment logic and updates remaining balance.
        """
        loan.remaining_balance -= Decimal(amount)
        if loan.remaining_balance <= 0:
            loan.remaining_balance = Decimal("0.00")
            loan.status = "CLOSED"
        loan.save()
        return loan
