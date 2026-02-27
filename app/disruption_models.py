# app/disruption_models.py

from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class DisruptionType(str, Enum):
    WEATHER_UPDATE = "WEATHER_UPDATE"
    AIRCRAFT_UNSERVICEABLE = "AIRCRAFT_UNSERVICEABLE"
    INSTRUCTOR_UNAVAILABLE = "INSTRUCTOR_UNAVAILABLE"
    STUDENT_UNAVAILABLE = "STUDENT_UNAVAILABLE"


class DisruptionEvent(BaseModel):
    event_id: str
    type: DisruptionType

    from_time: datetime
    to_time: datetime

    aircraft_id: Optional[str] = None
    instructor_id: Optional[str] = None
    student_id: Optional[str] = None

    new_weather: Optional[Dict] = None