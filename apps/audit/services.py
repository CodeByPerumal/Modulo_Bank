# apps/audit/services.py
from apps.audit.models import AuditLog

class AuditService:
    @staticmethod
    def log_event(user=None, action="", details="", method="SYSTEM", endpoint="/system/", ip_address=None):
        """
        Log an audit event into the AuditLog table.
        """
        AuditLog.objects.create(
            user=user,
            action=action,
            method=method,
            endpoint=endpoint,
            ip_address=ip_address,
            details=details,
        )

    @staticmethod
    def get_all_logs():
        """
        Retrieve all audit logs (used for testing and admin purposes).
        """
        return AuditLog.objects.all()
