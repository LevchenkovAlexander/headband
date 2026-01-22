from headband.database import AppointmentModel, MasterModel, ServiceModel
from datetime import time, timedelta
def _int_minutes_to_time(minutes: int) -> time:
    hours = minutes // 60
    mins = minutes % 60
    return time(hour=hours, minute=mins)

def _time_to_timedelta(t: time) -> timedelta:
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

def _timedelta_to_int_minutes(td: timedelta) -> int:
    return int(td.total_seconds() // 60)

async def get_possible_start_time(master_id, app_date, service_id):
    #TODO обработка выходных


    appointments = await AppointmentModel.get_by_master_and_date(master_id=master_id, date=app_date)
    master = await MasterModel.get_master_by_id(id=master_id)
    day_start = master.working_day_start
    day_end = master.working_day_end
    end_time = []
    end_time.append(_time_to_timedelta(day_start))
    start_time = []
    for appointment in appointments:
        start_time.append(_time_to_timedelta(appointment.time))
        service_for_gap = await ServiceModel.get_service_by_id(id=appointment.service_id)
        approx_time_for_gap = service_for_gap.approximate_time
        end_time.append(_time_to_timedelta(appointment.time)+_time_to_timedelta(_int_minutes_to_time(approx_time_for_gap)))
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
        return None, False
    else:
        return possible_starts, True