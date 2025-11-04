from rest_framework import serializers
from django.db import transaction as db_transaction
from apps.accounts.models import Account
from apps.transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'sender', 'receiver', 'amount', 'status', 'timestamp', 'description']
        read_only_fields = ['id', 'status', 'timestamp']

    def validate(self, attrs):
        sender = attrs['sender']
        receiver = attrs['receiver']
        amount = attrs['amount']
        user = self.context['request'].user

        if sender.user != user:
            raise serializers.ValidationError("You can only transfer from your own account.")
        if sender == receiver:
            raise serializers.ValidationError("Sender and receiver accounts cannot be the same.")
        if amount <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        if sender.balance < amount:
            raise serializers.ValidationError("Insufficient balance in sender account.")

        return attrs

    def create(self, validated_data):
        sender = validated_data['sender']
        receiver = validated_data['receiver']
        amount = validated_data['amount']

        with db_transaction.atomic():
            sender.balance -= amount
            sender.save()

            receiver.balance += amount
            receiver.save()

            validated_data['status'] = 'SUCCESS'
            transaction_obj = Transaction.objects.create(**validated_data)

        return transaction_obj
