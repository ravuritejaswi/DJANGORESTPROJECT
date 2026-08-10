from django.contrib import admin

from .models import (
    DriverProfile,
    Vehicle,
    VehicleType,
    Ride,
    RideStatus,
)


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "license_number",
        "is_available",
        "rating",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "license_number",
    )

    list_filter = (
        "is_available",
    )

    ordering = (
        "-created_at",
    )


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "name",
    )


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle_number",
        "driver",
        "vehicle_type",
        "model",
        "color",
        "is_active",
        "created_at",
    )

    search_fields = (
        "vehicle_number",
        "model",
        "driver__user__email",
    )

    list_filter = (
        "vehicle_type",
        "is_active",
    )

    ordering = (
        "-created_at",
    )


@admin.register(RideStatus)
class RideStatusAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "created_at",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "name",
    )


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "driver",
        "vehicle",
        "status",
        "ride_type",
        "fare",
        "scheduled_at",
        "created_at",
    )

    search_fields = (
        "id",
        "user__username",
        "user__email",
        "driver__user__email",
        "vehicle__vehicle_number",
    )

    list_filter = (
        "ride_type",
        "status",
        "created_at",
    )

    ordering = (
        "-created_at",
    )
