from decimal import Decimal


def calculate_fare(
    base_fare,
    distance_charge=0,
    time_charge=0,
    surge_charge=0,
):
    base_fare = Decimal(str(base_fare))
    distance_charge = Decimal(str(distance_charge))
    time_charge = Decimal(str(time_charge))
    surge_charge = Decimal(str(surge_charge))

    return base_fare + distance_charge + time_charge + surge_charge


def get_ride_fare():
    base_fare = Decimal("40")
    distance_charge = Decimal("80")
    time_charge = Decimal("20")
    surge_charge = Decimal("10")

    total = calculate_fare(
        base_fare,
        distance_charge,
        time_charge,
        surge_charge,
    )

    return {
        "base_fare": base_fare,
        "distance_fare": distance_charge,
        "time_fare": time_charge,
        "surge": surge_charge,
        "total": total,
    }
