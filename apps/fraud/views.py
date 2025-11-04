from rest_framework import generics, permissions
from apps.fraud.models import FraudAlert
from apps.fraud.serializers import FraudAlertSerializer

class FraudAlertListView(generics.ListAPIView):
    """
    List all fraud alerts (admin only)
    """
    queryset = FraudAlert.objects.all().order_by('-flagged_at')
    serializer_class = FraudAlertSerializer
    permission_classes = [permissions.IsAdminUser]

# apps/fraud/views.py
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.generics import ListAPIView
from apps.fraud.models import FraudAlert
from apps.fraud.serializers import FraudAlertSerializer

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"

class FraudAlertListView(ListAPIView):
    queryset = FraudAlert.objects.all().order_by('-flagged_at')
    serializer_class = FraudAlertSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

