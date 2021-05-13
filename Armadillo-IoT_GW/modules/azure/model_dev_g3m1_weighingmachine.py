
from modules.azure.model_dev_base import ModelDevBase
from modules.azure.weightcode_reporter import WeightCodeReporter


class ModelDevG3M1WeighingMachine(ModelDevBase):
    def __init__(self, modelConfig):
        super().__init__(modelConfig)
        self._weightcode_reporter = None

    def model_id(self):
        return "dtmi:atmark_techno:Armadillo:IoT_GW_G3M1_WeighingMachine;1"

    def _make_active_reporters(self, config, report_queue, report_repository):
        reporters = []
 
        weight_code_reporter = WeightCodeReporter(report_queue, report_repository)
        reporters.append(weight_code_reporter)
        self._weightcode_reporter = weight_code_reporter
        self._props[WeightCodeReporter.WEIGHING_STATUS] = weight_code_reporter.weighing_status()

        return reporters

#
# End of File
#
