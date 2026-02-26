def assign_aircraft(
    aircraft_list,
    day,
    slot,
    aircraft_daily_usage,
    aircraft_slot_bookings
):
    """
    Returns aircraft object if eligible.
    """

    for aircraft in aircraft_list:

        # 1️⃣ Must be serviceable
        if aircraft.maintenance_status.lower() != "serviceable":
            continue

        # 2️⃣ Availability check
        available = False
        for entry in aircraft.availability:
            if (
                entry["day"].lower() == day.lower()
                and entry["slot_id"] == slot.slot_id
            ):
                available = True
                break

        if not available:
            continue

        # 3️⃣ Prevent double booking
        if (aircraft.aircraft_id, day, slot.slot_id) in aircraft_slot_bookings:
            continue

        # Passed all checks → assign
        aircraft_daily_usage[aircraft.aircraft_id][day] += 1

        aircraft_slot_bookings.add(
            (aircraft.aircraft_id, day, slot.slot_id)
        )

        return aircraft

    return None