import uuid
from datetime import time, date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db_session, miniapp_db_fcn
from backend.database.responses import IDResponse, StatusResponse


#Requests
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

class AddressCreateRequest(BaseModel):
    master_id: uuid.UUID
    address: str

class AddressUpdateRequest(BaseModel):
    id: uuid.UUID
    address: str

class WorkingDayUpdateRequest(BaseModel):
    master_id: uuid.UUID
    day_date: date
    start_time: time
    end_time: time
    address_id: uuid.UUID

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

#Responses
class AbsenceCreateResponse(BaseModel):
    status: str
    absence_id: uuid.UUID
    cancelled_appointments: List[str] = Field(default_factory=list)

class AddressBaseResponse(BaseModel):
    id: uuid.UUID
    address: str
    master_id: uuid.UUID

class AddressListResponse(BaseModel):
    status: str
    addresses: List[AddressBaseResponse]

class WeekTemplateResp(BaseModel):
    id: uuid.UUID
    weekday: int
    start_time: time
    end_time: time
    address_id: uuid.UUID
    address: Optional[str] = None

class WeekTemplateResponse(StatusResponse):
    templates: List[WeekTemplateResp]

class AbsenceResp(BaseModel):
    id: uuid.UUID
    start_date: date
    end_date: date
    reason: str

class AbsenceListResponse(StatusResponse):
    absences: Optional[List[AbsenceResp]] = List[dict]

class DayResponse(BaseModel):
    day: date
    start_time: time
    end_time: time
    address: str

#API
router = APIRouter(
    prefix="/master/profile/schedule",
    tags=["Master.Profile"])


@router.get("/addresses", response_model=AddressListResponse)
async def get_master_addresses(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение всех адресов мастера"""
    addresses = await miniapp_db_fcn.get_addresses_by_master(
        master_id=master_id,
        session=session
    )
    return {
        "status": "success",
        "addresses": addresses
    }

@router.post("/create_address", response_model=IDResponse)
async def create_address(
    request: AddressCreateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Создание нового адреса"""
    address_id = await miniapp_db_fcn.create_address(
        master_id=request.master_id,
        address=request.address,
        session=session
    )
    return {
        "status": "success",
        "id": address_id
    }

@router.delete("/delete_address/{address_id}", response_model=StatusResponse)
async def delete_address(
    address_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Удаление адреса"""
    status = await miniapp_db_fcn.delete_address(
        address_id=address_id,
        session=session
    )
    return {"status": status}


@router.patch("/addresses/update", response_model=StatusResponse)
async def update_address(
    request: AddressUpdateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Обновление адреса"""
    status = await miniapp_db_fcn.update_address(
        address_id=request.id,
        address=request.address,
        session=session
    )
    return {"status": status}

@router.post("/set_template", response_model=StatusResponse)
async def set_template(
        request: TemplateCreateRequest,
        session: AsyncSession = Depends(get_db_session)):
    """Создание шаблона недели"""
    status = await miniapp_db_fcn.set_week_template_full(
        master_id=request.master_id,
        templates=request.days,
        session=session
    )
    return {"status": status}

@router.get("/get_template", response_model=WeekTemplateResponse)
async def get_week_template(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение текущего шаблона недели"""
    templates = await miniapp_db_fcn.get_week_template_by_master(
        master_id=master_id,
        session=session
    )
    return {
        "status": "success",
        "templates": templates
    }

@router.patch("/update_template", response_model=StatusResponse)
async def update_week_template(
    request: List[TemplateUpdateRequest],
    session: AsyncSession = Depends(get_db_session)):
    """Обновление конкретного дня в шаблоне"""
    status = await miniapp_db_fcn.update_week_template(templates=request, session=session)
    return {"status": status}

@router.delete("/day_off_template", response_model=StatusResponse)
async def delete_day_week_template(
    master_id: uuid.UUID,
    weekday: int,
    session: AsyncSession = Depends(get_db_session)):
    """Удаление дня (добавление выходного)"""
    status = await miniapp_db_fcn.delete_day(id=master_id, weekday=weekday, session=session)
    return {"status": status}

@router.get("/working_day", response_model=DayResponse)
async def get_working_day(master_id: uuid.UUID,
                          day: date,
                          session: AsyncSession = Depends(get_db_session)):
    day_resp = await miniapp_db_fcn.get_day(master_id=master_id, day=day, session=session)
    return {"status": "success",
            "day": day,
            "start_time": day_resp.start_time,
            "end_time": day_resp.end_time,
            "address": await miniapp_db_fcn.get_address_by_id(id=day_resp.address_id, session=session)}

@router.patch("/working_day/update", response_model=StatusResponse)
async def update_working_day(
        request: WorkingDayUpdateRequest,
        session: AsyncSession = Depends(get_db_session)):
    """Обновление конкретной даты"""
    status = await miniapp_db_fcn.update_working_day(request=request, session=session)
    return {"status": status}


@router.post("/set_absence", response_model=AbsenceCreateResponse)
async def create_absence(
        request: AbsenceCreateRequest,
        session: AsyncSession = Depends(get_db_session)
):
    """
    Добавить период отсутствия мастера.
    Все записи в этот период будут автоматически отменены.
    """
    if request.start_date > request.end_date:
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")

    if request.start_date < date.today():
        raise HTTPException(status_code=400, detail="start_date cannot be in the past")

    status, absence_id, cancelled = await miniapp_db_fcn.create_absence(
        master_id=request.master_id,
        start_date=request.start_date,
        end_date=request.end_date,
        reason=request.reason,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=400, detail=status)

    return {
        "status": status,
        "absence_id": absence_id,
        "cancelled_appointments": cancelled
    }

@router.get("/absence", response_model=AbsenceListResponse)
async def get_absences(
        master_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    """Получить список периодов отсутствия мастера"""
    absences, status = await miniapp_db_fcn.get_absences_by_master(
        master_id=master_id,
        session=session
    )

    return {
        "status": status,
        "absences": absences
    }


@router.delete("/delete_absences/{absence_id}", response_model=StatusResponse)
async def delete_absence(
        absence_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    """
    Удалить период отсутствия.
    Записи, которые были отменены, НЕ восстанавливаются.
    """
    status = await miniapp_db_fcn.delete_absence(
        absence_id=absence_id,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=404, detail=status)

    return {"status": status}

@router.patch("/update_absence", response_model=StatusResponse)
async def update_absence(absence: AbsenceUpdateRequest,
                        session: AsyncSession = Depends(get_db_session)
):
    """
    Изменить период отсутствия.
    Записи, которые были отменены, НЕ восстанавливаются.
    """
    status = await miniapp_db_fcn.update_absence(
        update_data=absence,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=404, detail=status)

    return {"status": status}
