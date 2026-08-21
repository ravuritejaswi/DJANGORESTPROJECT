from rest_framework.permissions import BasePermission


class IsAdminOrDriver(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsRideOwnerOrDriver(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True

        if obj.driver and obj.driver.user == request.user:
            return True

        return False

class IsOwnDriverProfile(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
