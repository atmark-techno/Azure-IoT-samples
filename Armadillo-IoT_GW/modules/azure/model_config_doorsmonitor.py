from modules.azure.model_config_base import ModelConfigBase


class ModelConfigDoorsMonitor(ModelConfigBase):
    DISABLE_WHITELIST = "disable_whitelist"

    def disable_whitelist(self):
        return self._configs.get(ModelConfigDoorsMonitor.DISABLE_WHITELIST, False)

    def set_disable_whitelist(self, value):
        self._configs[ModelConfigDoorsMonitor.DISABLE_WHITELIST] = value

    def _is_valid_conf_item(self, name, value):
        if name == ModelConfigDoorsMonitor.DISABLE_WHITELIST:
            if not isinstance(value, bool):
                print("Error! the setting value of ", name, " is not bool.")
                return False
            return True
        else:
            return super()._is_valid_conf_item(name, value)

#
# End of File
#

