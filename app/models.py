from sqlalchemy import Column, String, Boolean, Integer,JSON,Float,DateTime, Text
from app.database import Base
from datetime import datetime


class Student(Base):
    __tablename__ = "students"

    student_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    stage = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    solo_eligible = Column(Boolean, default=False)
    required_sorties_per_week = Column(Integer, nullable=False)
    availability = Column(JSON, nullable=False)
    preferred_sortie_types = Column(JSON)


class Instructor(Base):
    __tablename__ = "instructors"

    instructor_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ratings = Column(JSON, nullable=False)
    currency = Column(Boolean, default=True)
    max_duty_hours_per_day = Column(Integer, nullable=False)
    sim_instructor = Column(Boolean, default=False)
    availability = Column(JSON, nullable=False)


class Aircraft(Base):
    __tablename__ = "aircraft"

    aircraft_id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False)
    maintenance_status = Column(String, nullable=False)
    availability = Column(JSON, nullable=False)


class Simulator(Base):
    __tablename__ = "simulators"

    simulator_id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False)
    max_sessions_per_day = Column(Integer, nullable=False)
    availability = Column(JSON, nullable=False)


class TimeSlot(Base):
    __tablename__ = "time_slots"

    slot_id = Column(String, primary_key=True, index=True)
    label = Column(String, nullable=False)
    start = Column(String, nullable=False)
    end = Column(String, nullable=False)
    duration_hours = Column(Float, nullable=False)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    run_id = Column(String, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(String)  # SUCCESS / FAILED
    inserted_count = Column(Integer, default=0)
    updated_count = Column(Integer, default=0)
    diff_summary = Column(JSON)