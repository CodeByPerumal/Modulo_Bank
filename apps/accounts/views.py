from rest_framework import generics, permissions
from apps.accounts.models import Account
from apps.accounts.serializers import AccountSerializer, AccountCreateSerializer
from apps.users.permissions import IsAdmin, IsCustomer


class AccountCreateView(generics.CreateAPIView):
    """
    Allow customers to open a new account.
    """
    serializer_class = AccountCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

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

class AccountDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single account by ID.
    Customers can view their own account only.
    Admins can view any account.
    """
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Account.objects.all()
        return Account.objects.filter(user=user)


from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from apps.accounts.models import Account
from apps.accounts.serializers import AccountSerializer
from apps.users.permissions import IsAdmin, IsCustomer


class AccountBalanceView(APIView):
    """
    Returns account balance(s) for the authenticated user.
    Admins can view all balances.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == 'admin':
            accounts = Account.objects.all().values('id', 'user__username', 'balance')
        else:
            accounts = Account.objects.filter(user=user).values('id', 'account_type', 'balance')

        return Response({"accounts": list(accounts)})