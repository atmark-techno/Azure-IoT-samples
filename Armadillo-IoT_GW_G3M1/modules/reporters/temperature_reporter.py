from modules.lib.reporter import Reporter
from modules.lib.report import Report
from modules.lib.alarm_machine import AlarmMachine


class TemperatureReporter(Reporter):
    def data_type(self):
        return 'temperature'

    def report(self):
        with open('/sys/class/thermal/thermal_zone0/temp') as file:
            temp = int(file.read()) / float(1000)
        report = Report.report_now(
            'measurement',
            type='temperature',
            key='zone_0',
            value=temp,
            unit='c'
        )

        alarm = None
        if self.alarm_machine() is not None:
            alarm = self.alarm_machine().judge('temperature', temp,
                                               report.reported_at)
        return report, alarm
