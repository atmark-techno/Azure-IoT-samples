import re
import subprocess

from modules.lib.reporter import Reporter
from modules.lib.report import Report


class SignalQualityReporter(Reporter):
    def data_type(self):
        return 'signal_quality'

    def report(self):
        signal_quality = 0
        try:
            cmd = 'mmcli -m 0'.split()
            output = subprocess.check_output(cmd).decode()
            pattern = "signal quality: '([0-9]+)'"
            matched = re.search(pattern, output)

            if matched is not None:
                signal_quality = int(matched.groups()[0])
        except subprocess.CalledProcessError:
            pass

        return Report.report_now(
            'measurement',
            type='signal_quality',
            key='lte',
            value=signal_quality,
            unit='%'
        ), None # no alarm
