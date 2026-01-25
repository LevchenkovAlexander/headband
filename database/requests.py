from datetime import time, datetime, date
from typing import Optional, Dict
import re
from pydantic import BaseModel, validator, field_validator

class AppointmentCreateRequest(BaseModel):
    id: Optional[int] = None
    user_id: int
    master_id: int
    date: date
    start_time: time
    end_time: time
    service_id: int

class MasterUpdateRequest(BaseModel):
    photo_path: Optional[str] = None
    name: Optional[str] = None
    working_day_start: Optional[time] = None
    working_day_end: Optional[time] = None
    day_off: Optional[str] = None