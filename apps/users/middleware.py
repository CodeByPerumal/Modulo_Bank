import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Attach authenticated user from JWT cookie to every request.
    """

    def process_request(self, request):
        token = request.COOKIES.get('access')
        if not token:
            return  # No token in cookies → skip

        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            request.user = user
        except Exception:
            # Invalid or expired token
            request.user = None
