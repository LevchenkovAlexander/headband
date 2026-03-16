import logging
import os
import uuid
from contextlib import asynccontextmanager
from enum import Enum
from typing import List, Optional, AsyncGenerator

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, select, update, delete, text, func, BigInteger, String, Date, Integer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import time, date
from sqlalchemy import inspect

logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

db_address = os.getenv('DB_ADDRESS')
engine = create_async_engine(db_address)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def setup_database():
    try:
        async with engine.begin() as conn:
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


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()


class Base(DeclarativeBase):
    pass


class Week(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class AdminModel(Base):
    __tablename__ = "admins"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    appointments: Mapped[List["AppointmentModel"]] = relationship(
        "AppointmentModel",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @classmethod
    async def create(cls, session: AsyncSession, data: dict):
        user = cls(**data)
        session.add(user)
        await session.flush()
        return user.id

    @classmethod
    async def get_by_chat_id(cls, session: AsyncSession, chat_id: int):
        query = select(cls).where(cls.chat_id == chat_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: uuid.UUID):
        query = select(cls).where(cls.id == user_id)
        result = await session.execute(query)
        return result.scalars().first()


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)

    # Relationships
    master_categories: Mapped[List["MasterCategoryModel"]] = relationship(
        "MasterCategoryModel",
        back_populates="category",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    prices: Mapped[List["PriceModel"]] = relationship(
        "PriceModel",
        back_populates="category",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @classmethod
    async def get_all(cls, session: AsyncSession):
        query = select(cls)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, category_id: uuid.UUID):
        query = select(cls).where(cls.id == category_id)
        result = await session.execute(query)
        return result.scalars().first()


class MasterModel(Base):
    __tablename__ = "masters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    working_day_start: Mapped[time]
    working_day_end: Mapped[time]

    # Relationships
    appointments: Mapped[List["AppointmentModel"]] = relationship(
        "AppointmentModel",
        back_populates="master",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    working_days: Mapped[List["WorkingDayModel"]] = relationship(
        "WorkingDayModel",
        back_populates="master",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    week_templates: Mapped[List["WeekTemplateModel"]] = relationship(
        "WeekTemplateModel",
        back_populates="master",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    master_absences: Mapped[List["MasterAbsenceModel"]] = relationship(
        "MasterAbsenceModel",
        back_populates="master",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    master_categories: Mapped[List["MasterCategoryModel"]] = relationship(
        "MasterCategoryModel",
        back_populates="master",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    prices: Mapped[List["PriceModel"]] = relationship(
        "PriceModel",
        back_populates="master",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @classmethod
    async def create(cls, session: AsyncSession, data: dict):
        master = cls(**data)
        session.add(master)
        await session.flush()
        return master.id

    @classmethod
    async def get_by_id(cls, session: AsyncSession, master_id: uuid.UUID):
        query = select(cls).where(cls.id == master_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_by_chat_id(cls, session: AsyncSession, chat_id: int):
        query = select(cls).where(cls.chat_id == chat_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_categories(cls, session: AsyncSession, master_id: uuid.UUID):
        query = select(CategoryModel).join(MasterCategoryModel).where(MasterCategoryModel.master_id == master_id)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def update(cls, session: AsyncSession, master_id: uuid.UUID, update_data: dict):
        query = update(cls).where(cls.id == master_id).values(**update_data)
        await session.execute(query)
        return "success"

class MasterCategoryModel(Base):
    __tablename__ = "master_categories"

    master_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("masters.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    master: Mapped["MasterModel"] = relationship("MasterModel", back_populates="master_categories")
    category: Mapped["CategoryModel"] = relationship("CategoryModel", back_populates="master_categories")



class WorkingDayModel(Base):
    __tablename__ = "working_days"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    master_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("masters.id", ondelete="CASCADE"))
    day_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time]
    end_time: Mapped[time]
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    master: Mapped["MasterModel"] = relationship("MasterModel", back_populates="working_days")
    appointments: Mapped[List["AppointmentModel"]] = relationship(
        "AppointmentModel",
        back_populates="working_day",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @classmethod
    async def create(cls, session: AsyncSession, data: dict):
        working_day = cls(**data)
        session.add(working_day)
        await session.flush()
        return working_day.id

    @classmethod
    async def get_by_master_and_date(cls, session: AsyncSession, master_id: uuid.UUID, day_date: date):
        query = select(cls).where(cls.master_id == master_id, cls.day_date == day_date)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_by_master_id(cls, session: AsyncSession, master_id: uuid.UUID):
        query = select(cls).where(cls.master_id == master_id)
        result = await session.execute(query)
        return result.scalars().all()


class WeekTemplateModel(Base):
    __tablename__ = "week_template"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    master_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("masters.id", ondelete="CASCADE"))
    weekday: Mapped[int] = mapped_column(BigInteger)
    start_time: Mapped[time]
    end_time: Mapped[time]
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    master: Mapped["MasterModel"] = relationship("MasterModel", back_populates="week_templates")

    @classmethod
    async def create(cls, session: AsyncSession, data: dict):
        template = cls(**data)
        session.add(template)
        await session.flush()
        return template.id

    @classmethod
    async def get_by_master_id(cls, session: AsyncSession, master_id: uuid.UUID):
        query = select(cls).where(cls.master_id == master_id)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_master_and_weekday(cls, session: AsyncSession, master_id: uuid.UUID, weekday: int):
        query = select(cls).where(cls.master_id == master_id, cls.weekday == weekday)
        result = await session.execute(query)
        return result.scalars().first()


class MasterAbsenceModel(Base):
    __tablename__ = "master_absences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    master_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("masters.id", ondelete="CASCADE"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    master: Mapped["MasterModel"] = relationship("MasterModel", back_populates="master_absences")

    @classmethod
    async def create(cls, session: AsyncSession, data: dict):
        absence = cls(**data)
        session.add(absence)
        await session.flush()
        return absence.id

    @classmethod
    async def get_by_master_id(cls, session: AsyncSession, master_id: uuid.UUID):
        query = select(cls).where(cls.master_id == master_id)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def is_absent(cls, session: AsyncSession, master_id: uuid.UUID, check_date: date):
        query = select(cls).where(
            cls.master_id == master_id,
            cls.start_date <= check_date,
            cls.end_date >= check_date
        )
        result = await session.execute(query)
        return result.scalars().first() is not None


# ==================== PRICES ====================
class PriceModel(Base):
    __tablename__ = "prices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(BigInteger)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"))
    approximate_time: Mapped[int] = mapped_column(BigInteger)
    master_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("masters.id", ondelete="CASCADE"))

    # Relationships
    category: Mapped["CategoryModel"] = relationship("CategoryModel", back_populates="prices")
    master: Mapped["MasterModel"] = relationship("MasterModel", back_populates="prices")
    appointments: Mapped[List["AppointmentModel"]] = relationship(
        "AppointmentModel",
        back_populates="price",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @classmethod
    async def create(cls, session: AsyncSession, data: dict):
        price = cls(**data)
        session.add(price)
        await session.flush()
        return price.id

    @classmethod
    async def get_by_id(cls, session: AsyncSession, price_id: uuid.UUID):
        query = select(cls).where(cls.id == price_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_by_master_id(cls, session: AsyncSession, master_id: uuid.UUID):
        query = select(cls).where(cls.master_id == master_id)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_category(cls, session: AsyncSession, master_id: uuid.UUID, category_id: uuid.UUID):
        query = select(cls).where(cls.master_id == master_id, cls.category_id == category_id)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def update(cls, session: AsyncSession, price_id: uuid.UUID, update_data: dict):
        query = update(cls).where(cls.id == price_id).values(**update_data)
        await session.execute(query)
        return "success"

    @classmethod
    async def delete(cls, session: AsyncSession, price_id: uuid.UUID):
        obj = await session.get(cls, price_id)
        if obj:
            await session.delete(obj)
            return "success"
        return "no such price"


# ==================== APPOINTMENTS ====================
class AppointmentModel(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    master_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("masters.id", ondelete="CASCADE"))
    date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(String)
    final_price: Mapped[int] = mapped_column(BigInteger)
    price_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("prices.id", ondelete="CASCADE"))
    working_day_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("working_days.id", ondelete="CASCADE"))

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="appointments")
    master: Mapped["MasterModel"] = relationship("MasterModel", back_populates="appointments")
    price: Mapped["PriceModel"] = relationship("PriceModel", back_populates="appointments")
    working_day: Mapped["WorkingDayModel"] = relationship("WorkingDayModel", back_populates="appointments")

    @classmethod
    async def create(cls, session: AsyncSession, data: dict):
        appointment = cls(**data)
        session.add(appointment)
        await session.flush()
        return appointment.id

    @classmethod
    async def get_by_master_and_date(cls, session: AsyncSession, master_id: uuid.UUID, app_date: date):
        query = select(cls).where(cls.master_id == master_id, cls.date == app_date).order_by(cls.time)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_user_id(cls, session: AsyncSession, user_id: uuid.UUID):
        query = select(cls).where(cls.user_id == user_id).order_by(cls.date, cls.time)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, appointment_id: uuid.UUID):
        query = select(cls).where(cls.id == appointment_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def delete(cls, session: AsyncSession, appointment_id: uuid.UUID):
        obj = await session.get(cls, appointment_id)
        if obj:
            await session.delete(obj)
            return "success"
        return "no such appointment"


class GuidesModel(Base):
    __tablename__ = "guides"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    steps: Mapped[str] = mapped_column(String)
    author: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))

    @classmethod
    async def get_all(cls, session: AsyncSession):
        query = select(cls)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, guide_id: uuid.UUID):
        query = select(cls).where(cls.id == guide_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def create(cls, session: AsyncSession, data: dict):
        guide = cls(**data)
        session.add(guide)
        await session.flush()
        return guide.id