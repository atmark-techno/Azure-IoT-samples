from modules.reporters.temperature_reporter import TemperatureReporter


class CpuTempReporter(TemperatureReporter):
    def report(self):
        (report, alarm) = super().report()
        if report:
            report.reported_data['type'] = "CPU_temp"

        return (report, alarm)

#
# End of File
#
