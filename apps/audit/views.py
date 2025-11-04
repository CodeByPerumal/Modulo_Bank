from rest_framework import generics, permissions
from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission: only admin users can access audit logs.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", "") == "admin"


class AuditLogListView(generics.ListAPIView):
    """
    ✅ Admin-only endpoint to view audit logs.
    GET /api/audit/
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]
