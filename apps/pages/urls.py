from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('logout/', views.logout_page, name='logout'),
    path("accounts/", views.accounts_list_page, name="accounts-list"),
    path("accounts/create/", views.accounts_create_page, name="accounts-create"),
    path("transactions/", views.transactions_page, name="transactions-page"),
    path("loans/apply/", views.loan_apply_page, name="loan-apply"),
    path("loans/myloans/", views.my_loans_page, name="my-loans"),
    path('loans/approve/<uuid:loan_id>/', views.loan_approval_action, name='loan-approval-action'),
    path('audit/', views.audit_logs_page, name='audit-logs'),
    path('dashboard/admin/users/', views.admin_users_page, name='admin-user-list-page'),
    path("healthz/", views.health_check, name="health-check"),


]
