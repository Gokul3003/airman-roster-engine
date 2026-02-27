from datetime import datetime

from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.dispatch_validator import validate_dispatch
from app.disruption_models import DisruptionEvent
from app.evaluation_harness import run_evaluation_suite
from app.ingestion import run_ingestion
from app.langgraph_orchestrator import build_dispatch_graph
from app.reallocation_engine import reallocate_roster
from app.roster_engine import generate_weekly_roster
from app.roster_versioning import (
    calculate_churn,
    calculate_diff,
    fetch_versions,
    get_latest_roster,
    save_version,
)
from app.weather import get_weather
from app.weather_rules import evaluate_weather

app = FastAPI(title="AIRMAN AI Dispatch Agent")

# Create tables
Base.metadata.create_all(bind=engine)


# -----------------------------
# DB Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Root
# -----------------------------
@app.get("/")
def root():
    return {"message": "Airman Agent Running"}


# -----------------------------
# Ingestion
# -----------------------------
@app.post("/ingest/run")
def ingest_run():
    result = run_ingestion()
    return {"status": "SUCCESS", "details": result}


# -----------------------------
# Weather Test
# -----------------------------
@app.get("/test-dispatch")
def test_dispatch():
    weather = get_weather("VOBG", "09:30", "12:00")
    result = evaluate_weather("BASIC", "CIRCUITS", weather)

    return {"weather": weather, "decision": result}


# -----------------------------
# Roster
# -----------------------------
@app.get("/roster/generate")
def generate_roster():
    return generate_weekly_roster()


@app.get("/dispatch/final-report")
def dispatch_final_report():
    roster = generate_weekly_roster()
    return validate_dispatch(roster)


# -----------------------------
# Dispatch Recompute
# -----------------------------
@app.post("/dispatch/recompute")
def dispatch_recompute(date: str = Query(...)):
    result = generate_weekly_roster()
    return {"date": date, "recomputed": True, "result": result}


# -----------------------------
# Evaluation
# -----------------------------
@app.post("/eval/run")
def eval_run():
    result = generate_weekly_roster()

    compliance = result.get("compliance_report", {})
    system_status = compliance.get("system_status")
    status = "FAIL" if system_status == "VIOLATION" else "PASS"

    return {
        "evaluation_status": status,
        "system_status": system_status,
        "summary_metrics": compliance.get("summary_metrics"),
        "violations": compliance.get("violations"),
    }


# -----------------------------
# Version History (Level 2)
# -----------------------------
@app.get("/roster/versions")
def get_versions_endpoint(db: Session = Depends(get_db)):
    return fetch_versions(db)


@app.post("/roster/reallocate")
def reallocate_endpoint(
    event: DisruptionEvent,
    db: Session = Depends(get_db),
):
    current_roster = get_latest_roster(db)

    if not current_roster:
        current_roster = generate_weekly_roster()

    new_roster, violations = reallocate_roster(current_roster, event)

    churn = calculate_churn(current_roster, new_roster)
    diff = calculate_diff(current_roster, new_roster)

    save_version(
        db=db,
        correlation_id=event.event_id,
        roster_snapshot=new_roster,
        diff=diff,
        churn=churn,
        violations=violations,
    )

    return {
        "event_id": event.event_id,
        "violations": violations,
        "churn": churn,
        "diff_count": len(diff),
        "updated_roster": new_roster,
    }


# -----------------------------
# Stress Test
# -----------------------------
@app.post("/eval/stress-test")
def stress_test(db: Session = Depends(get_db)):
    base = get_latest_roster(db)

    events = [
        DisruptionEvent(
            event_id="STRESS_WX_LOW",
            type="WEATHER_UPDATE",
            from_time=datetime(2026, 2, 27, 7),
            to_time=datetime(2026, 2, 27, 14),
            new_weather={
                "ceiling": 400,
                "visibility": 2,
                "confidence": "HIGH",
            },
        ),
        DisruptionEvent(
            event_id="STRESS_AC_FAIL",
            type="AIRCRAFT_UNSERVICEABLE",
            from_time=datetime(2026, 2, 27, 7),
            to_time=datetime(2026, 2, 27, 12),
            aircraft_id="AC01",
        ),
        DisruptionEvent(
            event_id="STRESS_INST_1",
            type="INSTRUCTOR_UNAVAILABLE",
            from_time=datetime(2026, 2, 27, 7),
            to_time=datetime(2026, 2, 27, 9),
            instructor_id="I001",
        ),
        DisruptionEvent(
            event_id="STRESS_INST_2",
            type="INSTRUCTOR_UNAVAILABLE",
            from_time=datetime(2026, 2, 27, 12),
            to_time=datetime(2026, 2, 27, 14),
            instructor_id="I002",
        ),
        DisruptionEvent(
            event_id="STRESS_WX_RECOVER",
            type="WEATHER_UPDATE",
            from_time=datetime(2026, 2, 27, 7),
            to_time=datetime(2026, 2, 27, 14),
            new_weather={
                "ceiling": 5000,
                "visibility": 10,
                "confidence": "HIGH",
            },
        ),
    ]

    return run_evaluation_suite(base, events)


# -----------------------------
# Graph Reallocation (LangGraph)
# -----------------------------
@app.post("/roster/reallocate-graph")
def reallocate_with_graph(
    event: DisruptionEvent,
    db: Session = Depends(get_db),
):
    graph = build_dispatch_graph()

    base_roster = get_latest_roster(db)

    if base_roster is None:
        base_roster = generate_weekly_roster()

    result = graph.invoke({"roster": base_roster, "event": event})

    return result