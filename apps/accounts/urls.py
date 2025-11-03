from django.urls import path
from apps.accounts.views import AccountCreateView, AccountListView

urlpatterns = [
    path('create/', AccountCreateView.as_view(), name='create-account'),
    path('', AccountListView.as_view(), name='list-accounts'),
]
