import math
from django.core.cache import cache
from rides.models import DriverLocation
from rides.utils.validators import validate_coordinates


def make_driver_available(driver):
    if driver:
        driver.is_available = True
        driver.save(update_fields=["is_available"])


def update_driver_location(driver, latitude, longitude):
    latitude, longitude = validate_coordinates(
        latitude,
        longitude,
    )

    location, created = DriverLocation.objects.update_or_create(
        driver=driver,
        defaults={
            "latitude": latitude,
            "longitude": longitude,
        },
    )

    return location, created


def get_nearby_drivers():
    cache_key = "nearby_drivers"

    # 1. Check cache
    drivers = cache.get(cache_key)

    if drivers is not None:
        print("CACHE HIT")
        return drivers

    # 2. Cache miss - get data
    print("CACHE MISS")

    drivers = [
        {
            "driver_id": 1,
            "name": "Driver 1",
            "latitude": 17.3850,
            "longitude": 78.4867,
        },
        {
            "driver_id": 2,
            "name": "Driver 2",
            "latitude": 17.4000,
            "longitude": 78.4800,
        },
    ]

    # 3. Store in Redis for 60 seconds
    cache.set(cache_key, drivers, timeout=60)

    return drivers


def invalidate_nearby_drivers_cache():
    cache_key = "nearby_drivers"

    # Remove old/stale cache
    cache.delete(cache_key)

    print("CACHE INVALIDATED")


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def find_nearby_drivers(latitude, longitude, radius):
    drivers = DriverLocation.objects.filter(
        availability_status="ONLINE",
        is_available=True,
    ).values(
        "driver_id",
        "latitude",
        "longitude",
    )

    nearby_drivers = []

    for driver in drivers:
        distance = calculate_distance(
            latitude,
            longitude,
            float(driver["latitude"]),
            float(driver["longitude"]),
        )

        if distance <= radius:
            nearby_drivers.append(
                {
                    "driver_id": str(driver["driver_id"]),
                    "distance_km": round(distance, 2),
                }
            )

    nearby_drivers.sort(key=lambda x: x["distance_km"])

    return nearby_drivers
