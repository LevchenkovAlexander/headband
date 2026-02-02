
import logging
import uuid
from enum import Enum
from typing import List, Optional

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, select, update, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import time, date
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

class Week(Enum):
    MONDAY = "1"
    TUESDAY = "2"
    WEDNESDAY = "3"
    THURSDAY = "4"
    FRIDAY = "5"
    SATURDAY = "6"
    SUNDAY = "7"

class ServiceCategory(Enum):
    HAIRSTYLE = "1"
    COSMETOLOGY_SKINCARE = "2"
    MANICURE_PEDICURE = "3"
    BROWS_LASHES = "4"
    DEPILATION_EPILATION = "5"
    MAKEUP = "6"
    FULLMAKEUP_CONSULTATIONS = "7"
    SOLARIUM = "8"
    OTHER = "9"

class AdminModel(Base):
    __tablename__ = "admins"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    yaToken: Mapped[Optional[str]]

    # Relationships
    organizations: Mapped[List["OrganizationModel"]] = relationship(
        "OrganizationModel",
        back_populates="admin",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @classmethod
    async def create(cls, session: SessionDep, data: dict):
        admin = cls(**data)
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        return "success", admin.id

    @classmethod
    async def update(cls, session: SessionDep, update_data: dict):
        obj_id = update_data.pop("id", None)
        if not obj_id:
            logging.error(ValueError("ID is required for update"))
            return "ID is required for update"

        query = (
            update(cls)
            .where(cls.id == obj_id)
            .values(**update_data))
        await session.execute(query)
        await session.commit()
        return "success"

    @classmethod
    async def delete(cls, session: SessionDep, id: uuid.UUID):
        obj = await session.get(cls, id)
        if obj:
            await session.delete(obj)
            await session.commit()
            return "success"
        return "no such id admin"

class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(index=True)
    address: Mapped[str]
    description: Mapped[str] = mapped_column(default="no info")
    categories: Mapped[str]
    fixed_schedule: Mapped[bool]
    fixed_prices: Mapped[bool]
    day_start_template: Mapped[time]
    day_end_template: Mapped[time]
    day_off: Mapped[str]
    admin_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("admins.id", ondelete="CASCADE"))
    unique_code_master: Mapped[str] = mapped_column(unique=True, index=True)
    unique_code_user: Mapped[str] = mapped_column(unique=True, index=True)

    # Relationships
    admin: Mapped["AdminModel"] = relationship("AdminModel", back_populates="organizations")
    masters: Mapped[List["MasterModel"]] = relationship(
        "MasterModel",
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    prices: Mapped[List["PriceModel"]] = relationship(
        "PriceModel",
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    users: Mapped[List["UserModel"]] = relationship(
        "UserModel",
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @classmethod
    async def get_org_by_id(cls, session: SessionDep, id: uuid.UUID):
        query = select(cls).where(cls.id == id)
        result = await session.execute(query)
        org = result.scalar_one_or_none()
        return org

    @classmethod
    async def get_by_master_unique(cls, session: SessionDep, unique_code: str):
        query = select(cls).where(cls.unique_code_master == unique_code)
        result = await session.execute(query)
        organization = result.scalar_one_or_none()
        if organization:
            return organization.id, True
        return None, False

    @classmethod
    async def get_by_user_unique(cls, session: SessionDep, unique_code: str):
        query = select(cls).where(cls.unique_code_user == unique_code)
        result = await session.execute(query)
        organization = result.scalar_one_or_none()
        if organization:
            return organization.id, True
        return None, False

    @classmethod
    async def create(cls, session: SessionDep, data: dict):
        org = cls(**data)
        session.add(org)
        await session.commit()
        await session.refresh(org)
        return "success", org.id

    @classmethod
    async def update(cls, session: SessionDep, update_data: dict):
        obj_id = update_data.pop("id", None)
        if not obj_id:
            logging.error(ValueError("ID is required for update"))
            return "ID is required for update"

        query = (
            update(cls)
            .where(cls.id == obj_id)
            .values(**update_data))
        await session.execute(query)
        await session.commit()
        return "success"

    @classmethod
    async def get_organizations_by_adm_id(cls, session: SessionDep, adm_id: uuid.UUID):
        query = select(cls.id).where(cls.admin_id == adm_id)
        result = await session.execute(query)
        ids = [row[0] for row in result.fetchall()]
        return ids

class MasterModel(Base):
    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE")
    )
    username: Mapped[str] = mapped_column(default="no info")
    full_name: Mapped[str] = mapped_column(default="no info")
    working_day_start: Mapped[time]
    working_day_end: Mapped[time]
    day_off: Mapped[str]

    # Relationships
    organization: Mapped["OrganizationModel"] = relationship(
        "OrganizationModel",
        back_populates="masters"
    )
    appointments: Mapped[List["AppointmentModel"]] = relationship(
        "AppointmentModel",
        back_populates="master",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    individual_prices: Mapped[List["IndividualPricesModel"]] = relationship(
        "IndividualPricesModel",
        back_populates="master",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @classmethod
    async def create(cls, session: SessionDep, data: dict):
        master = cls(**data)
        session.add(master)
        await session.commit()
        await session.refresh(master)
        return True

    @classmethod
    async def get_master_by_id(cls, session: SessionDep, id: int):
        query = select(cls).where(cls.id == id)
        result = await session.execute(query)
        master = result.scalar_one_or_none()
        return master

    @classmethod
    async def get_masters_by_org_id(cls, session: SessionDep, org_id: uuid.UUID):
        query = select(cls.id).where(cls.organization_id == org_id)
        result = await session.execute(query)
        ids = [row[0] for row in result.fetchall()]
        return ids

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
    username: Mapped[Optional[str]]
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL")
    )

    # Relationships
    organization: Mapped[Optional["OrganizationModel"]] = relationship(
        "OrganizationModel",
        back_populates="users"
    )
    appointments: Mapped[List["AppointmentModel"]] = relationship(
        "AppointmentModel",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @classmethod
    async def create(cls, session: SessionDep, data: dict):
        user = cls(**data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return True

    @classmethod
    async def delete_of_org(cls, session: SessionDep, org_id: uuid.UUID):
        # Теперь это будет происходить автоматически через ondelete="SET NULL"
        # Но оставим метод для обратной совместимости
        stmt = update(cls).where(cls.organization_id == org_id).values(
            {"organization_id": None}
        )
        await session.execute(stmt)
        return "success"

class AppointmentModel(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id", ondelete="CASCADE"))
    date: Mapped[date]
    start_time: Mapped[time]
    end_time: Mapped[time]
    price_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prices.id", ondelete="CASCADE"))

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="appointments")
    master: Mapped["MasterModel"] = relationship("MasterModel", back_populates="appointments")
    price: Mapped["PriceModel"] = relationship("PriceModel", back_populates="appointments")

    @classmethod
    async def create(cls, session: SessionDep, data: dict):
        appointment = cls(**data)
        session.add(appointment)
        await session.commit()
        await session.refresh(appointment)
        return "success"

    @classmethod
    async def get_by_master_and_date(cls, session: SessionDep, master_id: int, date: date) -> List['AppointmentModel']:
        query = select(cls).where(
            cls.master_id == master_id,
            cls.date == date
        ).order_by(cls.start_time)
        result = await session.execute(query)
        appointments = result.scalars().all()
        return list(appointments)

    @classmethod
    async def delete(cls, session: SessionDep, id: uuid.UUID):
        appointment = await session.get(cls, id)
        if appointment:
            await session.delete(appointment)
            await session.commit()
            return "success"
        return "no such id"

class PriceModel(Base):
    __tablename__ = "prices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE")
    )
    name: Mapped[str]
    price: Mapped[int]
    category: Mapped[int]
    approximate_time: Mapped[time]

    # Relationships
    organization: Mapped["OrganizationModel"] = relationship(
        "OrganizationModel",
        back_populates="prices"
    )
    appointments: Mapped[List["AppointmentModel"]] = relationship(
        "AppointmentModel",
        back_populates="price",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    individual_prices: Mapped[List["IndividualPricesModel"]] = relationship(
        "IndividualPricesModel",
        back_populates="price",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @classmethod
    async def get_price_by_id(cls, session: SessionDep, id: uuid.UUID):
        query = select(cls).where(cls.id == id)
        result = await session.execute(query)
        price = result.scalar_one_or_none()
        return price

    @classmethod
    async def create(cls, session: SessionDep, data: dict):
        price = cls(**data)
        session.add(price)
        await session.commit()
        await session.refresh(price)
        return "success", price.id

    @classmethod
    async def update(cls, session: SessionDep, update_data: dict):
        obj_id = update_data.pop("id", None)
        if not obj_id:
            logging.error(ValueError("ID is required for update"))
            return "ID is required for update"

        query = (
            update(cls)
            .where(cls.id == obj_id)
            .values(**update_data))
        await session.execute(query)
        await session.commit()
        return "success"

    @classmethod
    async def delete(cls, session: SessionDep, id: uuid.UUID):
        obj = await session.get(cls, id)
        if obj:
            await session.delete(obj)
            await session.commit()
            return "success"
        return "no such id price"

    @classmethod
    async def delete_prices_by_org_id(cls, session: SessionDep, org_id: uuid.UUID):
        # Теперь это происходит автоматически через каскад
        # Но оставим для обратной совместимости
        query = delete(cls).where(cls.organization_id == org_id)
        await session.execute(query)
        return "success"

class IndividualPricesModel(Base):
    __tablename__ = "individual_prices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id", ondelete="CASCADE"))
    price_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prices.id", ondelete="CASCADE"))
    new_price: Mapped[int]

    # Relationships
    master: Mapped["MasterModel"] = relationship(
        "MasterModel",
        back_populates="individual_prices"
    )
    price: Mapped["PriceModel"] = relationship(
        "PriceModel",
        back_populates="individual_prices"
    )

    @classmethod
    async def organization_delete_price(cls, session: SessionDep, price_id: uuid.UUID):

        query = delete(cls).where(cls.price_id == price_id)
        await session.execute(query)
        return "success"

    @classmethod
    async def master_delete_price(cls, session: SessionDep, master_id: int):

        query = delete(cls).where(cls.master_id == master_id)
        await session.execute(query)
        return "success"