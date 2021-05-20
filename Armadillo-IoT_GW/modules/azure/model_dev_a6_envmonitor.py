from modules.azure.model_dev_base import ModelDevBase
from modules.azure.model_config_envmonitor import ModelConfigEnvMonitor
from modules.azure.environment_reporter_ex import EnvironmentReporterEx


class ModelDevA6EnvMonitor(ModelDevBase):
    def __init__(self, modelConfig):
        super().__init__(modelConfig, component_name="iot_gw_base")
        self._envReporter = None

    def model_id(self):
        return "dtmi:atmark_techno:Armadillo:IoT_GW_A6_EnvMonitor;1"

    def set_prop(self, name, value):
        # hide super()'s ModelConfigBase.THERMAL_SENSE_INTERVAL and it's read only property
        if name == ModelConfigEnvMonitor.INTERVAL:
            value = self._modelConfig.set_envsense_interval(value)
            if self._envReporter:
                self._envReporter.set_interval(value)
        return value

    def _aux_props(self):
        # hide super()'s ModelConfigBase.THERMAL_SENSE_INTERVAL
        return [
            (ModelConfigEnvMonitor.INTERVAL, self._modelConfig.envsense_interval())
        ]

    def _make_reporters(self, config):
        # hide super()'s CpuTempReporter
        reporters = []
        envReporter = EnvironmentReporterEx("env_sensor")
        envReporter.set_interval(config.envsense_interval())
        reporters.append(envReporter)
        self._envReporter = envReporter

        return reporters

#
# End of File
#
