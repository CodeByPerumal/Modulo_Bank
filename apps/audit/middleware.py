# apps/audit/middleware.py
from apps.audit.models import AuditLog

class AuditLogMiddleware:
    """
    Logs key user actions for auditing purposes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Capture method and path before the view runs
        response = self.get_response(request)

        # Only log write actions after view executes successfully
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and response.status_code < 500:
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            ip = self.get_client_ip(request)
            action = f"{request.method} {request.path}"

            AuditLog.objects.create(
                user=user,
                action=action,
                method=request.method,
                endpoint=request.path,
                ip_address=ip,
            )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
