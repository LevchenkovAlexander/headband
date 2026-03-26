import os
import uuid
from datetime import date, datetime
from typing import List

import aiofiles
from fastapi import Depends, APIRouter, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import db_functions, get_db_session
from backend.database.requests import MasterUpdateRequest, AddressCreateRequest, AddressUpdateRequest, WeekTemplate, \
    TemplateCreateRequest, TemplateUpdateRequest, WorkingDayUpdateRequest, AbsenceCreateRequest, AbsenceUpdateRequest, \
    GuideCreateRequest, GuideUpdateRequest
from backend.database.responses import AppointmentResponse, AppointmentListResponse, StatusResponse, \
    WeekTimetableResponse, GuidePageResponse, IDResponse, AddressListResponse, WeekTemplateResponse, \
    AbsenceCreateResponse, AbsenceListResponse

UPLOAD_DIR = "temps"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(
    prefix="/masters",
    tags=["Master"]
)


@router.get("/appointments/week/", response_model=WeekTimetableResponse)
async def get_week_timetable(
        master_id: uuid.UUID,
        start_date: datetime,
        session: AsyncSession = Depends(get_db_session)
):
    """Получение расписания мастера на неделю"""
    week_appointments, status = await db_functions.get_week_timetable(
        master_id=master_id,
        start_date=start_date,
        session=session
    )
    if status != "success":
        raise HTTPException(status_code=404, detail=status)

    return {
        "status": status,
        "week_appointments": week_appointments
    }



@router.get("/appointments/", response_model=AppointmentListResponse)
async def get_appointments_by_date(
        master_id: uuid.UUID,
        date: date,
        session: AsyncSession = Depends(get_db_session)
):
    """Получение записей мастера на дату"""
    appointments, count, status, addresses, names = await db_functions.get_appointments_by_date(
        master_id=master_id,
        app_date=date,
        session=session
    )

    a = []
    for i, appointment in enumerate(appointments):
        aresponse = AppointmentResponse.model_validate(appointment).model_dump()
        aresponse["address"] = addresses[i] if i < len(addresses) else None
        aresponse["service_name"] = names[i] if i < len(names) else None
        a.append(aresponse)

    return {
        "status": status,
        "count": count,
        "appointments": a
    }

