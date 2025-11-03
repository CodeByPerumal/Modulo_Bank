from rest_framework import serializers
from apps.accounts.models import Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'account_number', 'account_type', 'balance', 'created_at']
        read_only_fields = ['id', 'account_number', 'created_at', 'balance']

class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'account_number', 'account_type', 'balance', 'created_at']
        read_only_fields = ['id', 'account_number', 'created_at']

    def validate_balance(self, value):
        if value < 100:
            raise serializers.ValidationError("Minimum initial deposit is 100.")
        return value

