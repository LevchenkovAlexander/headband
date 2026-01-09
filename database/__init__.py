from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date

engine = create_async_engine('postgresql+asyncpg://username:password@localhost/dbname')

session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with session as s:
        yield s

async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class Base(DeclarativeBase):
    pass

class AppointmentModel(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    master_id: Mapped[int]
    date: Mapped[date]
    price: Mapped[int]
    service: Mapped[str]
    style: Mapped[str]

class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str]
    #TODO подумать над таблицей организаций

class MasterModel(Base):
    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int]
    photo_path: Mapped[str]
    name: Mapped[str]
    working_day_start: Mapped[date]
    working_day_end: Mapped[date]

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int]
    name: Mapped[str]


# TODO сделать валидацию