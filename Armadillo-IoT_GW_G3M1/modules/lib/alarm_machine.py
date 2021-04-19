from modules.lib.alarm import Alarm
from modules.lib.alarm_condition import AlarmCondition

class AlarmMachine:
    def judge(self, alarm_type, value, now):
        alarm = None
        if self.__condition is None:
            return None

        for cond in self.__condition:
            if cond.is_active():
                (result, alarm_id) = cond.check_clear(alarm_type, value)
                if result:
                    alarm = Alarm(cond.alarm_type(), cond.description(),
                                    alarm_id, is_activate=False, time=now)
            else:
                (result, alarm_id) = cond.check_generate(alarm_type, value)
                if result:
                    alarm = Alarm(cond.alarm_type(), cond.description(),
                                    alarm_id, is_activate=True, time=now)

        return alarm


    def __init__(self, condition):
        self.__condition = condition
