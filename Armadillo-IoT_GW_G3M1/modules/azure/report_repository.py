
import asyncio
import sys


from modules.lib.report_repository import ReportRepository
from modules.azure.iot_pnp_client import IoTPnPClient


class AzureReportRepository(ReportRepository):
    def __init__(self, report_queue, alarm_queue, iot_pnp_client, loop):
        super().__init__(report_queue, alarm_queue)
        self._iot_pnp_client = iot_pnp_client
        self._loop = loop

    def process_report(self, report):
        if report.data_type == 'measurement':
            reported_data = report.reported_data
            telemetry_data = {reported_data['type']: reported_data['value']}
            self._send_telemetry(telemetry_data)
            return True
        else:
            return False

    def process_reports(self, reports):
        if len(reports) == 1:
            return self.process_report(repreports[0])
        else:
            measurements = []
            for report in reports:
                if report.data_type == 'measurement':
                    reported_data = report.reported_data
                    telemetry_data = {reported_data['type']: reported_data['value']}
                    measurements.append(telemetry_data)
            if measurements:
                self._send_telemetry(measurements)
                return True
            else:
                return False

    def process_alarm(self, alarm):
        print("Sorry, but ", type(self).__name__, ".", "process_alarm()", " is not implemented yet. alarm.is_activate= ", alaram.is_activate, sep="")
        return True

    def dispatch_operation(self):
#        print("Sorry, but ", type(self).__name__, ".", "dispatch_operation()", " is not implemented yet.", sep="")
        return False

    def _send_telemetry(self, telemetry_data):
        future = asyncio.run_coroutine_threadsafe(
            self._iot_pnp_client.send_telemetry(telemetry_data), self._loop
        )
        future.result()