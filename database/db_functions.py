import logging
import random
import hashlib
import uuid



from aiogram.types import Message, User, Chat

from headband.database import AppointmentModel, MasterModel, Week, UserModel, \
    OrganizationModel, AsyncSessionLocal, PriceModel, AdminModel
from datetime import time, timedelta, datetime

from headband.database.requests import AppointmentCreateRequest, MasterCreateRequest, UserCreateRequest, \
    OrganizationCreateRequest, AdminCreateRequest


def _int_minutes_to_time(minutes: int) -> time:
    """Перевод int минут в класс time"""
    hours = minutes // 60
    mins = minutes % 60
    return time(hour=hours, minute=mins)

def _get_week_dates(start_date: datetime) -> list[datetime]:
    """Возвращает список из 7 дней недели, начиная с start_date"""
    week = [start_date + timedelta(days=i) for i in range(7)]
    return week

def _timedelta_to_time(td: timedelta) -> time:
    """Преобразует timedelta в time (только если < 24 часов)"""
    if td.days < 0:
        raise ValueError("Отрицательный timedelta не может быть преобразован в time")

    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    return time(hour=hours, minute=minutes)

def _time_to_timedelta(t: time) -> timedelta:
    """Перевод из класса time в timedelta для выполнения действий"""
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

def _timedelta_to_int_minutes(td: timedelta) -> int:
    """Перевод из формата чч.мм.сс в int минут"""
    return int(td.total_seconds() // 60)

def _get_weekday_caps(date_obj=None):
    """Получение дня недели из даты заглавными буквами"""
    if date_obj is None:
        date_obj = datetime.now()
    return date_obj.strftime('%A').upper()

async def get_possible_start_time(master_id, date, service_id):
    """Получение возможного времени для записи"""
    session = AsyncSessionLocal()
    try:
        master = await MasterModel.get_master_by_id(session = session, id=master_id)
        days_off = master.day_off
        weekday_name = _get_weekday_caps(date)
        weekday = Week[weekday_name].value

        if weekday in days_off:
            return None, "day off"

        else:
            appointments = await AppointmentModel.get_by_master_and_date(session = session, master_id=master_id, date=date)

            day_start = master.working_day_start
            day_end = master.working_day_end
            start_time = []
            end_time = []

            end_time.append(_time_to_timedelta(day_start))
            for appointment in appointments:
                start_time.append(_time_to_timedelta(appointment.start_time))
                end_time.append(_time_to_timedelta(appointment.end_time))
            start_time.append(_time_to_timedelta(day_end))

            price = await PriceModel.get_price_by_id(session = session, id=service_id)
            appointment_approx_time = price.approximate_time
            possible_time_for_start = 0
            possible_starts = []
            ten_minutes_gap = timedelta(minutes=10)
            for i in range(len(start_time)):
                gap = start_time[i]-end_time[i]
                if gap>=appointment_approx_time:
                    free_minutes = gap-appointment_approx_time
                    k = _timedelta_to_int_minutes(free_minutes)//10
                    possible_time_for_start+=(k+1)
                    for j in range(k+1):
                        possible_starts.append(end_time[i]+ten_minutes_gap*j)
            if possible_time_for_start == 0:
                return None, "no time for app"
            else:
                return possible_starts, "success"
    except Exception as e:
        await session.rollback()
        logging.info(f"Error getting possible_time: {e}")
        return None, "error"
    finally:
        await session.close()

async def get_appointments_by_date(master_id, date):
    session = AsyncSessionLocal()
    try:
        appointments = await AppointmentModel.get_by_master_and_date(session = session, master_id=master_id, date=date)
        if appointments:
            return appointments, len(appointments), "success"
        return None, 0, "no appointments today"
    except Exception as e:
        await session.rollback()
        logging.info(f"Error getting appointments by date: {e}")
        return None, 0, "error"
    finally:
        await session.close()

async def get_week_timetable(master_id, date):
    session = AsyncSessionLocal()
    try:
        week_list = _get_week_dates(date)
        week_appointments = []
        for day in week_list:
            appointments = await get_appointments_by_date(master_id, day)
            week_appointments.append(appointments)
        return week_appointments, "success"
    except Exception as e:
        await session.rollback()
        logging.info(f"Error getting appointments for week: {e}")
        return None, "error"
    finally:
        await session.close()

async def create_appointment(appointment_request: AppointmentCreateRequest):
    session = AsyncSessionLocal()
    try:
        price = await PriceModel.get_price_by_id(session = session, id=appointment_request.service_id)
        appointment_approx_time = price.approximate_time
        appointment_dict = appointment_request.model_dump()
        appointment_dict["end_time"] = _timedelta_to_time(_time_to_timedelta(appointment_dict["start_time"])+appointment_approx_time)
        status = await AppointmentModel.create(session = session, data=appointment_dict)
        return status
    except Exception as e:
        await session.rollback()
        logging.info(f"Error creating appointment: {e}")
        return "error"
    finally:
        await session.close()

async def update_master(master_id, update_data):
    session = AsyncSessionLocal()
    try:
        master = await MasterModel.update_master(session=session, id = master_id, update_data=update_data)
        return master, "success"
    except Exception as e:
        await session.rollback()
        logging.info(f"Error updating master: {e}")
        return None, "error"
    finally:
        await session.close()

async def cancel_appointment(appointment_id):
    session = AsyncSessionLocal()
    try:
        status = await AppointmentModel.delete(session = session, id=appointment_id)
        return status
    except Exception as e:
        await session.rollback()
        logging.info(f"Error canceling appointment: {e}")
        return "error"
    finally:
        await session.close()

async def create_master(user: User, chat: Chat, args: str):
    session = AsyncSessionLocal()
    try:
        master = MasterCreateRequest(id=chat.id,
                                     organization_id=args[0:6],
                                     username=user.username,
                                     working_day_start=time(hour=8, minute=0),
                                     working_day_end = time(hour=18, minute=0),
                                     day_off = "0")
        if await MasterModel.create(session=session, data=master.model_dump()):
            return "success"
        return "unable to create"
    except Exception as e:
        await session.rollback()
        logging.info(f"Error creating master: {e}")
        return "error"
    finally:
        await session.close()

async def create_user(user: User, chat: Chat, args: str):
    session = AsyncSessionLocal()
    try:
        user = UserCreateRequest(id=chat.id,
                                 organization_id=args[0:6],
                                 username=user.username)
        if await UserModel.create(session=session, data=user.model_dump()):
            return "success"
        return "unable to create"
    except Exception as e:
        await session.rollback()
        logging.info(f"Error creating user: {e}")
        return "error", None
    finally:
        await session.close()

async def create_organization(org_request: OrganizationCreateRequest):
    session = AsyncSessionLocal()
    try:
        org_dict = org_request.model_dump()
        unique_code = str(uuid.uuid4())
        hash_uni = hashlib.sha256(unique_code.encode()).hexdigest()
        org_dict["unique_code"] = hash_uni
        status = await OrganizationModel.create(session=session, data=org_dict)
        return status
    except Exception as e:
        await session.rollback()
        logging.info(f"Error creating organization: {e}")
        return "error"
    finally:
        await session.close()

async def create_admin(adm_request: AdminCreateRequest):
    session = AsyncSessionLocal()
    try:
        admin_dict = adm_request.model_dump()
        status = await AdminModel.create(session=session, data=admin_dict)
        return status
    except Exception as e:
        await session.rollback()
        logging.info(f"Error creating appointment: {e}")
        return "error"
    finally:
        await session.close()

