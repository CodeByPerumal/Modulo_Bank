# apps/fraud/urls.py
from django.urls import path
from apps.fraud.views import FraudAlertListView

urlpatterns = [
    path('alerts/', FraudAlertListView.as_view(), name='fraud-alert-list'),
]
