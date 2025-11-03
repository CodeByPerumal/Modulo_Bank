from rest_framework import generics, permissions
from .models import FraudAlert
from .serializers import FraudAlertSerializer

class FraudAlertListView(generics.ListAPIView):
    queryset = FraudAlert.objects.all().order_by('-flagged_at')
    serializer_class = FraudAlertSerializer
    permission_classes = [permissions.IsAdminUser]
