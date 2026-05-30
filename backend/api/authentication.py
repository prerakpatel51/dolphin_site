from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication


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
            # Use DRF's built-in CSRF validation
            SessionAuthentication().enforce_csrf(request)

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
