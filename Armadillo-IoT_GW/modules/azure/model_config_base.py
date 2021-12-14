import json


class ModelConfigBase:
    AUTH                   = "auth"
    SEND_INTERVAL          = "send_interval"
    THERMAL_SENSE_INTERVAL = "thermalsense_interval"
    DISABLE_REBOOT         = "disable_reboot"

    IOTHUB_DEVICE_DPS_AUTH_MODE  = "mode"
    IOTHUB_DEVICE_DPS_ENDPOINT   = "IOTHUB_DEVICE_DPS_ENDPOINT"
    IOTHUB_DEVICE_DPS_ID_SCOPE   = "IOTHUB_DEVICE_DPS_ID_SCOPE"
    IOTHUB_DEVICE_DPS_DEVICE_ID  = "IOTHUB_DEVICE_DPS_DEVICE_ID"
    IOTHUB_DEVICE_DPS_DEVICE_KEY = "IOTHUB_DEVICE_DPS_DEVICE_KEY"

    IOTHUB_DEVICE_DPS_X509_CERT  = "IOTHUB_DEVICE_DPS_X509_CERT"
    IOTHUB_DEVICE_DPS_X509_KEY   = "IOTHUB_DEVICE_DPS_X509_KEY"
    IOTHUB_DEVICE_DPS_X509_PASS  = "IOTHUB_DEVICE_DPS_X509_PASS"

    X509_CERT_MODE     = "x509-cert"
    SYMMETRIC_KEY_MODE = "symmetric-key"

    def __init__(self):
        self._configs = {}

    def load(self, config_file_path):
        with open(config_file_path, 'r') as f:
            config = json.load(f)
            for key in config.keys():
                val = config[key]
                if (self._is_valid_conf_item(key, val)):
                    self._configs[key] = val
        if not self._configs.get(ModelConfigBase.AUTH):
            print("Error! auth setting not found.")
            return False
        else:
            return True

    def auth_props(self):
        return self._configs[ModelConfigBase.AUTH]

    def send_interval(self):
        return self._configs.get(ModelConfigBase.SEND_INTERVAL, 30)

    def thermal_sense_interval(self):
        return self._configs.get(ModelConfigBase.THERMAL_SENSE_INTERVAL, 5)

    def disable_reboot(self):
        return self._configs.get(ModelConfigBase.DISABLE_REBOOT, False)

    def set_thermal_sense_interval(self, value):
        curr_value = self.thermal_sense_interval()
        if value <= 0:
            value = curr_value
        elif value != curr_value:
            print("change ", ModelConfigBase.THERMAL_SENSE_INTERVAL, " is changed to ", value)
            self._configs[ModelConfigBase.THERMAL_SENSE_INTERVAL] = value
        return value

    def _is_valid_conf_item(self, name, value):
        if (name == ModelConfigBase.AUTH):
            if not isinstance(value, dict):
                print("Error! the setting value of ", name, " is invalid.")
                return False
            elif not ModelConfigBase._is_valid_auth_conf(value):
                print("Error! invalid auth conf.")
                return False
            return True
        elif (name in [ModelConfigBase.SEND_INTERVAL, ModelConfigBase.THERMAL_SENSE_INTERVAL]):
            if not isinstance(value, int):
                print("Error! the setting value of ", name, " is not integer.")
                return False
            elif (value == 0):
                print("Warning; the setting value of ", name,
                      " is 0, so use default value.")
            return True
        elif (name == ModelConfigBase.DISABLE_REBOOT):
            if not isinstance(value, bool):
                print("Error! the setting value of ", name, " is not bool.")
                return False
            return True
        else:
            print("Warning; unknown setting item: ", name)
            return False

    def is_x509_mode(self):
        auth_conf = self.auth_props()
        return auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_AUTH_MODE] == ModelConfigBase.X509_CERT_MODE

    @staticmethod
    def _is_valid_auth_conf(value):
        if not value.get(ModelConfigBase.IOTHUB_DEVICE_DPS_ENDPOINT):
            value.put(ModelConfigBase.IOTHUB_DEVICE_DPS_ENDPOINT, "global.azure-devices-provisioning.net")
        elif not value.get(ModelConfigBase.IOTHUB_DEVICE_DPS_ID_SCOPE):
            print("Error! IOTHUB_DEVICE_DPS_ID_SCOPE not found")
            return False
        elif not value.get(ModelConfigBase.IOTHUB_DEVICE_DPS_DEVICE_ID):
            print("Error! IOTHUB_DEVICE_DPS_DEVICE_ID not found")
            return False
        elif not ModelConfigBase._is_valid_auth_param(value):
            return False
        else:
            return True

    @staticmethod
    def _is_valid_auth_param(value):
        if not value.get(ModelConfigBase.IOTHUB_DEVICE_DPS_AUTH_MODE) \
            or value.get(ModelConfigBase.IOTHUB_DEVICE_DPS_AUTH_MODE) == ModelConfigBase.SYMMETRIC_KEY_MODE:
            if not value.get(ModelConfigBase.IOTHUB_DEVICE_DPS_DEVICE_KEY):
                print("Error! IOTHUB_DEVICE_DPS_DEVICE_KEY not found")
                return False
            else:
                return True
        elif (value.get(ModelConfigBase.IOTHUB_DEVICE_DPS_AUTH_MODE) == ModelConfigBase.X509_CERT_MODE):
            if not value.get(ModelConfigBase.IOTHUB_DEVICE_DPS_X509_CERT):
                print("Error! IOTHUB_DEVICE_DPS_X509_CERT not found")
                return False
            elif not value.get(ModelConfigBase.IOTHUB_DEVICE_DPS_X509_KEY):
                print("Error! IOTHUB_DEVICE_DPS_X509_KEY not found")
                return False
            elif value.get(ModelConfigBase.IOTHUB_DEVICE_DPS_X509_PASS) is None:
                print("Error! IOTHUB_DEVICE_DPS_X509_PASS not found")
                return False
            else:
                return True
        else:
            return False
#
# End of File
#

