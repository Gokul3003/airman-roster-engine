import json
import uuid
from app.database import SessionLocal
from app.models import Student,Instructor,Aircraft,Simulator,TimeSlot,IngestionRun
from datetime import datetime


def run_ingestion():
    db = SessionLocal()
    run_id = str(uuid.uuid4())

    ingestion_record = IngestionRun(
        run_id=run_id,
        started_at=datetime.utcnow(),
        status="RUNNING",
        inserted_count=0,
        updated_count=0,
        diff_summary={}
    )

    db.add(ingestion_record)
    db.commit()

    inserted = 0
    updated = 0
    diffs = {}
    try:
        #-----------------------Students--------------------------
        with open("data_bucket/students.json", "r") as f:
            students_data = json.load(f)
        
        student_diffs = {}

        for student in students_data:
            existing = db.query(Student).filter_by(
                student_id=student["student_id"]
            ).first()

            if not existing:
                db.add(Student(**student))
                inserted += 1
            else:
                changed_fields = {}
                for key, value in student.items():
                    if getattr(existing, key) != value:
                        setattr(existing, key, value)
                        changed_fields[key] = "updated"
                if changed_fields:
                    student_diffs[student["student_id"]] = changed_fields
                    updated += 1
        diffs["students"] = student_diffs

        # -------- Instructors --------
        with open("data_bucket/instructors.json", "r") as f:
            instructors_data = json.load(f)
        instructor_diffs = {}
        for instructor in instructors_data:
            existing = db.query(Instructor).filter_by(
                instructor_id=instructor["instructor_id"]
            ).first()

            if not existing:
                db.add(Instructor(**instructor))
                inserted += 1
            
            else:
                changed_fields = {}
                for key, value in instructor.items():
                    if getattr(existing, key) != value:
                        setattr(existing, key, value)
                        changed_fields[key] = "updated"

                if changed_fields:
                    instructor_diffs[instructor["instructor_id"]] = changed_fields
                    updated += 1
        diffs["instructors"] = instructor_diffs

        # -------- Aircraft --------
        with open("data_bucket/aircraft.json", "r") as f:
            aircraft_data = json.load(f)
        aircraft_diffs = {}

        for aircraft in aircraft_data:
            existing = db.query(Aircraft).filter_by(
                aircraft_id=aircraft["aircraft_id"]
            ).first()

            if not existing:
                db.add(Aircraft(**aircraft))
                inserted += 1
            
            else:
                changed_fields = {}

                for key, value in aircraft.items():
                    if getattr(existing, key) != value:
                        setattr(existing, key, value)
                        changed_fields[key] = "updated"

                if changed_fields:
                    aircraft_diffs[aircraft["aircraft_id"]] = changed_fields
                    updated += 1

        diffs["aircraft"] = aircraft_diffs

        # -------- Simulators --------
        with open("data_bucket/simulators.json", "r") as f:
            simulators_data = json.load(f)
        simulator_diffs = {}

        for simulator in simulators_data:
            existing = db.query(Simulator).filter_by(
                simulator_id=simulator["simulator_id"]
            ).first()

            if not existing:
                db.add(Simulator(**simulator))
                inserted += 1
            else:
                changed_fields = {}

                for key, value in simulator.items():
                    if getattr(existing, key) != value:
                        setattr(existing, key, value)
                        changed_fields[key] = "updated"

                if changed_fields:
                    simulator_diffs[simulator["simulator_id"]] = changed_fields
                    updated += 1

        diffs["simulators"] = simulator_diffs

        #----------------Time_solts-----------------
        with open("data_bucket/time_slots.json", "r") as f:
            time_slots = json.load(f)
        slot_diffs = {}

        for time_slot in time_slots:
            existing = db.query(TimeSlot).filter_by(
                slot_id = time_slot["slot_id"]
            ).first()

            if not existing:
                db.add(TimeSlot(**time_slot))
                inserted += 1
            else:
                changed_fields = {}

                for key, value in time_slot.items():
                    if getattr(existing, key) != value:
                        setattr(existing, key, value)
                        changed_fields[key] = "updated"

                if changed_fields:
                    slot_diffs[time_slot["slot_id"]] = changed_fields
                    updated += 1

        diffs["time_slots"] = slot_diffs

        db.commit()

        ingestion_record.completed_at = datetime.utcnow()
        ingestion_record.status = "SUCCESS"
        ingestion_record.inserted_count = inserted
        ingestion_record.updated_count = updated
        ingestion_record.diff_summary = diffs

        db.commit()

    except Exception as e:
        ingestion_record.status = "FAILED"
        ingestion_record.completed_at = datetime.utcnow()
        db.commit()
        raise e
    
    finally:
        db.close()
    
    return {
        "run_id": run_id,
        "status": "SUCCESS",
        "inserted": inserted,
        "updated": updated
    }