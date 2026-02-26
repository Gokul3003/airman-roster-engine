from datetime import datetime
from collections import defaultdict

from app.database import SessionLocal
from app.models import Student, TimeSlot, Instructor
from app.weather import get_weather
from app.weather_rules import evaluate_weather
from app.instructor_engine import assign_instructor


DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday"
]


def generate_weekly_roster():
    db = SessionLocal()

    students = db.query(Student).all()
    slots = db.query(TimeSlot).all()
    instructors = db.query(Instructor).all()

    # Track weekly student assignments
    student_weekly_count = {
        student.student_id: 0
        for student in students
    }

    # Track instructor duty hours per day
    instructor_daily_load = defaultdict(lambda: defaultdict(float))

    # Prevent instructor double booking in same slot
    instructor_slot_bookings = set()

    assignments = []

    for day in DAYS:
        for slot in slots:

            # Sort by priority (1 = highest)
            students_sorted = sorted(students, key=lambda s: s.priority)

            for student in students_sorted:

                # 1️⃣ Weekly quota check
                if student_weekly_count[student.student_id] >= student.required_sorties_per_week:
                    continue

                # 2️⃣ Student availability check
                available = False
                for entry in student.availability:
                    if (
                        entry["day"].lower() == day.lower()
                        and entry["slot_id"] == slot.slot_id
                    ):
                        available = True
                        break

                if not available:
                    continue

                # 3️⃣ Determine sortie type
                if student.preferred_sortie_types:
                    sortie_type = student.preferred_sortie_types[0]
                else:
                    sortie_type = "CIRCUITS"

                # 4️⃣ Assign instructor
                instructor = assign_instructor(
                    instructors=instructors,
                    student=student,
                    sortie_type=sortie_type,
                    day=day,
                    slot=slot,
                    instructor_daily_load=instructor_daily_load,
                    instructor_slot_bookings=instructor_slot_bookings
                )

                if not instructor:
                    continue  # No instructor available

                # 5️⃣ Get weather
                weather = get_weather("VOBG", slot.start, slot.end)

                # 6️⃣ Evaluate weather
                decision = evaluate_weather(
                    stage=student.stage,
                    sortie_type=sortie_type,
                    weather_data=weather
                )

                # 7️⃣ Create assignment
                assignment = {
                    "day": day,
                    "slot_id": slot.slot_id,
                    "slot_label": slot.label,
                    "student_id": student.student_id,
                    "student_name": student.name,
                    "stage": student.stage,
                    "sortie_type": sortie_type,
                    "instructor_id": instructor.instructor_id,
                    "instructor_name": instructor.name,
                    "dispatch_decision": decision["dispatch_decision"],
                    "rule_chunk": decision["rule_chunk"],
                    "weather_confidence": weather["confidence"]
                }

                assignments.append(assignment)

                # Update student weekly count
                student_weekly_count[student.student_id] += 1

                # Move to next slot
                break

    db.close()

    return {
        "generated_at": datetime.utcnow(),
        "total_assignments": len(assignments),
        "student_weekly_summary": student_weekly_count,
        "assignments": assignments
    }