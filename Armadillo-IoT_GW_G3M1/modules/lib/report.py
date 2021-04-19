from datetime import datetime


class Report:
    def __init__(self, data_type, reported_at, reported_data):
        self.data_type = data_type
        self.reported_at = reported_at
        self.reported_data = reported_data

    @classmethod
    def report_now(cls, data_type, **kwargs):
        return cls(data_type, datetime.now(), kwargs)
