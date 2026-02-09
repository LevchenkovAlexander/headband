import uuid
from datetime import date

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from headband.backend import get_db_session
from headband.backend.database import db_functions
from headband.backend.database.requests import AppointmentCreateRequest, PriceUpdateRequest
from headband.backend.database.responses import StatusResponse, PossibleTimesResponse, WeekTimetableResponse

router = APIRouter(
    prefix="/users",
    tags=["User"]
)

@router.post("/appointments/", response_model=StatusResponse)
async def create_appointment(appointment: AppointmentCreateRequest,
                             session: AsyncSession = Depends(get_db_session)):
    poss_times_dict = await get_possible_start_times(master_id=appointment.master_id, appointment_date=appointment.date, price_id=appointment.price_id, session=session)
    poss_times = poss_times_dict["times"]
    if appointment.start_time in poss_times:
        status = await db_functions.create_appointment(appointment, session=session)
    else:
        status = "time is already taken"
    return {"status": status}

@router.get("/appointments/possible-times", response_model=PossibleTimesResponse)
async def get_possible_start_times(master_id: uuid.UUID,
                                   appointment_date: date,
                                   price_id: uuid.UUID,
                                   session: AsyncSession = Depends(get_db_session)):
    poss_start, status = await db_functions.get_possible_start_time(
        master_id=master_id,
        date=appointment_date,
        price_id=price_id,
        session=session)

    return {
        "status": status,
        "times": poss_start or []
    }

@router.delete("/appointments/delete", response_model=StatusResponse)
async def cancel_appointment(id: uuid.UUID,
                             session: AsyncSession = Depends(get_db_session)
                             ):
    status = await db_functions.cancel_appointment(appointment_id=id, session=session)
    return {"status": status}

@router.get("/masters/appointments/week/", tags=["Master"], response_model=WeekTimetableResponse)
async def get_week_timetable(master_id: int,
                            start_date: date,
                            session: AsyncSession = Depends(get_db_session)):
    week_appointments, status = await db_functions.get_week_timetable(master_id=master_id, date=start_date, session=session)
    return {
        "status": status,
        "week_appointments": week_appointments
    }

@router.patch("/admins/update_price_position", tags=["Admin"], response_model=StatusResponse)
async def update_price(update_data: PriceUpdateRequest,
                              session: AsyncSession = Depends(get_db_session)):
    status = await db_functions.update_price(update_data=update_data, session=session)
    return {"status": status}

