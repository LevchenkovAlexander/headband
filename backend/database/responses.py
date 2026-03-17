from datetime import date, time
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ==================== BASE ====================
class StatusResponse(BaseModel):
    status: str


# ==================== APPOINTMENTS ====================
class AppointmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    master_id: UUID
    date: date
    time: time
    final_price: int
    price_id: UUID
    working_day_id: UUID
    address: Optional[str] = None
    service_name: Optional[str] = None


class AppointmentListResponse(BaseModel):
    status: str
    count: int
    appointments: List[AppointmentResponse]


class PossibleTimesResponse(BaseModel):
    status: str
    times: List[time]


class WeekTimetableResponse(BaseModel):
    status: str
    week_appointments: List[List[AppointmentResponse]]


# ==================== GUIDES ====================
class GuideBaseResponse(BaseModel):
    id: UUID
    steps: str
    author: UUID


class GuidePageResponse(BaseModel):
    status: str
    guides_fit: List[GuideBaseResponse]
    guides_all: List[GuideBaseResponse]


class GuideStepResponse(BaseModel):
    status: str
    steps: Optional[str] = None


# ==================== MASTERS ====================
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


# ==================== USERS ====================
class UserBaseResponse(BaseModel):
    id: UUID
    chat_id: int
    username: Optional[str] = None


class UserResponseMainPage(BaseModel):
    status: str
    appointments: List[AppointmentResponse]
    categories: List[str]


class MasterListItem(BaseModel):
    id: UUID
    name: str
    address: Optional[str] = None
    subcategories: List[str] = Field(default_factory=list)


class UserResponseMastersPage(BaseModel):
    status: str
    masters: List[MasterListItem]


# ==================== CATEGORIES ====================
class CategoryBaseResponse(BaseModel):
    id: UUID
    name: str


class CategoriesResponse(BaseModel):
    status: str
    categories: List[CategoryBaseResponse]


# ==================== PRICES ====================
class PriceBaseResponse(BaseModel):
    id: UUID
    name: str
    price: int
    category_id: UUID
    approximate_time: int  # минуты
    master_id: UUID


class PriceListResponse(BaseModel):
    status: str
    prices: List[PriceBaseResponse]


# ==================== ADMIN ====================
class AdminInfoResponse(BaseModel):
    status: str
    id: UUID
    num_masters: int
    num_users: int
    masters: List[MasterBaseResponse]


# ==================== WORKING DAYS ====================
class WorkingDayResponse(BaseModel):
    id: UUID
    date: date
    start_time: int  # минуты
    end_time: int
    address: Optional[str] = None


class WorkingDaysListResponse(BaseModel):
    status: str
    working_days: List[WorkingDayResponse]


# ==================== WEEK TEMPLATE ====================
class WeekTemplateResponse(BaseModel):
    id: UUID
    weekday: int  # 1-7
    start_time: int  # минуты
    end_time: int
    address: Optional[str] = None


class WeekTemplateListResponse(BaseModel):
    status: str
    templates: List[WeekTemplateResponse]


# ==================== MASTER ABSENCES ====================
class MasterAbsenceResponse(BaseModel):
    id: UUID
    start_date: date
    end_date: date
    reason: Optional[str] = None


class MasterAbsencesListResponse(BaseModel):
    status: str
    absences: List[MasterAbsenceResponse]