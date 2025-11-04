from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.transactions.models import Transaction


class AccountService:
    @staticmethod
    @transaction.atomic
    def deposit(account, amount: Decimal):
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive.")
        
        account.balance += amount
        account.save()

        Transaction.objects.create(
            sender=None,
            receiver=account,
            amount=amount,
            status='SUCCESS',
            description=f"Deposit of {amount} to account {account.account_number}",
            transaction_type="DEPOSIT"
        )
        return account

    @staticmethod
    @transaction.atomic
    def withdraw(account, amount: Decimal):
        if amount <= 0:
            raise ValidationError("Withdrawal amount must be positive.")
        if account.balance < amount:
            raise ValidationError("Insufficient balance.")

        account.balance -= amount
        account.save()

        Transaction.objects.create(
            sender=account,
            receiver=None,
            amount=amount,
            status='SUCCESS',
            description=f"Withdrawal of {amount} from account {account.account_number}",
            transaction_type="WITHDRAWAL"
        )
        return account

    @staticmethod
    @transaction.atomic
    def transfer(from_account, to_account, amount: Decimal):
        if amount <= 0:
            raise ValidationError("Transfer amount must be positive.")
        if from_account.balance < amount:
            raise ValidationError("Insufficient balance for transfer.")
        if from_account == to_account:
            raise ValidationError("Cannot transfer to the same account.")

        # Update balances
        from_account.balance -= amount
        to_account.balance += amount
        from_account.save()
        to_account.save()

        Transaction.objects.create(
            sender=from_account,
            receiver=to_account,
            amount=amount,
            status='SUCCESS',
            description=f"Transfer of {amount} from {from_account.account_number} to {to_account.account_number}",
            transaction_type="TRANSFER_OUT"
        )

        return from_account, to_account
