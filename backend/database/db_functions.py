import logging
import uuid
from typing import Tuple, Optional, List

from aiogram.types import User, Chat
from sqlalchemy import update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import AppointmentModel, MasterModel, UserModel, \
    PriceModel, GuidesModel, CategoryModel, MasterCategoryModel, MasterAbsenceModel, WeekTemplateModel, \
    WorkingDayModel, AddressModel, Week

from backend.database.requests import AppointmentCreateRequest, MasterCreateRequest, UserCreateRequest, \
    PriceCreateRequest, PriceUpdateRequest, WeekTemplate, TemplateUpdateRequest, WorkingDayUpdateRequest
from backend.database.responses import AppointmentResponse

from backend.database.time_helpers import _get_weekday_caps, _time_to_timedelta, _timedelta_to_int_minutes, \
    _get_week_dates, _timedelta_to_time, _cancel_conflicting_appointments_for_date
from datetime import timedelta, date, time, datetime


# ==================== GUIDES ====================
async def get_guides(master_id: uuid.UUID, session: AsyncSession) -> Tuple[str, List[dict], List[dict]]:
    """Получение гайдов по категориям мастера"""
    # Получаем категории мастера через junction table
    category_ids = await MasterCategoryModel.get_categories_by_master(id = master_id, session = session)

    g_fitable = await GuidesModel.get_by_categories(categories=category_ids, session=session)
    g_all = await GuidesModel.get_all(session=session)

    g_fit_resp = []
    g_all_resp = []

    for g in g_fitable:
        g_fit_resp.append({
            "id": str(g.id),
            "steps": g.steps,
            "author": str(g.author)
        })

    for g in g_all:
        g_all_resp.append({
            "id": str(g.id),
            "steps": g.steps,
            "author": str(g.author)
        })

    return "success", g_fit_resp, g_all_resp

async def get_steps(guide_id: uuid.UUID, session: AsyncSession) -> Tuple[str, Optional[str]]:
    """Получение шагов гайда по ID"""
    return await GuidesModel.get_by_id(guide_id=guide_id, session=session)

# ==================== APPOINTMENTS ====================
async def get_possible_start_time(
        master_id: uuid.UUID,
        app_date: date,
        price_id: uuid.UUID,
        session: AsyncSession
) -> Tuple[Optional[List[time]], str]:
    """Получение возможного времени для записи"""

    master = await MasterModel.get_by_id(session=session, master_id=master_id)
    if not master:
        return None, "master not found"

    is_absent = await MasterAbsenceModel.is_absent(
        session=session,
        master_id=master_id,
        check_date=app_date
    )
    if is_absent:
        return None, "master is absent"

    # Проверяем день недели через week_template
    weekday = _get_weekday_caps(app_date).value  # 1-7

    week_template = await WeekTemplateModel.get_by_master_and_weekday(
        session=session,
        master_id=master_id,
        weekday=weekday
    )

    if not week_template:
        return None, "day off"

    # Получаем working_day для этой даты
    working_day = await WorkingDayModel.get_by_master_and_date(
        session=session,
        master_id=master_id,
        day_date=app_date
    )

    if not working_day:
        # Создаём working_day из template если нет
        working_day_data = {
            "master_id": master_id,
            "day_date": app_date,
            "start_time": week_template.start_time,
            "end_time": week_template.end_time,
            "address": week_template.address
        }
        working_day_id = await WorkingDayModel.create(session=session, data=working_day_data)
        working_day = await WorkingDayModel.get_by_id(session=session, id=working_day_id)

    # Получаем записи мастера на эту дату
    appointments = await AppointmentModel.get_by_master_and_date(
        session=session,
        master_id=master_id,
        app_date=app_date
    )

    day_start = working_day.start_time  # в минутах
    day_end = working_day.end_time  # в минутах

    # Получаем длительность услуги
    price = await PriceModel.get_by_id(session=session, price_id=price_id)
    if not price:
        return None, "price not found"

    appointment_duration = price.approximate_time  # в минутах

    # Собираем занятые интервалы
    end_times = [day_start]
    start_times = []

    for appointment in appointments:
        app_time = _time_to_timedelta(appointment.time)
        app_minutes = _timedelta_to_int_minutes(app_time)
        start_times.append(app_minutes)
        end_times.append(app_minutes + appointment_duration)

    start_times.append(day_end)

    # Находим свободные слоты
    possible_starts = []
    ten_minutes = 10  # минут

    for i in range(len(start_times)):
        gap = start_times[i] - end_times[i]
        if gap >= appointment_duration:
            free_minutes = gap - appointment_duration
            k = free_minutes // ten_minutes
            for j in range(k + 1):
                slot_minutes = end_times[i] + ten_minutes * j
                possible_starts.append(_timedelta_to_time(timedelta(minutes=slot_minutes)))

    if not possible_starts:
        return None, "no time for app"

    return possible_starts, "success"

