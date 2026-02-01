import uuid
from typing import List, Dict, Any

from pydantic import BaseModel


class StatusResponse(BaseModel):
    status: str

class IDResponse(StatusResponse):
    id: uuid.UUID

class OrganizationResponse(IDResponse):
    tg_master: str
    tg_user: str

class AppointmentListResponse(StatusResponse):
    count: int = 0
    appointments: List[Dict[str, Any]] = []

class PossibleTimesResponse(StatusResponse):
    times: List[str] = []

class WeekTimetableResponse(StatusResponse):
    week_appointments: List[List[Dict[str, Any]]] = []


