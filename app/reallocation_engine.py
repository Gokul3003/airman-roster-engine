from copy import deepcopy
from datetime import datetime

from app.capacity_manager import CapacityManager
from app.compliance_engine import validate_operational_compliance
from app.weather_rules import evaluate_weather


def reallocate_roster(roster, event):
    """
    Reallocate roster based on disruption event.
    Supports:
        - dict event
        - Pydantic DisruptionEvent
        - datetime or string timestamps
    Returns:
        (updated_roster, violation_count)
    """

    # ===============================
    # 1️⃣ Defensive Validation
    # ===============================

    if roster is None:
        raise ValueError("Roster cannot be None.")

    if not isinstance(roster, dict):
        raise ValueError("Roster must be a dictionary.")

    if "roster" not in roster:
        raise ValueError("Invalid roster structure. Missing 'roster' key.")

    # Convert Pydantic event → dict
    if hasattr(event, "dict"):
        event = event.dict()

    if not isinstance(event, dict):
        raise ValueError("Event must be dict or Pydantic model.")

    event_type = event.get("type")

    # Deep copy so original is untouched
    new_roster = deepcopy(roster)

    # ===============================
    # 2️⃣ Register Existing Capacity
    # ===============================

    capacity_manager = CapacityManager()
    capacity_manager.register_existing_allocations(new_roster)

    # ===============================
    # 3️⃣ WEATHER UPDATE
    # ===============================

    if event_type == "WEATHER_UPDATE":

        from_raw = event.get("from_time")
        to_raw = event.get("to_time")

        # Support both string and datetime
        from_time = (
            datetime.fromisoformat(from_raw)
            if isinstance(from_raw, str)
            else from_raw
        )

        to_time = (
            datetime.fromisoformat(to_raw)
            if isinstance(to_raw, str)
            else to_raw
        )

        new_weather = event.get("new_weather", {})

        for day_block in new_roster["roster"]:
            for slot in day_block.get("slots", []):

                slot_datetime = datetime.fromisoformat(
                    f"{slot['date']}T{slot['start']}:00"
                )

                if from_time <= slot_datetime <= to_time:

                    decision = evaluate_weather(
                        slot.get("stage"),
                        slot.get("sortie_type"),
                        new_weather
                    )

                    if decision.get("dispatch_decision") == "NO_GO":

                        slot["activity"] = "SIM"
                        slot["dispatch_decision"] = "NO_GO"
                        slot["resource_id"] = "SIM01"
                        slot["reasons"] = [
                            "WX_BELOW_MINIMA",
                            "SIM_SUBSTITUTION"
                        ]

                        capacity_manager.register_sim(
                            slot["date"],
                            slot["slot_id"]
                        )

    # ===============================
    # 4️⃣ AIRCRAFT FAILURE
    # ===============================

    elif event_type == "AIRCRAFT_FAILURE":

        failed_aircraft = event.get("aircraft_id")

        for day_block in new_roster["roster"]:
            for slot in day_block.get("slots", []):
                if slot.get("resource_id") == failed_aircraft:

                    slot["activity"] = "SIM"
                    slot["dispatch_decision"] = "NO_GO"
                    slot["resource_id"] = "SIM01"
                    slot["reasons"] = [
                        "AIRCRAFT_UNSERVICEABLE",
                        "SIM_SUBSTITUTION"
                    ]

    # ===============================
    # 5️⃣ INSTRUCTOR UNAVAILABLE
    # ===============================

    elif event_type == "INSTRUCTOR_UNAVAILABLE":

        instructor_id = event.get("instructor_id")

        for day_block in new_roster["roster"]:
            for slot in day_block.get("slots", []):
                if slot.get("instructor_id") == instructor_id:

                    slot["dispatch_decision"] = "NEEDS_REVIEW"
                    slot["reasons"] = ["INSTRUCTOR_UNAVAILABLE"]

    # ===============================
    # 6️⃣ Compliance Recalculation
    # ===============================

    assignments = []

    for block in new_roster["roster"]:
        for slot in block.get("slots", []):
            assignments.append({
                "day": block["date"],
                "slot_id": slot.get("slot_id"),
                "student_id": slot.get("student_id"),
                "instructor_id": slot.get("instructor_id"),
                "aircraft_id": slot.get("resource_id"),
                "dispatch_decision": slot.get("dispatch_decision"),
                "activity": slot.get("activity"),
            })

    compliance_report = validate_operational_compliance(
        assignments=assignments,
        instructors=[],
        aircraft_list=[],
        students=[]
    )

    new_roster["compliance_report"] = compliance_report

    violations = len(compliance_report.get("violations", []))

    return new_roster, violations