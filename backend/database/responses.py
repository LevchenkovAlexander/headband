import uuid
from datetime import time, date
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


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
    service_name: Optional[str] = "no_info"

    model_config = ConfigDict(from_attributes=True)
class AdminResponseMasters(IDResponse):
    username: str
    full_name: str
    working_day_start: time
    working_day_end: time
    day_off: str
    categories: str

class AdminResponseSpecialOffers(IDResponse):
    organization_id: uuid.UUID
    name: str
    deadline_start: Optional[date]
    deadline_end: Optional[date]

class AdminResponseOrganizations(OrganizationResponse):
    name: str
    address: str
    categories: str

class AdminResponseInfo(IDResponse):
    email: EmailStr
    end_of_subscription: date
    num_organizations: int
    num_masters: int
    num_users: int
    organizations: List[Dict]
    masters: List[Dict]
    offers: List[Dict]

class OrgnaizationBaseResponse(BaseModel):
    id: uuid.UUID
    name: str

class OrganizationFilterResponse(StatusResponse):
    organizations: List[OrgnaizationBaseResponse] | []

class GuideResponse(BaseModel):
    id: uuid.UUID
    name: str
    category: str

class GuidePageResponse(StatusResponse):
    guides_fit: List[GuideResponse] | []
    guides_all: List[GuideResponse] | []

class StepResponse(StatusResponse):
    steps: Text

class UserResponseMainPage(StatusResponse):
    appointments: Optional[List[Dict]] = None
    categories: str

class UserResponseMastersOnMastersPage(BaseModel):
    id: uuid.UUID
    name: str
    address: str
    subcategories: str

class UserResponseMastersPage(StatusResponse):
    masters: Optional[List[UserResponseMastersOnMastersPage]] = None











