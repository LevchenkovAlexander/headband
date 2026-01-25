from typing import List, Dict, Any

from pydantic import BaseModel


class StatusResponse(BaseModel):
    status: str


class AppointmentListResponse(BaseModel):
    status: str
    count: int = 0
    appointments: List[Dict[str, Any]] = []

class PossibleTimesResponse(BaseModel):
    status: str
    times: List[str] = []

class WeekTimetableResponse(BaseModel):
    status: str
    week_appointments: List[List[Dict[str, Any]]] = []

