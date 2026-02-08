import uuid
from datetime import time, date
from typing import Optional
from pydantic import BaseModel, field_validator, EmailStr


class PossibleTimeRequest(BaseModel):
    master_id: uuid.UUID
    appointment_date: date
    price_id: uuid.UUID


class IDRequest(BaseModel):
    id: uuid.UUID

class AppointmentCreateRequest(BaseModel):
    user_id: uuid.UUID
    master_id: uuid.UUID
    date: date
    start_time: time
    price_id: uuid.UUID

class MasterUpdateRequest(BaseModel):
    id: uuid.UUID
    chat_id: int
    full_name: Optional[str] = None
    working_day_start: Optional[time] = None
    working_day_end: Optional[time] = None
    day_off: Optional[str] = None

class MasterCreateRequest(BaseModel):
    chat_id: int
    organization_id: uuid.UUID
    username: Optional[str] = "no info"
    full_name: Optional[str] = "no info"
    working_day_start: Optional[time]
    working_day_end: Optional[time]
    day_off: Optional[str]

class UserCreateRequest(BaseModel):
    chat_id: int
    organization_id: uuid.UUID
    username: Optional[str] = None

class OrganizationCreateRequest(BaseModel):
    name: str
    address: str
    description: Optional[str] = "no info"
    categories: str
    fixed_prices: bool
    day_start_template: time
    day_end_template: time
    day_off: str
    admin_id: uuid.UUID
    
class OrganizationUpdateRequest(BaseModel):
    id: uuid.UUID
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[str] = None
    fixed_prices: Optional[bool] = None
    day_start_template: Optional[time] = None
    day_end_template: Optional[time] = None
    day_off: Optional[str] = None
    admin_id: uuid.UUID

class PriceUpdateRequest(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: Optional[str] = None
    price: Optional[int] = None
    category: Optional[int] = None
    approximate_time: Optional[time] = None


class PriceCreateRequest(BaseModel):
    organization_id: uuid.UUID
    category: int
    name: str
    approximate_time: time
    price: int



class AdminCreateRequest(BaseModel):
    email: EmailStr
    password: str
    yaToken: Optional[str] = "no info"
    subscription: int
    end_of_subscription: Optional[date] = None

class AdminUpdateRequest(BaseModel):
    id: uuid.UUID
    password: Optional[str] = None
    yaToken: Optional[str] = None
    subscription: Optional[int] = None
    end_of_subscription: Optional[date] = None