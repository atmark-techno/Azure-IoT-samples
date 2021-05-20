from modules.reporters.environment_reporter import EnvironmentReporter


class EnvironmentReporterEx(EnvironmentReporter):
    def __init__(self, component_name):
        super().__init__()
        self._component_name = component_name

    def report(self):
        (report, alarm) = super().report()
        if report and self._component_name:
            report.reported_data['$.sub'] = self._component_name

        return (report, alarm)

#
# End of File
#

