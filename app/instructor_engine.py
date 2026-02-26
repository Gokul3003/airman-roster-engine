def assign_instructor(
    instructors,
    student,
    sortie_type,
    day,
    slot,
    instructor_daily_load,
    instructor_slot_bookings
):
    """
    Returns instructor object if eligible, else None.
    """

    for instructor in instructors:

        # 1️⃣ Must be current
        if not instructor.currency:
            continue

        # 2️⃣ Rating check (sortie-based)
        if sortie_type not in instructor.ratings:
            continue

        # 3️⃣ Availability check
        available = False
        for entry in instructor.availability:
            if (
                entry["day"].lower() == day.lower()
                and entry["slot_id"] == slot.slot_id
            ):
                available = True
                break

        if not available:
            continue

        # 4️⃣ Prevent double booking
        if (instructor.instructor_id, day, slot.slot_id) in instructor_slot_bookings:
            continue

        # 5️⃣ Max duty hours per day
        current_hours = instructor_daily_load[instructor.instructor_id][day]

        if current_hours + slot.duration_hours > instructor.max_duty_hours_per_day:
            continue

        # Passed all checks → assign
        instructor_daily_load[instructor.instructor_id][day] += slot.duration_hours

        instructor_slot_bookings.add(
            (instructor.instructor_id, day, slot.slot_id)
        )

        return instructor

    return None