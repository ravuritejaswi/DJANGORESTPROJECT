from django.contrib import admin

from .models import (
    Category,
    Provider,
    ProviderProfile,
    Service,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
    )


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "user__email",
    )


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "provider",
        "phone_number",
        "rating",
        "created_at",
    )

    search_fields = (
        "provider__name",
        "phone_number",
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "status",
        "category",
        "provider",
        "created_at",
    )

    list_filter = (
        "status",
        "category",
    )

    search_fields = (
        "name",
        "description",
        "provider__name",
    )

# Register your models here.
