from rest_framework import serializers
from .models import FraudAlert

class FraudAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudAlert
        fields = '__all__'
