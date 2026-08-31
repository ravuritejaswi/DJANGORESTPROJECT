from rest_framework.exceptions import ValidationError


def validate_coordinates(latitude, longitude):
    if latitude is None or longitude is None:
        raise ValidationError("latitude and longitude are required.")

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        raise ValidationError("latitude and longitude must be valid numbers.")

    if latitude < -90 or latitude > 90:
        raise ValidationError("Invalid latitude.")

    if longitude < -180 or longitude > 180:
        raise ValidationError("Invalid longitude.")

    return latitude, longitude
