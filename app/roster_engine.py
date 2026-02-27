from datetime import datetime, timedelta
from collections import defaultdict

from app.database import SessionLocal
from app.models import Student, TimeSlot, Instructor, Aircraft, Simulator
from app.weather import get_weather
from app.weather_rules import evaluate_weather
from app.instructor_engine import assign_instructor
from app.aircraft_engine import assign_aircraft
from app.compliance_engine import validate_operational_compliance


DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def generate_weekly_roster():

    db = SessionLocal()

    students = db.query(Student).all()
    slots = db.query(TimeSlot).all()
    instructors = db.query(Instructor).all()
    aircraft_list = db.query(Aircraft).all()
    simulators = db.query(Simulator).all()

    week_start = datetime.utcnow().date()

    # ----------------------------
    # TRACKING STRUCTURES
    # ----------------------------

    student_weekly_count = {s.student_id: 0 for s in students}
    student_daily_count = defaultdict(lambda: defaultdict(int))

    instructor_daily_load = defaultdict(lambda: defaultdict(float))
    instructor_slot_bookings = set()

    aircraft_slot_bookings = set()
    simulator_slot_bookings = set()

    roster_output = []

    # Build empty 7-day structure
    for day_index in range(7):
        roster_output.append({
            "date": str(week_start + timedelta(days=day_index)),
            "slots": []
        })

    compliance_assignments = []

    # ------------------------------------
    # STUDENT-CENTRIC PRIORITY LOOP
    # ------------------------------------

    for student in sorted(students, key=lambda s: s.priority):

        sorties_needed = student.required_sorties_per_week

        for day_index, day in enumerate(DAYS):

            if sorties_needed <= 0:
                break

            for slot in slots:

                if sorties_needed <= 0:
                    break

                # Daily cap (max 1 per day)
                if student_daily_count[student.student_id][day] >= 1:
                    continue

                # Student availability
                if not any(
                    entry["day"].lower() == day and entry["slot_id"] == slot.slot_id
                    for entry in student.availability
                ):
                    continue

                sortie_type = (
                    student.preferred_sortie_types[0]
                    if student.preferred_sortie_types
                    else "CIRCUITS"
                )

                # SOLO eligibility enforcement
                if sortie_type == "SOLO" and not student.solo_eligible:
                    continue

                # ---------------- Instructor ----------------

                instructor = assign_instructor(
                    instructors,
                    student,
                    sortie_type,
                    day,
                    slot,
                    instructor_daily_load,
                    instructor_slot_bookings
                )

                if not instructor:
                    continue

                # ---------------- Aircraft ----------------

                aircraft = assign_aircraft(
                    aircraft_list,
                    day,
                    slot,
                    defaultdict(lambda: defaultdict(int)),
                    aircraft_slot_bookings
                )

                if not aircraft:
                    continue

                # ---------------- Weather ----------------

                weather = get_weather("VOBG", slot.start, slot.end)

                decision = evaluate_weather(
                    student.stage,
                    sortie_type,
                    weather
                )

                dispatch_decision = decision["dispatch_decision"]
                activity = "FLIGHT"
                resource_id = aircraft.aircraft_id
                reasons = ["NORMAL_OPERATION"]

                # SIM substitution under NO_GO
                if dispatch_decision == "NO_GO":

                    sim_assigned = None

                    for sim in simulators:
                        if any(
                            entry["day"].lower() == day and entry["slot_id"] == slot.slot_id
                            for entry in sim.availability
                        ):
                            if (sim.simulator_id, day, slot.slot_id) not in simulator_slot_bookings:
                                sim_assigned = sim
                                break

                    if sim_assigned:
                        activity = "SIM"
                        resource_id = sim_assigned.simulator_id
                        simulator_slot_bookings.add(
                            (sim_assigned.simulator_id, day, slot.slot_id)
                        )
                        reasons = ["WX_BELOW_MINIMA", "SIM_SUBSTITUTION"]
                    else:
                        # No SIM available → skip
                        continue

                assignment = {
                    "slot_id": slot.slot_id,
                    "date": roster_output[day_index]["date"],   # 🔥 important for reallocation
                    "start": slot.start,
                    "end": slot.end,
                    "activity": activity,
                    "student_id": student.student_id,
                    "instructor_id": instructor.instructor_id,
                    "resource_id": resource_id,
                    "sortie_type": sortie_type,
                    "stage": student.stage,  # 🔥 needed for weather re-evaluation
                    "dispatch_decision": dispatch_decision,
                    "reasons": reasons,
                    "citations": [
                        f"rules:weather_minima#{decision['rule_chunk']}"
                    ]
                }

                roster_output[day_index]["slots"].append(assignment)

                compliance_assignments.append({
                    "day": day,
                    "slot_id": slot.slot_id,
                    "student_id": student.student_id,
                    "instructor_id": instructor.instructor_id,
                    "aircraft_id": aircraft.aircraft_id,
                    "dispatch_decision": dispatch_decision,
                    "activity": activity
                })

                # Update counters
                student_weekly_count[student.student_id] += 1
                student_daily_count[student.student_id][day] += 1
                sorties_needed -= 1

                break  # Move to next day

    # ------------------------------------
    # Compliance Validation
    # ------------------------------------

    compliance_report = validate_operational_compliance(
        compliance_assignments,
        instructors,
        aircraft_list,
        students
    )

    db.close()

    return {
        "week_start": str(week_start),
        "base_icao": "VOBG",
        "roster": roster_output,
        "unassigned": [],
        "compliance_report": compliance_report
    }