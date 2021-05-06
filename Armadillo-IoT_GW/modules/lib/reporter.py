from abc import ABC, abstractmethod
from modules.lib.alarm_machine import AlarmMachine

class Reporter(ABC):
    __interval = 30

    @abstractmethod
    def data_type(self):
        pass

    @abstractmethod
    def report(self):
        pass

    def interval(self):
        return self.__interval

    def set_interval(self, interval):
        self.__interval = interval
        return self

    def set_alarm_condition(self, alarm_condition):
        if alarm_condition is None:
            self.__alarm_machine = None
            return

        self.__alarm_machine = AlarmMachine(alarm_condition)

    def alarm_machine(self):
        return self.__alarm_machine

    def __init__(self):
        self.__alarm_machine = None
