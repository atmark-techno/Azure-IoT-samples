from modules.azure.model_config_base import ModelConfigBase


class ModelConfigEnvMonitor(ModelConfigBase):
    INTERVAL = "envsense_interval"

    def envsense_interval(self):
        return self._configs.get(ModelConfigEnvMonitor.INTERVAL, 10)

    def set_envsense_interval(self, value):
        curr_value = self.envsense_interval()
        if value <= 0:
            value = curr_value
        elif value != curr_value:
            print("", ModelConfigEnvMonitor.INTERVAL, " is changed to ", value)
            self._configs[ModelConfigEnvMonitor.INTERVAL] = value
        return value

    def _is_valid_conf_item(self, name, value):
        if name == ModelConfigEnvMonitor.INTERVAL:
            if not isinstance(value, int):
                print("Error! the setting value of ", name, " is not integer.")
                return False
            elif value <= 0:
                print("Warning; the setting value of ", name,
                      " is less than or equal 0, so use default value.")
            return True
        else:
            return super()._is_valid_conf_item(name, value)

#
# End of File
#

