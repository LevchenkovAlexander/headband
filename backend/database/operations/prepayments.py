import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import PrepayModel


async def create_prepayment(
        master_id: uuid.UUID,
        percent: int,
        start_date: date,
        end_date: date,
        session: AsyncSession
):
    """Создание периода предоплаты"""
    if start_date > end_date:
        return "error: start_date > end_date", uuid.UUID(int=0)

    data = {
        "master_id": master_id,
        "percent": percent,
        "start_date": start_date,
        "end_date": end_date
    }
    prepay_id = await PrepayModel.create(session=session, data=data)
    return "success", prepay_id


async def get_prepayments_by_master(
        master_id: uuid.UUID,
        session: AsyncSession
):
    """Получение всех периодов предоплаты мастера"""
    prepayments = await PrepayModel.get_by_master_id(session=session, master_id=master_id)
    resp = [{
        "id": p.id,
        "percent": p.percent,
        "start_date": p.start_date,
        "end_date": p.end_date,
        "master_id": p.master_id
    } for p in prepayments]
    return "success", resp


async def get_active_prepayment(
        master_id: uuid.UUID,
        check_date: date,
        session: AsyncSession
):
    """Получение активного периода предоплаты на дату"""
    prepay = await PrepayModel.get_active_by_date(
        session=session,
        master_id=master_id,
        check_date=check_date
    )
    if prepay:
        resp = {
            "id": prepay.id,
            "percent": prepay.percent,
            "start_date": prepay.start_date,
            "end_date": prepay.end_date,
            "master_id": prepay.master_id
        }
        return "success", resp
    return "no active prepayment", None


async def update_prepayment(
        prepay_id: uuid.UUID,
        update_data: dict,
        session: AsyncSession
):
    """Обновление периода предоплаты"""
    return await PrepayModel.update(session=session, prepay_id=prepay_id, update_data=update_data)


async def delete_prepayment(
        prepay_id: uuid.UUID,
        session: AsyncSession
):
    """Удаление периода предоплаты"""
    return await PrepayModel.delete(session=session, prepay_id=prepay_id)
