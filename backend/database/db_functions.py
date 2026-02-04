import logging
import hashlib
import uuid



from aiogram.types import User, Chat

from headband.backend.database import AppointmentModel, MasterModel, Week, UserModel, \
    OrganizationModel, AsyncSessionLocal, PriceModel, AdminModel


from headband.backend.database.requests import AppointmentCreateRequest, MasterCreateRequest, UserCreateRequest, \
    OrganizationCreateRequest, AdminCreateRequest, PriceCreateRequest, OrganizationUpdateRequest, PriceUpdateRequest, \
    AdminUpdateRequest
from headband.backend.database.responses import AppointmentResponse
from headband.backend.database.time_helpers import _get_weekday_caps, _time_to_timedelta, _timedelta_to_int_minutes, \
    _get_week_dates, _timedelta_to_time
from datetime import timedelta

async def get_possible_start_time(master_id, date, price_id):
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
            id = []
            id.append(master_id)
            #так как здесь мы работаем в рамках одной организации,
            #нам не за чем знать его записей в других
            appointments, status = await AppointmentModel.get_by_master_and_date(session = session, master_ids=id, date=date)
            day_start = master.working_day_start
            day_end = master.working_day_end
            start_time = []
            end_time = []

            end_time.append(_time_to_timedelta(day_start))
            for appointment in appointments:
                start_time.append(_time_to_timedelta(appointment.start_time))
                end_time.append(_time_to_timedelta(appointment.end_time))
            start_time.append(_time_to_timedelta(day_end))

            price = await PriceModel.get_price_by_id(session = session, id=price_id)
            appointment_approx_time = price.approximate_time
            possible_time_for_start = 0
            possible_starts = []
            ten_minutes_gap = timedelta(minutes=10)
            for i in range(len(start_time)):
                gap = start_time[i]-end_time[i]
                if gap>=_time_to_timedelta(appointment_approx_time):
                    free_minutes = gap-_time_to_timedelta(appointment_approx_time)
                    k = _timedelta_to_int_minutes(free_minutes)//10
                    possible_time_for_start+=(k+1)
                    for j in range(k+1):
                        possible_starts.append(_timedelta_to_time(end_time[i]+ten_minutes_gap*j))
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

async def get_appointments_by_date(master_chat_id, date):
    session = AsyncSessionLocal()
    try:
        ids = await MasterModel.get_ids_by_chat_id(session=session, chat_id=master_chat_id)
        appointments, flag = await AppointmentModel.get_by_master_and_date(session = session, master_ids=ids, date=date)
        adresses = []
        names = []
        for a in appointments:
            price_id = a.price_id
            name = await PriceModel.get_name_by_id(session=session, id=price_id)
            org_id = await PriceModel.get_org_id_by_id(session=session, id = price_id)
            address = await OrganizationModel.get_address_by_id(session=session, id=org_id)
            adresses.append(address)
            names.append(name)
        if flag:
            return appointments, len(appointments), "success", adresses, names
        return [], 0, "no appointments today", [], []
    except Exception as e:
        await session.rollback()
        logging.info(f"Error getting appointments by date: {e}")
        return [], 0, "error", [], []
    finally:
        await session.close()

async def get_week_timetable(master_id, date):
    session = AsyncSessionLocal()
    try:
        week_list = _get_week_dates(date)
        week_appointments = []
        for day in week_list:
            appointments, count, status, addresses, names = await get_appointments_by_date(master_id, day)
            a = []
            for i, appointment in enumerate(appointments):
                aresponse = AppointmentResponse.model_validate(appointment).model_dump()
                aresponse["address"] = addresses[i]
                aresponse["service_name"] = names[i]
                a.append(aresponse)
            week_appointments.append(a)
        return week_appointments, "success"
    except Exception as e:
        await session.rollback()
        logging.info(f"Error getting appointments for week: {e}")
        return [], "error"
    finally:
        await session.close()

async def create_appointment(appointment_request: AppointmentCreateRequest):
    session = AsyncSessionLocal()
    try:
        price = await PriceModel.get_price_by_id(session = session, id=appointment_request.price_id)
        appointment_dict = appointment_request.model_dump()
        appointment_dict["end_time"] = _timedelta_to_time(_time_to_timedelta(appointment_dict["start_time"])+_time_to_timedelta(price.approximate_time))
        status = await AppointmentModel.create(session = session, data=appointment_dict)
        return status
    except Exception as e:
        await session.rollback()
        logging.info(f"Error creating appointment: {e}")
        return "error"
    finally:
        await session.close()

async def update_master(update_data):
    session = AsyncSessionLocal()
    try:
        master_to_upd = update_data.model_dump(exclude_unset=True)
        status = await MasterModel.update(session=session, update_data=master_to_upd)
        return status
    except Exception as e:
        await session.rollback()
        logging.info(f"Error updating master: {e}")
        return "error"
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

