

class AppointmentTO():
    def __init__(self, user_id, master_id, date, start_time, end_time, service_id):
        self.user_id = user_id
        self.master_id = master_id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.service_id = service_id
