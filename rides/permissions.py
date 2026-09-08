from rest_framework.permissions import BasePermission


class IsAdminOrDriver(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_staff or user.is_superuser:
            return True

        from rides.models import DriverProfile

        return DriverProfile.objects.filter(user=user).exists()


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


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        return (
            user
            and user.is_authenticated
            and (user.is_staff or user.is_superuser)
        )


class IsAdminOrPassenger(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_staff or user.is_superuser:
            return True

        from rides.models import DriverProfile

        return not DriverProfile.objects.filter(user=user).exists()

class IsVehicleOwnerOrAdmin(BasePermission):
    """
    Allows access only to the driver who owns the vehicle
    or to an admin user.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_staff or user.is_superuser:
            return True

        if obj.driver and obj.driver.user == user:
            return True

        return False

class IsDriver(BasePermission):
    """
    Allows access only to authenticated users
    who have a DriverProfile.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        from rides.models import DriverProfile

        return DriverProfile.objects.filter(user=user).exists()

class IsVehicleOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin can manage any vehicle
        if user.is_staff or user.is_superuser:
            return True

        # Driver can manage only their own vehicle
        return obj.driver and obj.driver.user == user