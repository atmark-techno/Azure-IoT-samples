class AlarmCondition:
    latest_alarm_id = 0

    def __set_current_id(self):
        if AlarmCondition.latest_alarm_id == 0x7fffffff:
            AlarmCondition.latest_alarm_id = 0
        AlarmCondition.latest_alarm_id += 1
        return AlarmCondition.latest_alarm_id

    def alarm_type(self):
        return self.__alarm_type

    def description(self):
        return self.__description

    def __increment(self):
        self.__count += 1

    def is_active(self):
        return self.__is_active

    def __activate(self):
        self.__is_active = True
        self.__count = 0
        self.__set_current_id()

    def __deactivate(self):
        self.__is_active = False
        self.__count = 0
        self.__current_id = -1

    def check_generate(self, alarm_type, value):
        if self.__check_generate is None:
            return (False, -1)

        if self.__check_generate(alarm_type, value):
            self.__increment()
            if self.__count >= self.__generate_hysteresis:
                self.__activate()
                return (True, self.__current_id)
        else:
             self.__count = 0

        return (False, -1)

    def check_clear(self, alarm_type, value):
        if self.__check_clear is None:
            return (False, -1)

        if self.__check_clear(alarm_type, value):
            self.__increment()
            if self.__count >= self.__clear_hysteresis:
                current_id = self.__current_id
                self.__deactivate()
                return (True, current_id)
        else:
            self.__count = 0

        return (False, -1)

    def __init__(self, alarm_type, description,
                    generate_on, generate_hysteresis,
                    clear_on, clear_hysteresis):
        self.__alarm_type = alarm_type
        self.__description = description
        self.__check_generate = generate_on
        self.__generate_hysteresis = generate_hysteresis
        self.__check_clear = clear_on
        self.__clear_hysteresis = clear_hysteresis
        self.__is_active = False
        self.__count = 0
        self.__current_id = -1
