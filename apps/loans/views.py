from rest_framework import generics, permissions
from .models import Loan
from .serializers import LoanSerializer
from rest_framework import generics, permissions
from .models import Loan
from .serializers import LoanSerializer, LoanApprovalSerializer

class LoanApplyView(generics.CreateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

class MyLoansView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user)

class AllLoansView(generics.ListAPIView):
    queryset = Loan.objects.all().order_by('-created_at')
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAdminUser]

class LoanApprovalView(generics.UpdateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanApprovalSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'