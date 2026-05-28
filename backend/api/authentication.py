from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication


class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        return reason


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None

        # Enforce CSRF token validation for cookie-based authentication
        if request.method not in ("GET", "HEAD", "OPTIONS", "TRACE"):
            csrf_check = CSRFCheck(lambda req: None)
            csrf_check.process_request(request)
            reason = csrf_check.process_view(request, None, (), {})
            if reason:
                raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
