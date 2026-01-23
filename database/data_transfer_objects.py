

class AppointmentTO():
    def __init__(self, user_id, master_id, date, time, service_id):
        self.user_id = user_id
        self.master_id = master_id
        self.date = date
        self.time = time
        self.service_id = service_id