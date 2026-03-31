import logging
import os
import uuid
from enum import Enum
from typing import List, Optional, AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, select, update, BigInteger, String, Date, text, delete, and_
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import time, date
from sqlalchemy import inspect

logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
load_dotenv()
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
            '''tables_result = await conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            )
            tables = [row[0] for row in tables_result.fetchall()]

            await conn.execute(text("SET CONSTRAINTS ALL DEFERRED"))

            for table in tables:
                try:
                    await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                    logging.info(f"Таблица {table} удалена")
                except Exception as e:
                    logging.warning(f"Ошибка при удалении таблицы {table}: {e}")'''

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

class GuideStatus(Enum):
    CONFIRMED = 1
    PENDING = 2
    DENIED = 3

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

    @classmethod
    async def create(cls, session: AsyncSession, data: dict):
        category = cls(**data)
        session.add(category)
        await session.flush()
        return "success"

    @classmethod
    async def get_by_name(cls, session: AsyncSession, name: str):
        query = select(cls).where(cls.name == name)
        result = await session.execute(query)
        return result.scalars().first()


class MasterModel(Base):
    __tablename__ = "masters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id_tg: Mapped[int] = mapped_column(BigInteger, nullable=True)
    username_tg: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    chat_id_max: Mapped[int] = mapped_column(BigInteger, nullable=True)
    username_max: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    telephone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    master_link_id: Mapped[uuid.UUID]
    user_link_id: Mapped[uuid.UUID]

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
    addresses: Mapped[List["AddressModel"]] = relationship(
        "AddressModel",
        back_populates="master",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    earnings: Mapped[List["EarningsModel"]] = relationship(
        "EarningsModel",
        back_populates="master",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    prepayments: Mapped[List["PrepayModel"]] = relationship(
        "PrepayModel",
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

    @classmethod
    async def get_categories_by_master(cls, id: uuid.UUID, session: AsyncSession):
        query = select(cls).where(cls.master_id == id)
        result = await session.execute(query)
        categories = result.scalars().all()
        category_ids = [cat.id for cat in categories]
        return category_ids



class WorkingDayModel(Base):
    __tablename__ = "working_days"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    master_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("masters.id", ondelete="CASCADE"))
    day_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time]
    end_time: Mapped[time]
    address_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id", ondelete="CASCADE"))

    # Relationships
    master: Mapped["MasterModel"] = relationship("MasterModel", back_populates="working_days")
    address: Mapped["AddressModel"] = relationship("AddressModel", back_populates="working_days")
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

    @classmethod
    async def get_by_id(cls, session: AsyncSession, id: uuid.UUID):
        query = select(cls).where(cls.id == id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_by_id_and_dates(cls, id: uuid.UUID, sd: date, ed: date, session: AsyncSession):
        query = select(WorkingDayModel).where(
            WorkingDayModel.master_id == id,
            WorkingDayModel.day_date >= sd,
            WorkingDayModel.day_date <= ed
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def update(cls, session: AsyncSession, wd_id: uuid.UUID, update_data: dict):
        query = update(cls).where(cls.id == wd_id).values(**update_data)
        await session.execute(query)
        return "success"


class WeekTemplateModel(Base):
    __tablename__ = "week_template"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    master_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("masters.id", ondelete="CASCADE"))
    weekday: Mapped[int]
    start_time: Mapped[time]
    end_time: Mapped[time]
    address_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id", ondelete="CASCADE"))

    # Relationships
    master: Mapped["MasterModel"] = relationship("MasterModel", back_populates="week_templates")
    address: Mapped["AddressModel"] = relationship("AddressModel", back_populates="week_templates")

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

    @classmethod
    async def delete_by_master_id_weekday(cls, session: AsyncSession, master_id: uuid.UUID, weekday: int) -> str:
        query = delete(cls).where(and_(cls.master_id == master_id, cls.weekday == weekday))
        await session.execute(query)
        return "success"

    @classmethod
    async def update(cls, session: AsyncSession, template_id: uuid.UUID, update_data: dict) -> str:
        query = update(cls).where(cls.id == template_id).values(**update_data)
        await session.execute(query)
        return "success"

class MasterAbsenceModel(Base):
    __tablename__ = "master_absences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    master_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("masters.id", ondelete="CASCADE"))
    start_date: Mapped[date]
    end_date: Mapped[date]
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
    async def delete(cls, session: AsyncSession, absence_id: uuid.UUID) -> str:
        obj = await session.get(cls, absence_id)
        if obj:
            await session.delete(obj)
            return "success"
        return "absence not found"

    @classmethod
    async def is_absent(cls, session: AsyncSession, master_id: uuid.UUID, check_date: date):
        query = select(cls).where(
            cls.master_id == master_id,
            cls.start_date <= check_date,
            cls.end_date >= check_date
        )
        result = await session.execute(query)
        return result.scalars().first() is not None

    @classmethod
    async def update(cls, session: AsyncSession, id: uuid.UUID, master_id: uuid.UUID, update_data: dict) -> str:
        query = update(cls).where(cls.id == id, cls.master_id == master_id).values(**update_data)
        await session.execute(query)
        return "success"

class AddressModel(Base):
    __tablename__ = "addresses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    master_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("masters.id", ondelete="CASCADE"))
    address: Mapped[str]

    # Relationships
    master: Mapped["MasterModel"] = relationship("MasterModel", back_populates="addresses")
    working_days: Mapped[List["WorkingDayModel"]] = relationship(
        "WorkingDayModel",
        back_populates="address",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    week_templates: Mapped[List["WeekTemplateModel"]] = relationship(
        "WeekTemplateModel",
        back_populates="address",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    @classmethod
    async def create(cls, session: AsyncSession, data: dict):
        address = cls(**data)
        session.add(address)
        await session.flush()
        return address.id

    @classmethod
    async def get_by_id(cls, session: AsyncSession, address_id: uuid.UUID):
        query = select(cls).where(cls.id == address_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_by_master_id(cls, session: AsyncSession, master_id: uuid.UUID):
        query = select(cls).where(cls.master_id == master_id)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def delete(cls, session: AsyncSession, address_id: uuid.UUID):
        obj = await session.get(cls, address_id)
        if obj:
            await session.delete(obj)
            return "success"
        return "no such address"

    @classmethod
    async def update(cls, session: AsyncSession, address_id: uuid.UUID, update_data: dict) -> str:
        query = update(cls).where(cls.id == address_id).values(**update_data)
        await session.execute(query)
        return "success"


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

    @classmethod
    async def get_by_name(cls, session: AsyncSession, master_id: uuid.UUID, name: str):
        """Получение позиции по названию"""
        query = select(cls).where(cls.master_id == master_id, cls.name == name)
        result = await session.execute(query)
        return result.scalars().first()


class AppointmentModel(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    master_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("masters.id", ondelete="CASCADE"))
    date: Mapped[date]
    start_time: Mapped[time]
    final_price: Mapped[int]
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
        query = select(cls).where(cls.master_id == master_id, cls.date == app_date).order_by(cls.start_time)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_user_id(cls, session: AsyncSession, user_id: uuid.UUID):
        query = select(cls).where(cls.user_id == user_id).order_by(cls.date, cls.start_time)
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

    @classmethod
    async def get_by_date_range(cls, session: AsyncSession, master_id: uuid.UUID, start_date: date, end_date: date) -> List["AppointmentModel"]:
        query = select(cls).where(and_(cls.master_id == master_id, cls.date >= start_date, cls.date <= end_date))
        result = await session.execute(query)
        return list(result.scalars().all())

class GuidesModel(Base):
    __tablename__ = "guides"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    category: Mapped[str]
    steps: Mapped[str]
    author: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    guide_status: Mapped[int]

    @classmethod
    async def get_all(cls, session: AsyncSession):
        query = select(cls).where(cls.guide_status == GuideStatus.CONFIRMED).order_by(cls.name)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_categories(cls, categories: List[str], session: AsyncSession):
        query = select(cls).where(cls.category.in_(categories), cls.guide_status == GuideStatus.CONFIRMED).order_by(cls.name)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, guide_id: uuid.UUID):
        query = select(cls.steps).where(cls.id == guide_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def create(cls, session: AsyncSession, data: dict):
        data["guide_status"] = GuideStatus.PENDING
        guide = cls(**data)
        session.add(guide)
        await session.flush()
        return guide.id

    @classmethod
    async def update(cls, session: AsyncSession, id: uuid.UUID, author: uuid.UUID, update_data: dict):
        update_data["guide_status"] = GuideStatus.PENDING
        query = update(cls).where(cls.id ==id, cls.author == author).values(**update_data)
        await session.execute(query)
        return "success"

class EarningsModel(Base):
    __tablename__ = "earnings"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    price: Mapped[int]
    date: Mapped[date]
    master_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("masters.id", ondelete="CASCADE"))

    # Relationships
    master: Mapped["MasterModel"] = relationship("MasterModel", back_populates="earnings")

    @classmethod
    async def create(cls, session: AsyncSession, data: dict):
        earning = cls(**data)
        session.add(earning)
        await session.flush()
        return earning.id

    @classmethod
    async def get_by_id(cls, session: AsyncSession, earning_id: uuid.UUID):
        query = select(cls).where(cls.id == earning_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_by_master_id(cls, session: AsyncSession, master_id: uuid.UUID):
        query = select(cls).where(cls.master_id == master_id).order_by(cls.date.desc())
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_date_range(cls, session: AsyncSession, master_id: uuid.UUID, start_date: date, end_date: date):
        query = select(cls).where(
            and_(cls.master_id == master_id, cls.date >= start_date, cls.date <= end_date)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def update(cls, session: AsyncSession, earning_id: uuid.UUID, update_data: dict):
        query = update(cls).where(cls.id == earning_id).values(**update_data)
        await session.execute(query)
        return "success"

    @classmethod
    async def delete(cls, session: AsyncSession, earning_id: uuid.UUID):
        obj = await session.get(cls, earning_id)
        if obj:
            await session.delete(obj)
            return "success"
        return "no such earning"


class PrepayModel(Base):
    __tablename__ = "prepayments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    percent: Mapped[int]
    start_date: Mapped[date]
    end_date: Mapped[date]
    master_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("masters.id", ondelete="CASCADE"))

    # Relationships
    master: Mapped["MasterModel"] = relationship("MasterModel", back_populates="prepayments")

    @classmethod
    async def create(cls, session: AsyncSession, data: dict):
        prepay = cls(**data)
        session.add(prepay)
        await session.flush()
        return prepay.id

    @classmethod
    async def get_by_id(cls, session: AsyncSession, prepay_id: uuid.UUID):
        query = select(cls).where(cls.id == prepay_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_by_master_id(cls, session: AsyncSession, master_id: uuid.UUID):
        query = select(cls).where(cls.master_id == master_id).order_by(cls.start_date.desc())
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_active_by_date(cls, session: AsyncSession, master_id: uuid.UUID, check_date: date):
        query = select(cls).where(
            and_(
                cls.master_id == master_id,
                cls.start_date <= check_date,
                cls.end_date >= check_date
            )
        )
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def update(cls, session: AsyncSession, prepay_id: uuid.UUID, update_data: dict):
        query = update(cls).where(cls.id == prepay_id).values(**update_data)
        await session.execute(query)
        return "success"

    @classmethod
    async def delete(cls, session: AsyncSession, prepay_id: uuid.UUID):
        obj = await session.get(cls, prepay_id)
        if obj:
            await session.delete(obj)
            return "success"
        return "no such prepayment"