from rest_framework import generics, permissions
from apps.accounts.models import Account
from apps.accounts.serializers import AccountSerializer, AccountCreateSerializer

class AccountCreateView(generics.CreateAPIView):
    serializer_class = AccountCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AccountListView(generics.ListAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
