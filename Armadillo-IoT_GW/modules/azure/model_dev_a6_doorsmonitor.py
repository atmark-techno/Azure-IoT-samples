from modules.azure.model_dev_base import ModelDevBase
from modules.azure.door_status_reporter import DoorStatusReporter

class ModelDevA6DoorsMonitor(ModelDevBase):
    SID_WHITE_LIST = "sid_whitelist"

    def __init__(self, modelConfig):
        super().__init__(modelConfig, component_name="iot_gw_base")
        self._door_status_reporter = None

    def model_id(self):
        return "dtmi:atmark_techno:Armadillo:IoT_GW_A6_DoorsMonitor;3"

    def set_prop(self, name, value):
        if name == ModelDevA6DoorsMonitor.SID_WHITE_LIST:
            if self._door_status_reporter:
                self._door_status_reporter.set_sid_sensor_list(value)
        elif name in self._props:
            self._props[name] = value
        return value

    def _make_active_reporters(self, config, report_queue, report_repository):
        reporters = []
        door_status_reporter = DoorStatusReporter(report_queue, 
                                                  report_repository, 
                                                  config.disable_whitelist(),
                                                  component_name="door_sensor")
        reporters.append(door_status_reporter)
        self._door_status_reporter = door_status_reporter
        return reporters

    def _make_reporters(self, config):
        # hide super()'s CpuTempReporter
        reporters = []
        return reporters
#   
# End of File
#
