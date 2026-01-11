from typing import Annotated

from fastapi import Depends
from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date

engine = create_async_engine('postgresql+asyncpg://username:password@localhost/dbname')

session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with session as s:
        yield s

SessionDep = Annotated[AsyncSession, Depends(get_session)]

async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class Base(DeclarativeBase):
    pass

class AppointmentModel(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[float] = mapped_column(ForeignKey("users.id"))
    master_id: Mapped[float] = mapped_column(ForeignKey("masters.id"))
    date: Mapped[date]
    time: Mapped[date]
    service_id: Mapped[int]

    @classmethod
    async def create(cls, session: SessionDep, **kwargs):
        appointment = cls(**kwargs)
        session.add(appointment)
        await session.commit()
        await session.refresh(appointment)
        return appointment

    @classmethod
    async def delete(cls, session: SessionDep, id):
        appointment = session.get(cls, id)
        if appointment:
            await session.delete(appointment)
            await session.commit()
            return True
        return False


class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str]
    unique_code: Mapped[int]

class MasterModel(Base):
    __tablename__ = "masters"

    id: Mapped[float] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    photo_path: Mapped[str]
    name: Mapped[str]
    working_day_start: Mapped[date]
    working_day_end: Mapped[date]

    @classmethod
    async def get_master_by_id(cls, session: SessionDep, id):
        master = session.get(cls, id)
        if master:
            return master
        raise ValueError("There is no such master ID")
class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[float] = mapped_column(primary_key=True)
    name: Mapped[str]
    unique_code: Mapped[int]
class ServiceModel(Base):
    __tablename__ = "services"

    id: Mapped[float] = mapped_column(primary_key=True)
    name: Mapped[str]
    approximate_time: Mapped[int]
    category: Mapped[str]

class PriceModel(Base):
    __tablename__ = "prices"

    id: Mapped[float] = mapped_column(primary_key=True)
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id"))
    price: Mapped[int]
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