async def get_appointments_by_date(
        master_id: uuid.UUID,
        app_date: date,
        session: AsyncSession
) -> Tuple[List, int, str, List[Optional[str]], List[Optional[str]]]:
    """Получение записей мастера на дату"""
    appointments = await AppointmentModel.get_by_master_and_date(
        session=session,
        master_id=master_id,
        app_date=app_date
    )

    addresses = []
    names = []

    for a in appointments:
        price = await PriceModel.get_by_id(session=session, price_id=a.price_id)
        if price:
            names.append(price.name)
            working_day = await WorkingDayModel.get_by_id(session=session, id=a.working_day_id)
            if working_day and working_day.address:
                addr = await AddressModel.get_by_id(session=session, address_id=working_day.address_id)
                addresses.append(addr.address if addr else None)
            else:
                addresses.append(None)
        else:
            names.append(None)
            addresses.append(None)

    if appointments:
        return appointments, len(appointments), "success", addresses, names

    return [], 0, "no appointments today", [], []

async def get_appointments_by_user(
        chat_id: int,
        session: AsyncSession
) -> List[dict]:
    """Получение записей пользователя"""
    user = await UserModel.get_by_chat_id(session=session, chat_id=chat_id)
    if not user:
        return []

    appointments = await AppointmentModel.get_by_user_id(
        session=session,
        user_id=user.id
    )

    response_list = []
    for a in appointments:
        aresponse = AppointmentResponse.model_validate(a).model_dump()

        price = await PriceModel.get_by_id(session=session, price_id=a.price_id)
        if price:
            aresponse["service_name"] = price.name
            aresponse["final_price"] = a.final_price

        # Получаем адрес из working_day
        working_day = await WorkingDayModel.get_by_id(session=session, id=a.working_day_id)
        if working_day:
            aresponse["address"] = working_day.address

        response_list.append(aresponse)

    return response_list

async def create_appointment(
        appointment_request: AppointmentCreateRequest,
        session: AsyncSession
) -> str:
    """Создание записи"""
    price = await PriceModel.get_by_id(session=session, price_id=appointment_request.price_id)
    if not price:
        return "price not found"

    appointment_dict = appointment_request.model_dump()

    possible_times = await get_possible_start_time(appointment_dict["master_id"], appointment_dict["date"],appointment_dict["price_id"], session=session)
    if appointment_dict["start_time"] in possible_times:
        # Получаем или создаём working_day
        working_day = await WorkingDayModel.get_by_master_and_date(
            session=session,
            master_id=appointment_dict["master_id"],
            day_date=appointment_dict["date"]
        )

        if not working_day:
            # Создаём из week_template
            weekday = _get_weekday_caps(appointment_dict["date"]).value
            week_template = await WeekTemplateModel.get_by_master_and_weekday(
                session=session,
                master_id=appointment_dict["master_id"],
                weekday=weekday
            )
            if week_template:
                wd_data = {
                    "master_id": appointment_dict["master_id"],
                    "day_date": appointment_dict["date"],
                    "start_time": week_template.start_time,
                    "end_time": week_template.end_time,
                    "address": week_template.address
                }
                wd_id = await WorkingDayModel.create(session=session, data=wd_data)
                working_day = await WorkingDayModel.get_by_id(session=session, id=wd_id)

        if working_day:
            appointment_dict["working_day_id"] = working_day.id

        appointment_dict["final_price"] = price.price

        status = await AppointmentModel.create(session=session, data=appointment_dict)
        return status
    return "unpredictable error"

