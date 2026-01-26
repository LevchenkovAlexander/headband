import logging
from enum import Enum
from typing import List

from sqlalchemy import ForeignKey, select, Column, Integer, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import time, datetime, date, timedelta
from sqlalchemy import inspect

engine = create_async_engine('postgresql+asyncpg://postgres:1234@localhost/headband')

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


SessionDep = AsyncSession


async def setup_database():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

            tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
            logging.info(f"Таблицы в базе данных: {tables}")

            return True
    except Exception as e:
        logging.error(f"Ошибка создания БД: {e}")
        return False

async def close_connection():
    if engine:
        await engine.dispose()

class Base(DeclarativeBase):
    pass

class AppointmentModel(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    master_id = Column(Integer, ForeignKey("masters.id"))
    date: Mapped[date]
    start_time: Mapped[time]
    end_time: Mapped[time]
    service_id = Column(Integer, ForeignKey("services.id"))

    @classmethod
    async def create(cls, session: SessionDep, data: dict):
        appointment = cls(**data)
        session.add(appointment)
        await session.commit()
        await session.refresh(appointment)
        return "success"

    @classmethod
    async def get_by_master_and_date(cls, session: SessionDep, master_id: int, date: datetime.date) -> List['AppointmentModel']:
        query = select(cls).where(
            cls.master_id == master_id,
            cls.date == date
        ).order_by(cls.start_time)

        result = await session.execute(query)
        appointments = result.scalars().all()

        return list(appointments)  # Возвращаем список объектов

    @classmethod
    async def delete(cls, session: SessionDep, id: int):
        appointment = session.get(cls, id)
        if appointment:
            await session.delete(appointment)
            await session.commit()
            return "success"
        return "no such id"


class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str]
    name: Mapped[str]
    admin_id: Mapped[int]

    @classmethod
    async def check(cls, session: SessionDep, id: int):
        organization = await session.get(cls, ident=id)
        if organization is None:
            return False
        return True
    @classmethod
    async def create(cls, session: SessionDep, data: dict):
        user = cls(**data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return True

class MasterModel(Base):
    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    username: Mapped[str]
    photo_path: Mapped[str]
    full_name: Mapped[str]
    working_day_start: Mapped[time]
    working_day_end: Mapped[time]
    day_off: Mapped[str]

    @classmethod
    async def create(cls, session: SessionDep, data: dict):
        master = cls(**data)
        session.add(master)
        await session.commit()
        await session.refresh(master)
        return True

    @classmethod
    async def get_master_by_id(cls, session: SessionDep, id: int):
        query = select(cls).where(
            cls.id == id
        )
        result = await session.execute(query)
        master = result.scalar_one_or_none()
        return master

    @classmethod
    async def update_master(cls, session: SessionDep, id: int, update_data: dict):
        query = (
            update(cls)
            .where(cls.id == id)
            .values(**update_data)
            .returning(cls)
        )
        result = await session.execute(query)
        updated_master = result.scalar_one_or_none()
        await session.commit()
        return updated_master

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    @classmethod
    async def create(cls, session: SessionDep, data: dict):
        user = cls(**data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return True
class ServiceModel(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    approximate_time: Mapped[timedelta]
    category: Mapped[str]

    @classmethod
    async def get_service_by_id(cls, session: SessionDep, id: int):
        query = select(cls).where(
            cls.id == id
        )
        result = await session.execute(query)
        service = result.scalar_one_or_none()
        return service

class PriceModel(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(primary_key=True)
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id"))
    price: Mapped[int]
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))

class Week(Enum):
    MONDAY = "1"
    TUESDAY = "2"
    WEDNESDAY = "3"
    THURSDAY = "4"
    FRIDAY = "5"
    SATURDAY = "6"
    SUNDAY = "7"