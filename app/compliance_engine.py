from collections import defaultdict


def validate_operational_compliance(assignments, instructors, aircraft_list, students):

    violations = []
    instructor_daily_hours = defaultdict(lambda: defaultdict(float))
    aircraft_usage = defaultdict(set)
    instructor_total_hours = defaultdict(float)
    aircraft_total_slots = defaultdict(int)
    student_go_count = defaultdict(int)

    total_go = 0
    total_sessions = 0

    aircraft_lookup = {ac.aircraft_id: ac for ac in aircraft_list}

    for assignment in assignments:

        day = assignment["day"]
        slot_id = assignment["slot_id"]
        instructor_id = assignment["instructor_id"]
        aircraft_id = assignment["aircraft_id"]
        decision = assignment["dispatch_decision"]
        activity = assignment["activity"]
        student_id = assignment["student_id"]

        total_sessions += 1

        # ✅ Only count actual completed sessions
        if decision == "GO":
            total_go += 1
            student_go_count[student_id] += 1

        # Instructor duty hours
        instructor_daily_hours[instructor_id][day] += 2.5
        instructor_total_hours[instructor_id] += 2.5

        # Aircraft double booking check (only for FLIGHT)
        if activity == "FLIGHT":
            if (day, slot_id) in aircraft_usage[aircraft_id]:
                violations.append({
                    "type": "AIRCRAFT_DOUBLE_BOOKED",
                    "details": f"{aircraft_id} double booked on {day} {slot_id}",
                    "severity": "CRITICAL"
                })
            else:
                aircraft_usage[aircraft_id].add((day, slot_id))

            aircraft_total_slots[aircraft_id] += 1

            # Only validate aircraft maintenance for FLIGHT activity
            if activity == "FLIGHT" and aircraft_id:

                if aircraft_id not in aircraft_lookup:
                    violations.append({
                        "type": "INVALID_AIRCRAFT",
                        "aircraft_id": aircraft_id,
                        "severity": "CRITICAL"
                    })

                elif aircraft_lookup[aircraft_id].maintenance_status != "serviceable":
                    violations.append({
                        "type": "AIRCRAFT_UNSERVICEABLE",
                        "aircraft_id": aircraft_id,
                        "severity": "CRITICAL"
                    })

    # Instructor duty limit validation
    for instructor in instructors:
        iid = instructor.instructor_id
        max_hours = instructor.max_duty_hours_per_day

        for day, hours in instructor_daily_hours[iid].items():
            if hours > max_hours:
                violations.append({
                    "type": "INSTRUCTOR_OVERDUTY",
                    "details": f"{iid} exceeded duty hours on {day}",
                    "severity": "CRITICAL"
                })

    # Metrics
    go_success_rate = round(
        (total_go / total_sessions) * 100, 2
    ) if total_sessions else 0

    critical = [v for v in violations if v["severity"] == "CRITICAL"]

    if critical:
        system_status = "VIOLATION"
    else:
        system_status = "VALID"

    return {
        "system_status": system_status,
        "summary_metrics": {
            "total_sessions": total_sessions,
            "total_completed_sessions": total_go,
            "success_rate_percent": go_success_rate
        },
        "violations": violations
    }