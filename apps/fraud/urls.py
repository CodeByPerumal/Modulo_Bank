from django.urls import path
from .views import FraudAlertListView

urlpatterns = [
    path('alerts/', FraudAlertListView.as_view(), name='fraud-alerts'),
]
