import uuid
from datetime import time, date
from typing import Optional, List
from pydantic import BaseModel, field_validator, EmailStr





class PossibleTimeRequest(BaseModel):
    master_id: uuid.UUID
    appointment_date: date
    price_id: uuid.UUID

class StepCreateRequest(BaseModel):
    master_id: uuid.UUID
    guide_id: uuid.UUID
    step_num: int
    title: str
    text: str

class StepUpdateRequest(BaseModel):
    master_id: uuid.UUID
    guide_id: uuid.UUID
    step_id: uuid.UUID
    step_num: Optional[int] = None
    title: Optional[str] = None
    text: Optional[str] = None

class VideoStepCreateRequest(BaseModel):
    master_id: uuid.UUID
    guide_id: uuid.UUID
    step_num: int
    video_name: str
    video_file_path: str
    description: Optional[str] = None

class VideoStepUpdateRequest(BaseModel):
    master_id: uuid.UUID
    guide_id: uuid.UUID
    step_num: Optional[int] = None
    video_name: Optional[str] = None
    video_file_path: Optional[str] = None
    description: Optional[str] = None

class IDRequest(BaseModel):
    id: uuid.UUID

class AppointmentCreateRequest(BaseModel):
    user_id: uuid.UUID
    master_id: uuid.UUID
    date: date
    start_time: time
    price_id: uuid.UUID



class MasterCreateRequestTG(BaseModel):
    chat_id_tg: int
    username_tg: Optional[str] = "no info"
    full_name: Optional[str] = "no info"
    master_link_id: uuid.UUID
    user_link_id: uuid.UUID

class UserCreateRequest(BaseModel):
    chat_id: int
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




class PriceCreateRequest(BaseModel):
    category: int
    name: str
    approximate_time: int
    price: int

class AdminCreateRequest(BaseModel):
    email: EmailStr
    password: str
    yaToken: Optional[str] = "no info"
    subscription: int
    end_of_subscription: Optional[date] = None

class AdminAuthRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    yaToken: Optional[str] = None

class AdminUpdateRequest(BaseModel):
    id: uuid.UUID
    password: Optional[str] = None
    yaToken: Optional[str] = None
    subscription: Optional[int] = None
    end_of_subscription: Optional[date] = None

class OfferCreateRequest(BaseModel):
    organization_id: uuid.UUID
    name: str
    description: str
    deadline_start: Optional[date] = None
    deadline_end: Optional[date] = None

class OfferUpdateRequest(BaseModel):
    id: uuid.UUID
    name: Optional[str] = None
    description: Optional[str] = None
    deadline_start: Optional[date] = None
    deadline_end: Optional[date] = None

class MastersPageRequest(BaseModel):
    chat_id: int
    category: int
    filter: Optional[List[uuid.UUID]] = None

class AddressCreateRequest(BaseModel):
    master_id: uuid.UUID
    address: str

class AddressUpdateRequest(BaseModel):
    id: uuid.UUID
    address: str

class WeekTemplate(BaseModel):
    weekday: int
    start_time: time
    end_time: time
    address_id: uuid.UUID

class TemplateCreateRequest(BaseModel):
    master_id: uuid.UUID
    days: List[WeekTemplate]

class TemplateUpdateRequest(BaseModel):
    master_id: uuid.UUID
    weekday: int
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    address_id: Optional[uuid.UUID] = None

class WorkingDayUpdateRequest(BaseModel):
    master_id: uuid.UUID
    day_date: date
    start_time: time
    end_time: time
    address_id: uuid.UUID

class CategoryCreateRequest(BaseModel):
    name: str

class AbsenceCreateRequest(BaseModel):
    master_id: uuid.UUID
    start_date: date
    end_date: date
    reason: Optional[str] = None

class AbsenceUpdateRequest(BaseModel):
    absence_id: uuid.UUID
    master_id: uuid.UUID
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = None

class GuideCreateRequest(BaseModel):
    name: str
    category: str
    steps: str
    author: uuid.UUID

class GuideUpdateRequest(BaseModel):
    id: uuid.UUID
    author: uuid.UUID
    name: Optional[str] = None
    category: Optional[str] = None
    steps: Optional[str] = None

class EarningCreateRequest(BaseModel):
    master_id: uuid.UUID
    appointment_id: uuid.UUID

class EarningDateRangeRequest(BaseModel):
    master_id: uuid.UUID
    start_date: date
    end_date: date

class EarningUpdateRequest(BaseModel):
    id: uuid.UUID
    price: Optional[int] = None
    date: Optional[date] = None

class PrepayCreateRequest(BaseModel):
    master_id: uuid.UUID
    percent: int
    start_date: date
    end_date: date

class PrepayUpdateRequest(BaseModel):
    id: uuid.UUID
    percent: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class PrepayCheckRequest(BaseModel):
    master_id: uuid.UUID
    check_date: date

class MasterNotificationUpdateRequest(BaseModel):
    master_id: uuid.UUID
    appointment_notification: Optional[bool] = None
    appointment_cancel_notification: Optional[bool] = None
    appointment_confirm_notification: Optional[bool] = None
    guide_approved_notification: Optional[bool] = None
    subscription_ending_notification: Optional[bool] = None




