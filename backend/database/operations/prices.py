import uuid
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import PriceModel, CategoryModel
from backend.database.requests import PriceCreateRequest, PriceUpdateRequest


async def create_price_position(
    price_position: PriceCreateRequest,
    session: AsyncSession
):
    """Создание позиции прайса"""
    price_dict = price_position.model_dump()
    return await PriceModel.create(session=session, data=price_dict)


async def update_price(
    update_data: PriceUpdateRequest,
    session: AsyncSession
):
    """Обновление позиции прайса"""
    price_to_upd = update_data.model_dump(exclude_unset=True)
    return await PriceModel.update(
        session=session,
        price_id=update_data.id,
        update_data=price_to_upd
    )


async def delete_price(
    price_id: uuid.UUID,
    session: AsyncSession
):
    """Удаление позиции прайса"""
    return await PriceModel.delete(session=session, price_id=price_id)


async def get_prices_by_master(master_id: uuid.UUID, session: AsyncSession):
    prices = await PriceModel.get_by_master_id(session=session, master_id=master_id)
    resp = [{
        "id": str(p.id),
        "name": p.name,
        "price": p.price,
        "category": await CategoryModel.get_by_id(session=session, category_id=p.category_id),
        "approximate_time": p.approximate_time,
        "master_id": str(p.master_id)
    } for p in prices]
    return resp


async def get_prices_by_category(
    master_id: uuid.UUID,
    category_id: uuid.UUID,
    session: AsyncSession
):
    prices = await PriceModel.get_by_category(
        session=session,
        master_id=master_id,
        category_id=category_id
    )
    resp = [{
        "id": str(p.id),
        "name": p.name,
        "price": p.price,
        "category": await CategoryModel.get_by_id(session=session, category_id=p.category_id),
        "approximate_time": p.approximate_time,
        "master_id": str(p.master_id)
    } for p in prices]
    return "success", resp


async def create_pricelist(data: List, master_id: uuid.UUID, session: AsyncSession):
    for d in data:
        p = {}
        p["name"] = d["name"]
        p["price"] = d["price"]
        p["approximate_time"] = d["approximate_time"]
        p["category_id"] = await CategoryModel.get_by_name(session=session, name=d["category"])
        p["master_id"] = master_id
        d["id"] = await PriceModel.create(session=session, data=p)
    return data
