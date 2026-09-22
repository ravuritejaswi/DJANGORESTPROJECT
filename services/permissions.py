from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrProviderOwner(BasePermission):
    """
    Permissions:
    - Authenticated users can view services.
    - Admin users can manage all services.
    - Service providers can manage their own services.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.user.is_staff:
            return True

        try:
            request.user.provider
            return True
        except request.user.provider.RelatedObjectDoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_staff:
            return True

        try:
            return obj.provider.user == request.user
        except AttributeError:
            return False