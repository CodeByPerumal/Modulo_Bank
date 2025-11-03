# apps/audit/middleware.py
from apps.audit.models import AuditLog

class AuditLogMiddleware:
    """
    Custom middleware to log key user actions for auditing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Only log meaningful write actions
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            user = request.user if request.user.is_authenticated else None
            action = f"{request.method} {request.path}"
            ip = self.get_client_ip(request)

            AuditLog.objects.create(
                user=user,
                action=action,
                method=request.method,
                endpoint=request.path,
                ip_address=ip
            )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
