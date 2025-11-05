from django.urls import path
from .views import (
    TransactionCreateView,
    TransactionListView,
    DepositView,
    WithdrawView,
    TransactionDashboardView,
    TransactionListCreateView
)
urlpatterns = [
    path('transfer/', TransactionCreateView.as_view(), name='transfer-create'),
    path('list/', TransactionListView.as_view(), name='transaction-list'),
    path('deposit/', DepositView.as_view(), name='transaction-deposit'),
    path('withdraw/', WithdrawView.as_view(), name='transaction-withdraw'),
    path('dashboard/', TransactionDashboardView.as_view(), name='transaction-dashboard'),
    path("dashboard/view/", TransactionDashboardView.as_view(), name="dashboard-api"),
    path('', TransactionListCreateView.as_view(), name='transaction-list-create'),

]


