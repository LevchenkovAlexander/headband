import uuid
from datetime import date, datetime

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import db_functions, get_db_session
from backend.database.requests import MasterUpdateRequest
from backend.database.responses import AppointmentResponse, AppointmentListResponse, StatusResponse, \
    WeekTimetableResponse, GuidePageResponse

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


@router.get("/appointments/today/", response_model=AppointmentListResponse)
async def get_today_appointments(
        master_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    """Получение записей мастера на сегодня"""
    today = date.today()
    appointments, count, status, addresses, names = await db_functions.get_appointments_by_date(
        master_id=master_id,
        app_date=today,
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

