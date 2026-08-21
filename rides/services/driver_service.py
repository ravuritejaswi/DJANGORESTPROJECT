def make_driver_available(driver):
    if driver:
        driver.is_available = True
        driver.save(update_fields=["is_available"])

from django.core.cache import cache


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