async def cancel_appointment(appointment_id: uuid.UUID, session: AsyncSession) -> str:
    """Отмена записи"""
    return await AppointmentModel.delete(session=session, appointment_id=appointment_id)

async def get_week_timetable(
        master_id: uuid.UUID,
        start_date: datetime,
        session: AsyncSession
) -> Tuple[List[List[dict]], str]:
    """Получение расписания на неделю"""
    week_list = _get_week_dates(start_date)
    week_appointments = []

    for day in week_list:
        appointments, count, status, addresses, names = await get_appointments_by_date(
            master_id=master_id,
            app_date=day,
            session=session
        )
        day_appointments = []
        for i, appointment in enumerate(appointments):
            aresponse = AppointmentResponse.model_validate(appointment).model_dump()
            aresponse["address"] = addresses[i] if i < len(addresses) else None
            aresponse["service_name"] = names[i] if i < len(names) else None
            day_appointments.append(aresponse)

        week_appointments.append(day_appointments)

    return week_appointments, "success"


async def update_master(update_data, session: AsyncSession) -> str:
    """Обновление данных мастера"""
    master_to_upd = update_data.model_dump(exclude_unset=True)
    return await MasterModel.update(
        session=session,
        master_id=update_data.id,
        update_data=master_to_upd
    )

async def create_master(
        user: User,
        chat: Chat,
        session: AsyncSession,
        working_day_start: time = None,
        working_day_end: time = None
) -> str:
    """Создание мастера"""
    master_data = MasterCreateRequest(
        chat_id=chat.id,
        username=user.username,
        full_name=user.full_name if hasattr(user, 'full_name') else None,
        working_day_start=_timedelta_to_int_minutes(
            _time_to_timedelta(working_day_start)) if working_day_start else 540,  # 9:00
        working_day_end=_timedelta_to_int_minutes(_time_to_timedelta(working_day_end)) if working_day_end else 1080
        # 18:00
    )

    master_id = await MasterModel.create(session=session, data=master_data.model_dump())
    if master_id:
        return "success"
    return "unable to create"

async def get_master_categories(master_id: uuid.UUID, session: AsyncSession) -> List[CategoryModel]:
    """Получение категорий мастера"""
    return await MasterModel.get_categories(session=session, master_id=master_id)


async def create_user(
        user: User,
        chat: Chat,
        session: AsyncSession
) -> str:
    """Создание пользователя"""
    user_data = UserCreateRequest(
        chat_id=chat.id,
        username=user.username
    )

    created = await UserModel.create(session=session, data=user_data.model_dump())
    if created:
        return "success"
    return "unable to create"



"""price fetches"""
async def create_price_position(
    price_position: PriceCreateRequest,
    session: AsyncSession
) -> Tuple[str, uuid.UUID]:
    """Создание позиции прайса"""
    price_dict = price_position.model_dump()
    return await PriceModel.create(session=session, data=price_dict)


async def update_price(
    update_data: PriceUpdateRequest,
    session: AsyncSession
) -> str:
    """Обновление позиции прайса"""
    price_to_upd = update_data.model_dump(exclude_unset=True)
    return await PriceModel.update(
        session=session,
        price_id=update_data.id,
        update_data=price_to_upd
    )


async def delete_price(
    delete_id: uuid.UUID,
    session: AsyncSession
) -> str:
    """Удаление позиции прайса"""
    return await PriceModel.delete(session=session, price_id=delete_id)

#TODO сделать диплинки для рефералки
async def user_master_deeplink(
        args: str,
        session: AsyncSession
) -> Tuple[int, Optional[uuid.UUID]]:
    """
    Обработка deeplink
    Возвращает: (type, id)
    type: 0 - мастер, 1 - пользователь, 2 - не найдено
    """
    try:
        master_uuid = uuid.UUID(args)
        master = await MasterModel.get_by_id(session=session, master_id=master_uuid)
        if master:
            return 0, master_uuid
    except ValueError:
        pass

    # Пробуем найти по chat_id
    try:
        chat_id = int(args)
        master = await MasterModel.get_by_chat_id(session=session, chat_id=chat_id)
        if master:
            return 0, master.id

        user = await UserModel.get_by_chat_id(session=session, chat_id=chat_id)
        if user:
            return 1, user.id
    except ValueError:
        pass

    return 2, None


