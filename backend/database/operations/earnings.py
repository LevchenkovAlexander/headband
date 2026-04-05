import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import EarningsModel, AppointmentModel


async def create_earning(
        master_id: uuid.UUID,
        appointment_id: uuid.UUID,
        session: AsyncSession
):
    """Создание записи о доходе"""
    appo = await AppointmentModel.get_by_id(appointment_id=appointment_id, session=session)
    await AppointmentModel.confirm(session=session, id=appointment_id)

    data = {
        "master_id": master_id,
        "price": appo.final_price,
        "date": appo.date
    }

    earning_id = await EarningsModel.create(session=session, data=data)
    return "success", earning_id


async def get_earnings_by_date_range(
        master_id: uuid.UUID,
        start_date: date,
        end_date: date,
        session: AsyncSession
):
    """Получение доходов за период"""
    earnings = await EarningsModel.get_by_date_range(
        session=session,
        master_id=master_id,
        start_date=start_date,
        end_date=end_date
    )
    total = sum(e.price for e in earnings)
    return "success", total, len(earnings)


async def delete_earning(
        appo_id: uuid.UUID,
        session: AsyncSession
):
    """Удаление записи о доходе"""
    return await AppointmentModel.cancel(session=session, id=appo_id)