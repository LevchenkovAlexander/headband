import uuid
from datetime import date

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.responses import StatusResponse, PossibleTimesResponse
from backend.database import miniapp_db_fcn, get_db_session
from backend.database.requests import AppointmentCreateRequest

router = APIRouter(
    prefix="/users",
    tags=["User"]
)


'''@router.post("/appointments/", response_model=StatusResponse)
async def create_appointment(
        appointment: AppointmentCreateRequest,
        session: AsyncSession = Depends(get_db_session)
):
    """Создание записи на приём"""
    # Проверяем доступное время
    poss_times, status = await miniapp_db_fcn.get_possible_start_time(
        master_id=appointment.master_id,
        app_date=appointment.date,
        price_id=appointment.price_id,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=400, detail=status)

    if appointment.time not in poss_times:
        raise HTTPException(status_code=400, detail="time is already taken")

    status = await miniapp_db_fcn.create_appointment(
        appointment_request=appointment,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=400, detail=status)

    return {"status": status}


@router.get("/appointments/possible-times", response_model=PossibleTimesResponse)
async def get_possible_start_times(
        master_id: uuid.UUID,
        appointment_date: date,
        price_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    """Получение доступного времени для записи"""
    poss_start, status = await miniapp_db_fcn.get_possible_start_time(
        master_id=master_id,
        app_date=appointment_date,
        price_id=price_id,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=400, detail=status)

    return {
        "status": status,
        "times": poss_start or []
    }


@router.delete("/appointments/{appointment_id}", response_model=StatusResponse)
async def cancel_appointment(
        appointment_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    """Отмена записи"""
    status = await miniapp_db_fcn.cancel_appointment(
        appointment_id=appointment_id,
        session=session
    )

    if status != "success":
        raise HTTPException(status_code=404, detail=status)

    return {"status": status}


@router.get("/appointments", response_model=AppointmentListResponse)
async def get_user_appointments(
        chat_id: int,
        session: AsyncSession = Depends(get_db_session)
):
    """Получение записей пользователя"""
    appointments = await miniapp_db_fcn.get_appointments_by_user(
        chat_id=chat_id,
        session=session
    )

    return {
        "status": "success",
        "count": len(appointments),
        "appointments": appointments
    }
'''