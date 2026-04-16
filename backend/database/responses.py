import uuid
from datetime import date, time
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from backend.database.requests import WeekTemplate


class StatusResponse(BaseModel):
    status: str

class IDResponse(StatusResponse):
    id: uuid.UUID







class PossibleTimesResponse(BaseModel):
    status: str
    times: List[time]









class GuideStepResponse(BaseModel):
    status: str
    steps: Optional[str] = None


class MasterBaseResponse(BaseModel):
    id: UUID
    chat_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    working_day_start: int  # минуты от начала дня
    working_day_end: int
    categories: List[str] = Field(default_factory=list)


class MasterUpdateResponse(BaseModel):
    status: str


class MasterCategoriesResponse(BaseModel):
    status: str
    categories: List[dict]


class MasterPricesResponse(BaseModel):
    status: str
    prices: List[dict]


class UserBaseResponse(BaseModel):
    id: UUID
    chat_id: int
    username: Optional[str] = None


"""class UserResponseMainPage(BaseModel):
    status: str
    appointments: List[AppointmentResponse]
    categories: List[str]"""


class MasterListItem(BaseModel):
    id: UUID
    name: str
    address: Optional[str] = None
    subcategories: List[str] = Field(default_factory=list)


class UserResponseMastersPage(BaseModel):
    status: str
    masters: List[MasterListItem]


class CategoryBaseResponse(BaseModel):
    id: UUID
    name: str


class CategoriesResponse(BaseModel):
    status: str
    categories: List[CategoryBaseResponse]


class PriceBaseResponse(BaseModel):
    id: UUID
    name: str
    price: int
    category: str
    approximate_time: int  # минуты
    master_id: UUID


class PriceListResponse(BaseModel):
    status: str
    prices: List[PriceBaseResponse]


class AdminInfoResponse(BaseModel):
    status: str
    id: UUID
    num_masters: int
    num_users: int
    masters: List[MasterBaseResponse]


class WorkingDayResponse(BaseModel):
    id: UUID
    date: date
    start_time: int  # минуты
    end_time: int
    address: Optional[str] = None


class WorkingDaysListResponse(BaseModel):
    status: str
    working_days: List[WorkingDayResponse]





class WeekTemplateResp(BaseModel):
    id: UUID
    weekday: int
    start_time: time
    end_time: time
    address_id: uuid.UUID
    address: Optional[str] = None

class WeekTemplateResponse(StatusResponse):
    templates: List[WeekTemplateResp]

class WeekTemplateListResponse(BaseModel):
    status: str
    templates: List[WeekTemplateResponse]


class MasterAbsenceResponse(BaseModel):
    id: UUID
    start_date: date
    end_date: date
    reason: Optional[str] = None


class MasterAbsencesListResponse(BaseModel):
    status: str
    absences: List[MasterAbsenceResponse]

class AddressBaseResponse(BaseModel):
    id: UUID
    address: str
    master_id: UUID

class AddressListResponse(BaseModel):
    status: str
    addresses: List[AddressBaseResponse]

class AbsenceCreateResponse(BaseModel):
    status: str
    absence_id: uuid.UUID
    cancelled_appointments: List[str] = Field(default_factory=list)

class AbsenceResp(BaseModel):
    id: uuid.UUID
    start_date: date
    end_date: date
    reason: str

class AbsenceListResponse(StatusResponse):
    absences: Optional[List[AbsenceResp]] = List[dict]

class PriceListResponseFile():
    status: str
    prices: List[dict]

class EarningBaseResponse(BaseModel):
    id: UUID
    price: int
    date: date
    master_id: UUID

class EarningListResponse(BaseModel):
    status: str
    earnings: List[EarningBaseResponse]
    total: int = 0  # общая сумма

class PrepayBaseResponse(BaseModel):
    id: UUID
    percent: int
    start_date: date
    end_date: date
    master_id: UUID

class PrepayListResponse(BaseModel):
    status: str
    prepayments: List[PrepayBaseResponse]

class PrepayActiveResponse(BaseModel):
    status: str
    prepay: Optional[PrepayBaseResponse] = None

class MasterNotificationResponse(BaseModel):
    id: UUID
    master_id: UUID
    appointment_notification: bool
    appointment_cancel_notification: bool
    appointment_confirm_notification: bool
    guide_approved_notification: bool
    subscription_ending_notification: bool

class MasterNotificationGetResponse(StatusResponse):
    notification: MasterNotificationResponse
