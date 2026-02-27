# app/evaluation_harness.py

from app.reallocation_engine import reallocate_roster
from app.roster_versioning import calculate_churn


def run_evaluation_suite(base_roster, events):

    results = []
    current = base_roster

    for event in events:

        new_roster, violations = reallocate_roster(current, event)
        churn = calculate_churn(current, new_roster)

        results.append({
            "event_id": event.event_id,
            "violations": violations,
            "churn": churn
        })

        current = new_roster

    return {
        "total_events": len(events),
        "average_churn": sum(r["churn"] for r in results) / len(results),
        "max_churn": max(r["churn"] for r in results),
        "total_violations": sum(r["violations"] for r in results),
        "details": results
    }