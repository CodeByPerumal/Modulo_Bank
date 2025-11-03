from rest_framework import serializers
from .models import Loan

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            'id',
            'user',
            'account',
            'loan_type',
            'principal_amount',
            'interest_rate',
            'tenure_months',
            'emi',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'emi', 'status', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        loan = Loan.objects.create(user=user, **validated_data)
        return loan

class LoanApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['id', 'status']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        new_status = validated_data.get('status')

        # If approved, credit loan amount to account
        if new_status == 'APPROVED' and instance.status == 'PENDING':
            account = instance.account
            account.balance += instance.principal_amount
            account.save()
            instance.status = 'APPROVED'
        elif new_status == 'REJECTED':
            instance.status = 'REJECTED'

        instance.save()
        return instance
