from django.urls import path
from apps.accounts.views import AccountCreateView, AccountListView, AccountDetailView, AccountBalanceView

urlpatterns = [
    path('create/', AccountCreateView.as_view(), name='create-account'),
    path('', AccountListView.as_view(), name='list-accounts'),
    path("<uuid:pk>/", AccountDetailView.as_view(), name="account-detail"),
    path('balances/', AccountBalanceView.as_view(), name='account-balances'),
]
