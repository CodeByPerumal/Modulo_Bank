from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.users.models import User
from apps.audit.models import AuditLog


class AuditLogMiddlewareTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="john", password="pass123", role="customer")
        self.admin = User.objects.create_user(username="admin", password="admin123", role="admin")

    def test_audit_log_created_on_post(self):
        """
        ✅ When a POST is made to create an account, an AuditLog should be created.
        """
        self.client.force_authenticate(self.user)
        response = self.client.post("/api/v1/accounts/create/", {
            "account_type": "SAVINGS",
            "balance": 500
        }, format="json")

        # Must succeed
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # And an audit log should exist for this user
        self.assertTrue(
            AuditLog.objects.filter(user=self.user, method="POST").exists(),
            "Audit log not created for user POST request."
        )

    def test_admin_can_view_audit_logs(self):
        """
        ✅ Ensure admin can retrieve the audit log list endpoint.
        """
        AuditLog.objects.create(
            user=self.admin,
            action="Created Account",
            method="POST",
            endpoint="/api/v1/accounts/create/"
        )

        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/audit/")

        # Should return success (list of audit logs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
