from rest_framework import serializers
from django.db import transaction as db_transaction
from apps.accounts.models import Account
from apps.transactions.models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    from_account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(), write_only=True
    )
    to_account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(), write_only=True
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "from_account",
            "to_account",
            "amount",
            "description",
            "status",
            "timestamp",
        ]
        read_only_fields = ["id", "status", "timestamp"]

    def validate(self, attrs):
        from_account = attrs.get("from_account")
        to_account = attrs.get("to_account")
        amount = attrs.get("amount")

        if from_account == to_account:
            raise serializers.ValidationError("Cannot transfer to the same account.")

        if amount <= 0:
            raise serializers.ValidationError("Transfer amount must be greater than zero.")

        if from_account.balance < amount:
            raise serializers.ValidationError("Insufficient balance in the sender account.")

        return attrs

    def create(self, validated_data):
        from_account = validated_data.pop("from_account")
        to_account = validated_data.pop("to_account")
        amount = validated_data["amount"]

        with db_transaction.atomic():
            from_account.balance -= amount
            from_account.save()

            to_account.balance += amount
            to_account.save()

            validated_data["sender"] = from_account
            validated_data["receiver"] = to_account
            validated_data["status"] = "SUCCESS"

            transaction_obj = Transaction.objects.create(**validated_data)

        return transaction_obj
