from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.audit.services import AuditService
from apps.accounts.models import Account

User = get_user_model()

class AuditLoggingTests(TestCase):
    def setUp(self):
        # ✅ Create a real user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # ✅ Optional: create an account tied to the user
        self.account = Account.objects.create(user=self.user, balance=1000.00)

    def test_log_transaction_event(self):
        AuditService.log_event(
            user=self.user,
            action="Transaction",
            details="Test transaction"
        )
        self.assertEqual(AuditService.get_all_logs().count(), 1)

    def test_multiple_logs_created(self):
        AuditService.log_event(user=self.user, action="Deposit", details="Deposited 1000.00")
        AuditService.log_event(user=self.user, action="Withdraw", details="Withdrew 500.00")
        self.assertEqual(AuditService.get_all_logs().count(), 2)

    def test_audit_log_details_correct(self):
        AuditService.log_event(user=self.user, action="Login", details="User logged in")
        log = AuditService.get_all_logs().first()
        self.assertEqual(log.action, "Login")
        self.assertEqual(log.details, "User logged in")
