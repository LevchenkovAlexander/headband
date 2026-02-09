from datetime import date

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from headband.backend.database import db_functions, get_db_session
from headband.backend.database.requests import MasterUpdateRequest
from headband.backend.database.responses import AppointmentResponse, AppointmentListResponse, StatusResponse, \
    WeekTimetableResponse

router = APIRouter(
    prefix="/masters",
    tags=["Master"]
)

@router.get("/appointments/week/", response_model=WeekTimetableResponse)
async def get_week_timetable(master_id: int,
                            start_date: date,
                            session: AsyncSession = Depends(get_db_session)):
    week_appointments, status = await db_functions.get_week_timetable(master_id=master_id, date=start_date, session=session)
    return {
        "status": status,
        "week_appointments": week_appointments
    }

@router.get("/appointments/today/", response_model=AppointmentListResponse)
async def get_today_appointments(master_id: int,
                                   session: AsyncSession = Depends(get_db_session)):
    today = date.today()
    appointments, count, status, addresses, names = await db_functions.get_appointments_by_date(master_chat_id=master_id, date=today, session=session)
    a = []
    for i, appointment in enumerate(appointments):
        aresponse = AppointmentResponse.model_validate(appointment).model_dump()
        aresponse["address"] = addresses[i]
        aresponse["service_name"] = names[i]
        a.append(aresponse)
    return {
        "status": status,
        "count": count,
        "appointments": a
    }

@router.get("/appointments/", response_model=AppointmentListResponse)
async def get_appointments_by_date(master_id: int,
                                   date: date,
                                   session: AsyncSession = Depends(get_db_session)):
    appointments, count, status, addresses, names = await db_functions.get_appointments_by_date(master_chat_id=master_id, date=date, session=session)
    a = []
    for i, appointment in enumerate(appointments):
        aresponse = AppointmentResponse.model_validate(appointment).model_dump()
        aresponse["address"] = addresses[i]
        aresponse["service_name"] = names[i]
        a.append(aresponse)
    return {
        "status": status,
        "count": count,
        "appointments": a
    }

@router.patch("/profile", response_model=StatusResponse)
async def update_master_profile(update_data: MasterUpdateRequest,
                                   session: AsyncSession = Depends(get_db_session)):
    status = await db_functions.update_master(update_data=update_data, session=session)
    return {
        "status": status
    }
