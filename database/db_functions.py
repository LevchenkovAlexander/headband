from headband.database import AppointmentModel, MasterModel, ServiceModel, Week
from datetime import time, timedelta, datetime


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

async def get_possible_start_time(appointmentTO):

    master_id = appointmentTO.master_id
    app_date = appointmentTO.date
    service_id = appointmentTO.service_id

    master = await MasterModel.get_master_by_id(id=master_id)
    days_off = master.day_off
    weekday_name = _get_weekday_caps(app_date)
    weekday = Week[weekday_name].value

    if weekday in days_off:
        return None, "day off"

    else:
        appointments = await AppointmentModel.get_by_master_and_date(master_id=master_id, date=app_date)

        day_start = master.working_day_start
        day_end = master.working_day_end
        start_time = []
        end_time = []

        end_time.append(_time_to_timedelta(day_start))
        for appointment in appointments:
            start_time.append(_time_to_timedelta(appointment.start_time))
            end_time.append(_time_to_timedelta(appointment.end_time))
        start_time.append(_time_to_timedelta(day_end))

        service = await ServiceModel.get_service_by_id(id=service_id)
        appointment_approx_time = service.approximate_time
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

async def get_appointments_by_date(master_id, date):
    appointments = await AppointmentModel.get_by_master_and_date(master_id=master_id, date=date)
    if appointments:
        return appointments, len(appointments), "success"
    return None, 0, "no appointments today"

async def get_week_timetable(master_id, date):
    week_list = _get_week_dates(date)
    week_appointments = []
    for day in week_list:
        appointments = get_appointments_by_date(master_id, day)
        week_appointments.append(appointments)
    return week_appointments, "success"

async def create_appointment(appointmentTO):

    service = await ServiceModel.get_service_by_id(id=appointmentTO.service_id)
    appointment_approx_time = service.approximate_time
    appointment = AppointmentModel(user_id = appointmentTO.user_id,
                                   master_id = appointmentTO.master_id,
                                   date = appointmentTO.date,
                                   start_time = appointmentTO.start_time,
                                   end_time = _timedelta_to_time(_time_to_timedelta(appointmentTO.start_time)+_time_to_timedelta(_int_minutes_to_time(appointment_approx_time))),
                                   service_id = appointmentTO.service_id)
    status = AppointmentModel.create(appointment)
    return status

async def cancel_appointment(appointment_id):
    status = AppointmentModel.delete(id=appointment_id)
    return status

