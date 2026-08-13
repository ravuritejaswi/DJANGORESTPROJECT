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