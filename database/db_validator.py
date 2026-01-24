from datetime import time, datetime, date
from typing import Optional, Dict
import re
from pydantic import BaseModel, validator, field_validator

class AppointmentTO(BaseModel):
    id: Optional[int] = None
    user_id: int
    master_id: int
    date: date
    start_time: time
    end_time: time
    service_id: int

class MasterTO(BaseModel):
    id: Optional[int] = None
    organization_id: int
    photo_path: str
    name: str
    working_day_start: time
    working_day_end: time
    day_off: int

class MasterUpdate(BaseModel):
    photo_path: Optional[str] = None
    name: Optional[str] = None
    working_day_start: Optional[time] = None
    working_day_end: Optional[time] = None
    day_off: Optional[str] = None