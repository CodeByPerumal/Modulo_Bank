from django.urls import path
from .views import DashboardSummaryView, AdminDashboardView

urlpatterns = [
    path('dashboard/', DashboardSummaryView.as_view(), name='user-dashboard'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
]
