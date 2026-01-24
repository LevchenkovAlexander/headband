

class AppointmentTO():
    def __init__(self, user_id, master_id, date, start_time, end_time, service_id):
        self.user_id = user_id
        self.master_id = master_id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.service_id = service_id

class MasterTO():
    def __init__(self, master_id, photo_path, name, working_day_start, working_day_end, day_off):
        self.master_id = master_id
        self.photo_path = photo_path
        self.name = name
        self.working_day_start = working_day_start
        self.working_day_end = working_day_end
        self.day_off = day_off