# ==================== WORKING DAYS ====================
async def create_working_day(
        master_id: uuid.UUID,
        day_date: date,
        start_time: int,
        end_time: int,
        address: Optional[str],
        session: AsyncSession
) -> uuid.UUID:
    """Создание рабочего дня"""
    data = {
        "master_id": master_id,
        "day_date": day_date,
        "start_time": start_time,
        "end_time": end_time,
        "address": address
    }
    return await WorkingDayModel.create(session=session, data=data)


async def get_working_days_by_master(
        master_id: uuid.UUID,
        start_date: date,
        end_date: date,
        session: AsyncSession
) -> List[dict]:
    """Получение рабочих дней мастера за период"""
    working_days = await WorkingDayModel.get_by_id_and_dates(id = master_id, sd = start_date, ed = end_date, session=session)

    return [
        {
            "id": str(wd.id),
            "date": wd.day_date,
            "start_time": wd.start_time,
            "end_time": wd.end_time,
            "address": wd.address
        }
        for wd in working_days
    ]


# ==================== WEEK TEMPLATE ====================
async def set_week_template(
        master_id: uuid.UUID,
        weekday: int,
        start_time: int,
        end_time: int,
        address: Optional[str],
        session: AsyncSession
) -> uuid.UUID:
    """Установка шаблона недели"""
    # Удаляем существующий шаблон для этого дня
    existing = await WeekTemplateModel.get_by_master_and_weekday(
        session=session,
        master_id=master_id,
        weekday=weekday
    )
    if existing:
        await session.delete(existing)

    data = {
        "master_id": master_id,
        "weekday": weekday,
        "start_time": start_time,
        "end_time": end_time,
        "address": address
    }
    return await WeekTemplateModel.create(session=session, data=data)

# ==================== MASTER ABSENCES ====================
async def add_absence(
        master_id: uuid.UUID,
        start_date: date,
        end_date: date,
        reason: Optional[str],
        session: AsyncSession
) -> uuid.UUID:
    """Добавление отсутствия мастера"""
    data = {
        "master_id": master_id,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason
    }
    return await MasterAbsenceModel.create(session=session, data=data)

async def get_absences_by_master(
        master_id: uuid.UUID,
        session: AsyncSession
) -> List[dict]:
    """Получение периодов отсутствия мастера"""
    absences = await MasterAbsenceModel.get_by_master_id(
        session=session,
        master_id=master_id
    )
    return [
        {
            "id": str(a.id),
            "start_date": a.start_date,
            "end_date": a.end_date,
            "reason": a.reason
        }
        for a in absences
    ]

# ==================== CATEGORIES ====================
async def get_all_categories(session: AsyncSession) -> List[dict]:
    """Получение всех категорий"""
    categories = await CategoryModel.get_all(session=session)
    return [
        {
            "id": str(cat.id),
            "name": cat.name
        }
        for cat in categories
    ]

async def create_category(
        name: str,
        session: AsyncSession
) -> uuid.UUID:
    """Создание категории"""
    data = {"name": name}
    return await CategoryModel.create(session=session, data = data)


async def get_prices_by_master(master_id: uuid.UUID, session: AsyncSession):
    return await PriceModel.get_by_master_id(session=session, master_id=master_id)

async def create_address(
    master_id: uuid.UUID,
    address: str,
    session: AsyncSession
) -> uuid.UUID:
    """Создание адреса"""
    data = {
        "master_id": master_id,
        "address": address
    }
    return await AddressModel.create(session=session, data=data)


async def get_addresses_by_master(
    master_id: uuid.UUID,
    session: AsyncSession
) -> List[dict]:
    """Получение всех адресов мастера"""
    addresses = await AddressModel.get_by_master_id(
        session=session,
        master_id=master_id
    )
    return [
        {
            "id": str(addr.id),
            "address": addr.address
        }
        for addr in addresses
    ]


