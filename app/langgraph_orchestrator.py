# app/langgraph_orchestrator.py

from typing import TypedDict
from langgraph.graph import StateGraph, END

from app.reallocation_engine import reallocate_roster
from app.compliance_engine import validate_operational_compliance
from app.database import SessionLocal
from app.models import Instructor, Aircraft, Student


# -----------------------------------------------------
# Graph State Definition
# -----------------------------------------------------

class DispatchState(TypedDict):
    roster: dict
    event: dict
    updated_roster: dict
    violations: int
    explanation: str


# -----------------------------------------------------
# Node 1 — Reallocation
# -----------------------------------------------------

def reallocation_node(state: DispatchState):

    roster = state["roster"]
    event = state["event"]

    updated_roster, violations = reallocate_roster(roster, event)

    return {
        "updated_roster": updated_roster,
        "violations": violations
    }


# -----------------------------------------------------
# Node 2 — Compliance Validation
# -----------------------------------------------------

def compliance_node(state: DispatchState):

    db = SessionLocal()

    instructors = db.query(Instructor).all()
    aircraft = db.query(Aircraft).all()
    students = db.query(Student).all()

    assignments = []

    for day_block in state["updated_roster"]["roster"]:
        for slot in day_block["slots"]:

            aircraft_id = None
            if slot["activity"] == "FLIGHT":
                aircraft_id = slot["resource_id"]

            assignments.append({
                "day": day_block["date"],
                "slot_id": slot["slot_id"],
                "student_id": slot["student_id"],
                "instructor_id": slot["instructor_id"],
                "aircraft_id": aircraft_id,
                "dispatch_decision": slot["dispatch_decision"],
                "activity": slot["activity"]
            })

    compliance_report = validate_operational_compliance(
        assignments,
        instructors,
        aircraft,
        students
    )

    db.close()

    return {
        "updated_roster": state["updated_roster"],
        "violations": compliance_report.get("violation_count", 0)
    }


# -----------------------------------------------------
# Node 3 — Explanation
# -----------------------------------------------------

def explanation_node(state: DispatchState):

    violations = state["violations"]

    if violations > 0:
        explanation = (
            "Reallocation completed but compliance violations were detected."
        )
    else:
        explanation = (
            "Reallocation successful. No compliance violations detected."
        )

    return {
        "explanation": explanation
    }


# -----------------------------------------------------
# Build & Compile Graph
# -----------------------------------------------------

def build_dispatch_graph():

    builder = StateGraph(DispatchState)

    # Add nodes
    builder.add_node("reallocation", reallocation_node)
    builder.add_node("compliance", compliance_node)
    builder.add_node("explanation", explanation_node)

    # Entry point
    builder.set_entry_point("reallocation")

    # Edges
    builder.add_edge("reallocation", "compliance")
    builder.add_edge("compliance", "explanation")
    builder.add_edge("explanation", END)

    # Compile graph
    graph = builder.compile()

    # 🔥 Print ASCII representation (for demo / logs)
    try:
        print("\n=== LANGGRAPH WORKFLOW ===")
        print(graph.get_graph().draw_ascii())
        print("==========================\n")
    except Exception:
        print("LangGraph ASCII visualization not supported in this version.")

    return graph