@router.patch("/profile", response_model=StatusResponse)
async def update_master_profile(
    update_data: MasterUpdateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Обновление профиля мастера"""
    status = await db_functions.update_master(
        update_data=update_data,
        session=session
    )
    return {"status": status}

@router.get("/guides", response_model=GuidePageResponse)
async def get_guides(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение списка гайдов для мастера"""
    status, g_fitable, g_all = await db_functions.get_guides(
        master_id=master_id,
        session=session
    )
    return {
        "status": status,
        "guides_fit": g_fitable,
        "guides_all": g_all
    }

@router.get("/guides/{guide_id}", response_model=dict)
async def get_steps(
    guide_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение шагов конкретного гайда"""
    status, steps = await db_functions.get_steps(
        guide_id=guide_id,
        session=session
    )
    return {
        "status": status,
        "steps": steps
    }

@router.post("/guides", response_model=IDResponse)
async def create_guide(
    request: GuideCreateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    try:
        guide_id = await db_functions.create_guide(
            session=session,
            request=request
        )
        return {"status": "success", "id": guide_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/guides", response_model=StatusResponse)
async def update_guide(
    request: GuideUpdateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    status = db_functions.update_guide(session=session,
        update_data=request)
    if status != "success":
        raise HTTPException(status_code=404, detail=status)
    return {"status": status}


@router.get("/categories", response_model=dict)
async def get_master_categories(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение категорий мастера"""
    categories = await db_functions.get_master_categories(
        master_id=master_id,
        session=session
    )
    return {
        "status": "success",
        "categories": [{"id": str(cat.id), "name": cat.name} for cat in categories]
    }


@router.get("/prices", response_model=dict)
async def get_master_prices(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение прайс-листа мастера"""
    prices = await db_functions.get_prices_by_master(
        master_id=master_id,
        session=session
    )
    return {
        "status": "success",
        "prices": prices
    }

@router.get("/addresses", response_model=AddressListResponse)
async def get_master_addresses(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение всех адресов мастера"""
    addresses = await db_functions.get_addresses_by_master(
        master_id=master_id,
        session=session
    )
    return {
        "status": "success",
        "addresses": addresses
    }


@router.post("/addresses", response_model=IDResponse)
async def create_address(
    request: AddressCreateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Создание нового адреса"""
    address_id = await db_functions.create_address(
        master_id=request.master_id,
        address=request.address,
        session=session
    )
    return {
        "status": "success",
        "id": address_id
    }


@router.delete("/addresses/{address_id}", response_model=StatusResponse)
async def delete_address(
    address_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Удаление адреса"""
    status = await db_functions.delete_address(
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
    status = await db_functions.update_address(
        address_id=request.id,
        address=request.address,
        session=session
    )
    return {"status": status}

@router.post("/week_template", response_model=StatusResponse)
async def set_template(
        request: TemplateCreateRequest,
        session: AsyncSession = Depends(get_db_session)):
    """Создание шаблона недели"""
    status = await db_functions.set_week_template_full(
        master_id=request.master_id,
        templates=request.days,
        session=session
    )
    return {"status": status}

@router.get("/week-template", response_model=WeekTemplateResponse)
async def get_week_template(
    master_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение текущего шаблона недели"""
    templates = await db_functions.get_week_template_by_master(
        master_id=master_id,
        session=session
    )
    return {
        "status": "success",
        "templates": templates
    }

@router.patch("/week_template", response_model=StatusResponse)
async def update_week_template(
    request: TemplateUpdateRequest,
    session: AsyncSession = Depends(get_db_session)):
    """Обновление конкретного дня в шаблоне"""
    status = await db_functions.update_week_template(req=request, session=session)
    return {"status": status}

@router.delete("/week_template", response_model=StatusResponse)
async def delete_day_week_template(
    master_id: uuid.UUID,
    weekday: int,
    session: AsyncSession = Depends(get_db_session)):
    """Удаление дня (добавление выходного)"""
    status = await db_functions.delete_day(id=master_id, weekday=weekday, session=session)
    return {"status": status}

@router.patch("/working_day/update", response_model=StatusResponse)
async def update_working_day(
        request: WorkingDayUpdateRequest,
        session: AsyncSession = Depends(get_db_session)):
    """Обновление конкретной даты"""
    status = await db_functions.update_working_day(request=request, session=session)
    return {"status": status}

@router.post("/upload_price_list")
async def upload_file(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, detail="Invalid file type")

    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"image_{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(1024 * 1024):  # читаем по 1 МБ
            await f.write(chunk)

    return {"filename": safe_filename, "path": file_path}


@router.post("/absences", response_model=AbsenceCreateResponse)
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

    status, absence_id, cancelled = await db_functions.create_absence(
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


@router.get("/absences", response_model=AbsenceListResponse)
async def get_absences(
        master_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    """Получить список периодов отсутствия мастера"""
    absences, status = await db_functions.get_absences_by_master(
        master_id=master_id,
        session=session
    )

    return {
        "status": status,
        "absences": absences
    }


@router.delete("/absences/{absence_id}", response_model=StatusResponse)
async def delete_absence(
        absence_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    """
    Удалить период отсутствия.
    Записи, которые были отменены, НЕ восстанавливаются.
    """
    status = await db_functions.delete_absence(
        absence_id=absence_id,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=404, detail=status)

    return {"status": status}

@router.patch("/absence", response_model=StatusResponse)
async def update_absence(absence: AbsenceUpdateRequest,
                        session: AsyncSession = Depends(get_db_session)
):
    """
    Изменить период отсутствия.
    Записи, которые были отменены, НЕ восстанавливаются.
    """
    status = await db_functions.update_absence(
        update_data=absence,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=404, detail=status)

    return {"status": status}