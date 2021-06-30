
from modules.azure.model_dev_base import ModelDevBase
from modules.azure.weightcode_reporter import WeightCodeReporter
from modules.azure.weightcode_reporter import DeviceModel

class ModelDevA6WeighingMachine(ModelDevBase):
    def __init__(self, modelConfig):
        super().__init__(modelConfig, component_name="iot_gw_base")
        self._weightcode_reporter = None

    def model_id(self):
        return "dtmi:atmark_techno:Armadillo:IoT_GW_A6_WeighingMachine;1"

    def _make_active_reporters(self, config, report_queue, report_repository):
        reporters = []
 
        weight_code_reporter = WeightCodeReporter(report_queue, report_repository, DeviceModel.A6)
        reporters.append(weight_code_reporter)
        self._weightcode_reporter = weight_code_reporter
        self._props[WeightCodeReporter.WEIGHING_STATUS] = weight_code_reporter.weighing_status()

        return reporters

    def _make_reporters(self, config):
        # hide super()'s CpuTempReporter
        reporters = []
        return reporters

#
# End of File
#
