import datetime as dt

class Alarm:
    @property
    def alarm_type(self):
        return self.__alarm_type

    @property
    def time(self):
        return self.__time

    @property
    def description(self):
        return self.__description

    @property
    def severity(self):
        return self.__severity

    def to_dict(self, source, status='ACTIVE'):
        return {
            'type': self.__alarm_type,
            'time': self.__time.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'text': self.__description,
            'severity': self.__severity,
            'status': status,
            'source': source,
        }

    def __init__(self, alarm_type, description, alarm_id, severity='WARNING',
                                                 time=None, is_activate=True):
        if time is None:
            time = dt.datetime.now()

        self.__alarm_type = alarm_type
        self.__time = time
        self.__description = description
        self.__severity = severity
        self.is_activate = is_activate
        self.alarm_id = alarm_id
