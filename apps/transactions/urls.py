from django.urls import path
from .views import TransactionCreateView, TransactionListView

urlpatterns = [
    path('transfer/', TransactionCreateView.as_view(), name='transfer-create'),
    path('list/', TransactionListView.as_view(), name='transaction-list'),
]
