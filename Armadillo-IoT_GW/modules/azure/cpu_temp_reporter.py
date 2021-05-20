from modules.reporters.temperature_reporter import TemperatureReporter


class CpuTempReporter(TemperatureReporter):
    def __init__(self, component_name=None):
        super().__init__()
        self._component_name = component_name

    def report(self):
        (report, alarm) = super().report()
        if report:
            report.reported_data['type'] = "CPU_temp"
            if self._component_name:
                report.reported_data['$.sub'] = self._component_name

        return (report, alarm)

#
# End of File
#
