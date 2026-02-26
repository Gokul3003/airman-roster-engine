from collections import defaultdict


def validate_dispatch(roster_output):
    assignments = roster_output["assignments"]
    student_summary = roster_output["student_weekly_summary"]

    go_assignments = []
    no_go_assignments = []

    instructor_usage = defaultdict(int)
    aircraft_usage = defaultdict(int)

    for a in assignments:

        if a["dispatch_decision"] == "GO":
            go_assignments.append(a)
        else:
            no_go_assignments.append(a)

        instructor_usage[a["instructor_id"]] += 1
        aircraft_usage[a["aircraft_id"]] += 1

    total = len(assignments)
    go_count = len(go_assignments)
    no_go_count = len(no_go_assignments)

    dispatch_rate = round((go_count / total) * 100, 2) if total > 0 else 0

    unmet_students = {
        student_id: count
        for student_id, count in student_summary.items()
        if count == 0
    }

    return {
        "operational_summary": {
            "total_assignments": total,
            "go_count": go_count,
            "no_go_count": no_go_count,
            "dispatch_success_rate_percent": dispatch_rate
        },
        "resource_utilization": {
            "instructor_usage": dict(instructor_usage),
            "aircraft_usage": dict(aircraft_usage)
        },
        "unmet_students": unmet_students,
        "go_assignments": go_assignments,
        "no_go_assignments": no_go_assignments
    }