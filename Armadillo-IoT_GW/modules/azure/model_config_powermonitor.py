from modules.azure.model_config_base import ModelConfigBase


class ModelConfigPowerMonitor(ModelConfigBase):
    ALERT_CONF = "powermonitor_alert_conf"
    INTERVAL   = "powermonitor_interval"

    THRESHOLD = "threshold"
    ENABLED   = "enabled"

    def __init__(self):
        default_alert_conf = {
            ModelConfigPowerMonitor.THRESHOLD: 0.0,
            ModelConfigPowerMonitor.ENABLED: False
        }
        super().__init__()
        self._configs[ModelConfigPowerMonitor.ALERT_CONF] = default_alert_conf

    def alert_conf(self):
        return self._configs[ModelConfigPowerMonitor.ALERT_CONF]

    def powermonitor_interval(self):
        return self._configs.get(ModelConfigPowerMonitor.INTERVAL, 10)

    def set_alert_config(self, value):
        curr_value = self.alert_conf()
        if (value[ModelConfigPowerMonitor.ENABLED]
        and value[ModelConfigPowerMonitor.THRESHOLD] <= 0.0):
            value = curr_value
        elif value != curr_value:
            print("", ModelConfigPowerMonitor.ALERT_CONF, " is changed to ", value)
            self._configs[ModelConfigPowerMonitor.ALERT_CONF] = value
        return value

    def set_powermonitor_interval(self, value):
        curr_value = self.powermonitor_interval()
        if value <= 0:
            value = curr_value
        elif value != curr_value:
            print("", ModelConfigPowerMonitor.INTERVAL, " is changed to ", value)
            self._configs[ModelConfigPowerMonitor.INTERVAL] = value
        return value

    def _is_valid_conf_item(self, name, value):
        if (name == ModelConfigPowerMonitor.ALERT_CONF):
            if not isinstance(value, dict):
                print("Error! the setting value of ", name, " is invalid.")
                return False
            elif not ModelConfigPowerMonitor._is_valid_alert_conf(value):
                print("Error! invalid alert conf.")
                return False
            return True
        elif (name == ModelConfigPowerMonitor.INTERVAL):
            if not isinstance(value, int):
                print("Error! the setting value of ", name, " is not integer.")
                return False
            elif (value == 0):
                 print("Warning; the setting value of ", name,
                       " is 0, so use default value.")
            return True
        else:
            return super()._is_valid_conf_item(name, value)

    @staticmethod
    def _is_valid_alert_conf(value):
        if not value.get(ModelConfigPowerMonitor.THRESHOLD):
            return False
        else:
            th = value[ModelConfigPowerMonitor.THRESHOLD]
            if not isinstance(th, int) and not isinstance(th, float):
                print("Error! the setting value of ", name, " is not a number.")
                return False
        if value.get(ModelConfigPowerMonitor.ENABLED) is None:
            return False
        else:
            en = value[ModelConfigPowerMonitor.ENABLED]
            if not isinstance(en, bool):
                print("Error! the setting value of ", name, " is not bool.")
                return False
        return True

# 
# End of File
#
