from rest_framework import serializers
from rides.models import DriverProfile


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = [
            "id",
            "user",
            "license_number",
            "is_available",
            "rating",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "rating", "created_at", "updated_at"]