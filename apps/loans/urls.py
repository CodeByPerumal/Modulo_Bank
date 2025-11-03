from django.urls import path
from .views import LoanApplyView, MyLoansView, AllLoansView, LoanApprovalView

urlpatterns = [
    path('apply/', LoanApplyView.as_view(), name='loan-apply'),
    path('myloans/', MyLoansView.as_view(), name='my-loans'),
    path('all/', AllLoansView.as_view(), name='all-loans'),
    path('approve/<uuid:id>/', LoanApprovalView.as_view(), name='loan-approve'),
]
