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