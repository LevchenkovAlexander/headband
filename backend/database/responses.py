import uuid
from datetime import time, date
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, ConfigDict


class StatusResponse(BaseModel):
    status: str

class IDResponse(StatusResponse):
    id: uuid.UUID

class OrganizationResponse(IDResponse):
    tg_master: str
    tg_user: str

class AppointmentListResponse(StatusResponse):
    count: int = 0
    appointments: List[Dict] = []


class PossibleTimesResponse(StatusResponse):
    times: List[time] = []

class WeekTimetableResponse(StatusResponse):
    week_appointments: List[List[Dict[str, Any]]] = []


class AppointmentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    master_id: uuid.UUID
    date: date
    start_time: time
    end_time: time
    price_id: uuid.UUID
    address: Optional[str] = "no_info"

    model_config = ConfigDict(from_attributes=True)