async def create_master(user: User, chat: Chat, organization_id: uuid.UUID):
    session = AsyncSessionLocal()
    try:
        organization = await OrganizationModel.get_org_by_id(session=session, id = organization_id)
        master = MasterCreateRequest(chat_id=chat.id,
                                     organization_id=organization_id,
                                     username=user.username,
                                     working_day_start=organization.day_start_template,
                                     working_day_end = organization.day_end_template,
                                     day_off = organization.day_off)
        if await MasterModel.create(session=session, data=master.model_dump()):
            return "success"
        return "unable to create"
    except Exception as e:
        await session.rollback()
        logging.info(f"Error creating master: {e}")
        return "error"
    finally:
        await session.close()


async def create_user(user: User, chat: Chat, organization_id: uuid.UUID):
    session = AsyncSessionLocal()
    try:
        user = UserCreateRequest(chat_id=chat.id,
                                 organization_id=organization_id,
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
        org_dict["unique_code_master"] = hash_uni[0:32]
        org_dict["unique_code_user"] = hash_uni[32:64]
        status, org_id = await OrganizationModel.create(session=session, data=org_dict)
        return status, hash_uni[0:32], hash_uni[32:64], org_id
    except Exception as e:
        await session.rollback()
        logging.info(f"Error creating organization: {e}")
        return "error", None, 0
    finally:
        await session.close()

async def update_organization(update_data: OrganizationUpdateRequest):
    session = AsyncSessionLocal()
    try:
        org_to_upd = update_data.model_dump(exclude_unset=True)
        status = await OrganizationModel.update(session=session, update_data=org_to_upd)
        return status
    except Exception as e:
        await session.rollback()
        logging.info(f'Error updating organization: {e}')
        return "error"
    finally:
        await session.close()


async def delete_organization(delete_id: uuid.UUID):
    session = AsyncSessionLocal()
    try:
        org = await session.get(OrganizationModel, delete_id)
        if not org:
            return "organization not found"
        await session.delete(org)
        await session.commit()
        return "success"
    except Exception as e:
        await session.rollback()
        logging.error(f'Error deleting organization: {e}')
        return "error"
    finally:
        await session.close()

"""admin fetches"""


async def update_admin(update_data: AdminUpdateRequest):
    session = AsyncSessionLocal()
    try:
        org_to_upd = update_data.model_dump(exclude_unset=True)
        status = await AdminModel.update(session=session, update_data=org_to_upd)
        return status
    except Exception as e:
        await session.rollback()
        logging.info(f'Error updating price: {e}')
        return "error"
    finally:
        await session.close()

async def create_admin(adm_request: AdminCreateRequest):
    session = AsyncSessionLocal()
    try:
        admin_dict = adm_request.model_dump()
        status, adm_id = await AdminModel.create(session=session, data=admin_dict)
        return status, adm_id
    except Exception as e:
        await session.rollback()
        logging.info(f"Error creating appointment: {e}")
        return "error", 0
    finally:
        await session.close()

"""price fetches"""
async def create_price_position(price_position: PriceCreateRequest):
    session = AsyncSessionLocal()
    try:
        price_dict = price_position.model_dump()
        status, id = await PriceModel.create(session=session, data=price_dict)
        return status, id
    except Exception as e:
        await session.rollback()
        logging.info(f"Error creating price: {e}")
        return "error", 0
    finally:
        await session.close()
async def update_price(update_data: PriceUpdateRequest):
    session = AsyncSessionLocal()
    try:
        org_to_upd = update_data.model_dump(exclude_unset=True)
        status = await PriceModel.update(session=session, update_data=org_to_upd)
        return status
    except Exception as e:
        await session.rollback()
        logging.info(f'Error updating price: {e}')
        return "error"
    finally:
        await session.close()


async def delete_price(delete_id: uuid.UUID):
    session = AsyncSessionLocal()
    try:
        price = await session.get(PriceModel, delete_id)
        if not price:
            return "price not found"

        # Удалит каскадно appointments и individual_prices
        await session.delete(price)
        await session.commit()
        return "success"
    except Exception as e:
        await session.rollback()
        logging.error(f'Error deleting price: {e}')
        return "error"
    finally:
        await session.close()



async def user_master_deeplink(args: str):
    session = AsyncSessionLocal()
    try:
        master_res, master_status = await OrganizationModel.get_by_master_unique(session=session, unique_code=args)
        user_res, user_status = await OrganizationModel.get_by_user_unique(session=session, unique_code=args)
        logging.info(f"user_res {user_res}")
        logging.info(f"master_res {master_res}")
        if master_status:
            return 0, master_res
        elif user_status:
            return 1, user_res
        else:
            return 2, None
    except Exception as e:
        await session.rollback()
        logging.info(f"Error with user_master_deeplink: {e}")
        return 3, None
    finally:
        await session.close()


