from collections import defaultdict


def validate_operational_compliance(assignments, instructors, aircraft_list, students):

    violations = []
    instructor_daily_hours = defaultdict(lambda: defaultdict(float))
    aircraft_usage = defaultdict(set)
    instructor_total_hours = defaultdict(float)
    aircraft_total_slots = defaultdict(int)
    student_go_count = defaultdict(int)

    total_go = 0
    total_no_go = 0

    # Lookup dictionaries
    aircraft_lookup = {ac.aircraft_id: ac for ac in aircraft_list}
    instructor_lookup = {ins.instructor_id: ins for ins in instructors}
    student_lookup = {stu.student_id: stu for stu in students}

    for assignment in assignments:

        day = assignment["day"]
        slot_id = assignment["slot_id"]
        instructor_id = assignment["instructor_id"]
        aircraft_id = assignment["aircraft_id"]
        decision = assignment["dispatch_decision"]
        student_id = assignment["student_id"]

        # GO / NO_GO tracking
        if decision == "GO":
            total_go += 1
            student_go_count[student_id] += 1
        else:
            total_no_go += 1
            violations.append({
                "type": "NO_GO_OPERATIONAL_ASSIGNMENT",
                "details": f"{student_id} scheduled despite NO_GO on {day} {slot_id}",
                "severity": "WARNING"
            })

        # Instructor duty hours
        instructor_daily_hours[instructor_id][day] += 2.5
        instructor_total_hours[instructor_id] += 2.5

        # Aircraft tracking
        if (day, slot_id) in aircraft_usage[aircraft_id]:
            violations.append({
                "type": "AIRCRAFT_DOUBLE_BOOKED",
                "details": f"{aircraft_id} double booked on {day} {slot_id}",
                "severity": "CRITICAL"
            })
        else:
            aircraft_usage[aircraft_id].add((day, slot_id))

        aircraft_total_slots[aircraft_id] += 1

        # Maintenance validation
        if aircraft_id in aircraft_lookup:
            if aircraft_lookup[aircraft_id].maintenance_status != "serviceable":
                violations.append({
                    "type": "AIRCRAFT_NOT_SERVICEABLE",
                    "details": f"{aircraft_id} assigned while under maintenance",
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

    # ----- UTILIZATION METRICS -----

    instructor_utilization = {}
    for instructor in instructors:
        iid = instructor.instructor_id
        max_weekly = instructor.max_duty_hours_per_day * 6  # assume 6-day week
        used = instructor_total_hours[iid]
        percent = round((used / max_weekly) * 100, 2) if max_weekly else 0
        instructor_utilization[iid] = percent

    aircraft_utilization = {}
    for aircraft in aircraft_list:
        aid = aircraft.aircraft_id
        total_possible_slots = 24  # assume 6 days * 4 slots
        used = aircraft_total_slots[aid]
        percent = round((used / total_possible_slots) * 100, 2)
        aircraft_utilization[aid] = percent

    student_completion = {}
    for student in students:
        sid = student.student_id
        required = student.required_sorties_per_week
        completed = student_go_count[sid]
        percent = round((completed / required) * 100, 2) if required else 0
        student_completion[sid] = percent

    go_success_rate = round(
        (total_go / (total_go + total_no_go)) * 100, 2
    ) if (total_go + total_no_go) else 0

    # ----- SYSTEM STATUS -----

    critical = [v for v in violations if v["severity"] == "CRITICAL"]

    if critical:
        system_status = "VIOLATION"
    elif violations:
        system_status = "VALID_WITH_WARNINGS"
    else:
        system_status = "VALID"

    return {
        "system_status": system_status,
        "summary_metrics": {
            "total_go_flights": total_go,
            "total_no_go_flights": total_no_go,
            "go_success_rate_percent": go_success_rate
        },
        "utilization_metrics": {
            "instructor_utilization_percent": instructor_utilization,
            "aircraft_utilization_percent": aircraft_utilization,
            "student_completion_percent": student_completion
        },
        "violations": violations
    }