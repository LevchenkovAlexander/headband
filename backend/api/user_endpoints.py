import uuid
from datetime import date

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession


from headband.backend.database import db_functions, get_db_session
from headband.backend.database.requests import AppointmentCreateRequest, MastersPageRequest
from headband.backend.database.responses import StatusResponse, PossibleTimesResponse, \
    UserResponseMainPage, UserResponseMastersPage

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

@router.get("/main_page", response_model=UserResponseMainPage)
async def get_main_page(chat_id: int,
                   session: AsyncSession = Depends(get_db_session)):
    appointments = await db_functions.get_appointments_by_user(chat_id=chat_id, session=session)
    categories = await db_functions.get_categories_by_user(chat_id=chat_id, session=session)
    return {"status": "success",
            "appointments": appointments,
            "categories": categories}
@router.get("/filter/organizations", response_model=OrganizationFilterResponse)
async def get_organizatons(user_id: int,
                           session: AsyncSession = Depends(get_db_session())):
    status, organizations = await db_functions.get_organization_filter(user_id=user_id, session=session)
    return {"status": status,
            "organizations": organizations}



@router.post("/masters_page", response_model=UserResponseMastersPage)
async def get_masters_page(request: MastersPageRequest,
                           session: AsyncSession = Depends(get_db_session)):
    response, success = await db_functions.get_masters_by_category_and_user(chat_id=request.chat_id, category=request.category, session=session, filter=request.filter)
    return {"status": success,
            "masters": response}