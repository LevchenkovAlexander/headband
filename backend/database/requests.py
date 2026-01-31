import uuid
from datetime import time, datetime, date
from typing import Optional, Dict
import re
from pydantic import BaseModel, validator, field_validator, EmailStr


class AppointmentCreateRequest(BaseModel):
    id: Optional[int] = None
    user_id: int
    master_id: int
    date: date
    start_time: time
    end_time: time
    price_id: uuid.UUID

class MasterUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    working_day_start: Optional[time] = None
    working_day_end: Optional[time] = None
    day_off: Optional[str] = None

class MasterCreateRequest(BaseModel):
    id: int
    organization_id: uuid.UUID
    username: Optional[str] = "no info"
    full_name: Optional[str] = "no info"
    working_day_start: Optional[time]
    working_day_end: Optional[time]
    day_off: Optional[str]

class UserCreateRequest(BaseModel):
    id: int
    organization_id: uuid.UUID
    username: Optional[str] = None

class OrganizationCreateRequest(BaseModel):
    name: str
    address: str
    description: Optional[str] = "no info"
    categories: str
    fixed_schedule: bool
    fixed_prices: bool
    day_start_template: time
    day_end_template: time
    day_off: str
    admin_id: uuid.UUID

class AdminCreateRequest(BaseModel):
    email: EmailStr
    password: str
    yaToken: Optional[str] = "no info"