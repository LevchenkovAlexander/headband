import uuid
from datetime import date

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession


from backend.database import db_functions, get_db_session
from backend.database.requests import AppointmentCreateRequest, PriceUpdateRequest
from backend.database.responses import StatusResponse, PossibleTimesResponse, WeekTimetableResponse, \
    OrganizationFilterResponse

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

@router.get("/filter/organizations", response_model=OrganizationFilterResponse)
async def get_organizatons(user_id: int,
                           session: AsyncSession = Depends(get_db_session())):
    status, organizations = await db_functions.get_organization_filter(user_id=user_id, session=session)
    return {"status": status,
            "organizations": organizations}