async def get_address_by_id(
    address_id: uuid.UUID,
    session: AsyncSession
) -> Optional[dict]:
    """Получение адреса по ID"""
    address = await AddressModel.get_by_id(
        session=session,
        address_id=address_id
    )
    if address:
        return {
            "id": str(address.id),
            "master_id": str(address.master_id),
            "address": address.address
        }
    return None


async def delete_address(
    address_id: uuid.UUID,
    session: AsyncSession
) -> str:
    """Удаление адреса"""
    return await AddressModel.delete(session=session, address_id=address_id)


async def update_address(address_id: uuid.UUID, address: str, session: AsyncSession) -> str:
    return await AddressModel.update(session=session, address_id=address_id, update_data={"address": address})

async def set_week_template_full(master_id: uuid.UUID, templates: List[WeekTemplate], session: AsyncSession) -> str:
    try:

        for template_data in templates:
            week_template = WeekTemplateModel(
                master_id=master_id,
                weekday=template_data.weekday,
                start_time=template_data.start_time,
                end_time=template_data.end_time,
                address_id=template_data.address_id
            )
            session.add(week_template)

        await session.commit()
        return "success"
    except Exception as e:
        await session.rollback()
        logging.error(f"Ошибка создания шаблона недели: {e}")
        return f"error: {str(e)}"

async def get_week_template_by_master(master_id: uuid.UUID, session: AsyncSession) -> List[dict]:
    templates = await WeekTemplateModel.get_by_master_id(session=session, master_id=master_id)
    response = []

    for t in templates:
        address = None
        if t.address_id:
            addr = await AddressModel.get_by_id(session=session, address_id=t.address_id)
            address = addr.address if addr else None

        response.append({
            "id": t.id,
            "weekday": t.weekday,
            "start_time": t.start_time,
            "end_time": t.end_time,
            "address_id": t.address_id,
            "address": address
        })

    return response

async def update_week_template(req: TemplateUpdateRequest, session: AsyncSession):
    try:
        # Находим существующий шаблон
        template = await WeekTemplateModel.get_by_master_and_weekday(
            session=session,
            master_id=req.master_id,
            weekday=req.weekday
        )
        if not template:
            await WeekTemplateModel.create(session=session, data={
                "master_id": req.master_id,
                "weekday": req.weekday,
                "start_time": req.start_time,
                "end_time": req.end_time,
                "address_id": req.address_id
            })
            return "success"

        update_data = req.model_dump(exclude_none=True)

        if not update_data:
            return "no data to update"

        return await WeekTemplateModel.update(
            session=session,
            template_id=template.id,
            update_data=update_data
        )

    except Exception as e:
        logging.error(f"Ошибка обновления шаблона недели: {e}")
        return f"error: {str(e)}"

async def delete_day(id: uuid.UUID, weekday: int, session: AsyncSession):
    return await WeekTemplateModel.delete_by_master_id_weekday(session=session, master_id=id, weekday=weekday)


async def update_working_day(
        request: WorkingDayUpdateRequest,
        session: AsyncSession
):
    """
    Обновление конкретного рабочего дня (форс-мажор).
    Отменяет записи, которые не вписываются в новое время.
    """
    try:
        working_day = await WorkingDayModel.get_by_master_and_date(
            session=session, master_id=request.master_id, day_date=request.date
        )
        if not working_day:
            await WorkingDayModel.create(data = request.model_dump(), session=session)
            return "success"

        cancelled = await _cancel_conflicting_appointments_for_date(
            session=session,
            master_id=request.master_id,
            date=request.day_date,
            new_start=request.start_time,
            new_end=request.end_time
        )

        await WorkingDayModel.update(
            session=session,
            wd_id=working_day.id,
            update_data=request.model_dump()
        )
        return "success", cancelled

    except Exception as e:
        await session.rollback()
        logging.error(f"Ошибка обновления рабочего дня: {e}")
        return f"error: {str(e)}", []