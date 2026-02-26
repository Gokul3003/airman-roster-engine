from fastapi import FastAPI, Query
from app.database import engine, Base, SessionLocal
from app import models
from app.ingestion import run_ingestion
from app.weather_rules import evaluate_weather
from app.weather import get_weather
from app.roster_engine import generate_weekly_roster
from app.roster_engine import generate_weekly_roster
from app.dispatch_validator import validate_dispatch



app = FastAPI(title="AIRMAN AI Dispatch Agent")


# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Airman Agent Running"}

@app.post("/ingest/run")
def ingest():
    return run_ingestion()

@app.get("/test-dispatch")
def test_dispatch():
    # weather = get_weather("VOBG", "07:00", "09:30")
    weather = get_weather("VOBG", "09:30", "12:00")
    result = evaluate_weather("BASIC", "CIRCUITS", weather)

    decision = evaluate_weather(stage= "BASIC", sortie_type="CIRCUITS", weather_data=weather)
    return {
        "weather": weather,
        "decision": result
    }

@app.get("/roster/generate")
def generate_roster():
    return generate_weekly_roster()

@app.get("/dispatch/final-report")
def dispatch_final_report():
    roster = generate_weekly_roster()
    return validate_dispatch(roster)


@app.post("/ingest/run")
def ingest_run():
    db = SessionLocal()
    try:
        result = run_ingestion(db)
        return {
            "status": "SUCCESS",
            "details": result
        }
    finally:
        db.close()


@app.post("/dispatch/recompute")
def dispatch_recompute(date: str = Query(...)):
    """
    Recompute dispatch for a given date.
    """
    result = generate_weekly_roster()
    return {
        "date": date,
        "recomputed": True,
        "result": result
    }

@app.post("/eval/run")
def eval_run():
    result = generate_weekly_roster()

    compliance = result.get("compliance_report", {})
    system_status = compliance.get("system_status")

    if system_status == "VIOLATION":
        status = "FAIL"
    else:
        status = "PASS"

    return {
        "evaluation_status": status,
        "system_status": system_status,
        "summary_metrics": compliance.get("summary_metrics"),
        "violations": compliance.get("violations")
    }