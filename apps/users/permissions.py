from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """Allow access only to Admin users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')

class IsCustomer(permissions.BasePermission):
    """Allow access only to Customer users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'customer')

class IsAuditor(permissions.BasePermission):
    """Allow access only to Auditor users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'auditor')

