from rest_framework import generics, permissions
from apps.accounts.models import Account
from apps.accounts.serializers import AccountSerializer, AccountCreateSerializer
from apps.users.permissions import IsAdmin, IsCustomer


class AccountCreateView(generics.CreateAPIView):
    """
    Allow customers to open a new account.
    """
    serializer_class = AccountCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AccountListView(generics.ListAPIView):
    """
    Customers see their own accounts.
    Admins can view all accounts.
    """
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Account.objects.all()
        return Account.objects.filter(user=user)
