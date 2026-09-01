from rest_framework.throttling import SimpleRateThrottle


class LoginThrottle(SimpleRateThrottle):
    scope = "login"

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class RegistrationThrottle(SimpleRateThrottle):
    scope = "registration"

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class PasswordResetThrottle(SimpleRateThrottle):
    scope = "password_reset"

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class OTPThrottle(SimpleRateThrottle):
    scope = "otp"

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class RideCreationThrottle(SimpleRateThrottle):
    scope = "ride_creation"

    def get_cache_key(self, request, view):
        return self.get_ident(request)