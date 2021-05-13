import asyncio
import datetime
from datetime import datetime
from enum import Enum
from time import time
from time import localtime, strftime
from serial import Serial
from serial.tools.list_ports import comports

from modules.lib.report import Report
from modules.lib.ttylib import ALX3601
from modules.lib.ttylib import port
from modules.lib.active_reporter import ActiveReporter
from modules.lib.led_blinker import LedBlinker


def get_other_port(vid, pid):
    vid = int(vid, 16)
    pid = int(pid, 16)

    for i in comports():
        if i.vid == 11388:
            continue  # ignore LTE module's COM port
        if i.vid != vid or i.pid != pid:
            return i.device
    return None

def make_qrcode_reader():
    return ALX3601(port("065A","A002"))

class WeighingState(Enum):
    WAIT_MEASUREMENT   = 1,
    GOT_MEASURED_VALUE = 2,
    READY_REPORT       = 3


class WeightCodeReporter(ActiveReporter):
    WEIGHING_STATUS = "weighing_status"
    SART_TIME   = "start_time"
    LAST_TIME   = "last_time"
    COUNT       = "count"
    ERROR_COUNT = "error_count"

    TZ_INFO = strftime("%z", localtime())
    INVALID_TIME = datetime.fromtimestamp(0).isoformat() + "Z"

    def __init__(self, report_queue, report_repository, port=None):
        super().__init__(report_queue, report_repository)
        self._curr_state     = WeighingState.WAIT_MEASUREMENT
        self._measured_val   = 0.0
        self._measure_time   = ''
        self._item_code      = ''
        if port is None:
            port = get_other_port("065A","A002")
            if port is None:
                raise Exception("weighin machine's COM port is not found")
        self._weigh_machine  = Serial(port, timeout=1.0)
        self._qrcode_reader  = make_qrcode_reader()
        self._weighing_status = {
            WeightCodeReporter.SART_TIME: WeightCodeReporter.INVALID_TIME,
            WeightCodeReporter.LAST_TIME: WeightCodeReporter.INVALID_TIME,
            WeightCodeReporter.COUNT: 0,
            WeightCodeReporter.ERROR_COUNT: 0
        }
        self._weigh_machine.close()
        self._led_blinker = LedBlinker("led2", ["led3", "led4"])
        self._led_task = asyncio.get_event_loop().create_task(self._led_blinker.run())

    def weighing_status(self):
        return self._weighing_status

    def weighing_status_prop(self):
        return {WeightCodeReporter.WEIGHING_STATUS: self._weighing_status}

    def request_stop(self):
        super().request_stop()
        # 必要ならブロッキング I/O をキャンセル.
        #   xxx

    def _before_loop(self):
        self._weigh_machine.open()
        self._led_blinker.start_blink()

    def _after_loop(self):
        self._led_blinker.request_stop()
        self._weigh_machine.close()

    def _handle_state(self):
        if WeighingState.WAIT_MEASUREMENT == self._curr_state:
            self._handle_wait_measurement()
        elif WeighingState.GOT_MEASURED_VALUE == self._curr_state:
            self._handle_got_measured_value()
        elif WeighingState.READY_REPORT == self._curr_state:
            self._handle_ready_report()

    def _do_transit_action(self, next_state):
        # next_state の値に応じて LED 点灯制御
        #   xxx
        print("transient to the state ", next_state)

    def _handle_wait_measurement(self):
        bytes = self._weigh_machine.read_until('\r\n')
        length = len(bytes) if bytes is not None else 0
        if 0 == length:
            return  # timed out
        elif (length <= 2) or (('\r' != bytes[length - 2]) or ('\n' != bytes[length - 1])):
            tempBuf = bytearray(bytes)
            tempBuf.join(self._weigh_machine.read_until('\r\n'))
        try:
            self._measured_val = WeightCodeReporter._parse_weight_data(bytes)
        except:
            print("got an error on weighing!")
            self._weighing_status[WeightCodeReporter.ERROR_COUNT] += 1
            return
        self._measure_time = datetime.now().isoformat() + WeightCodeReporter.TZ_INFO
        self._transit_state(WeighingState.GOT_MEASURED_VALUE)
        # It should be add error handling

    def _handle_got_measured_value(self):
        decoded_str = self._qrcode_reader.trigger_read()
        self._item_code = decoded_str
        self._transit_state(WeighingState.READY_REPORT)
        pass

    def _handle_ready_report(self):
        # make report and enqueue it
        report = Report.report_now(
            'measurement',
            type='item_weight',
            key='tl-280',
            value={
                'item': self._item_code,
                'weight': self._measured_val,
                'weighed_time': self._measure_time},
            unit='g'
        )
        self._report_queue.push(report)

        # update the weighing status and reflect to digital twin
        self._weighing_status[WeightCodeReporter.LAST_TIME] = self._measure_time
        if 0 == self._weighing_status[WeightCodeReporter.COUNT]:
            self._weighing_status[WeightCodeReporter.SART_TIME] = self._measure_time
        self._weighing_status[WeightCodeReporter.COUNT] += 1
        self._report_repository.send_updated_prop(self.weighing_status_prop())

        # update status
        self._transit_state(WeighingState.WAIT_MEASUREMENT)

    @staticmethod
    def _parse_weight_data(weight_data):
        try:
            str = weight_data.decode(encoding='utf-8') if type(weight_data) is bytes else weight_data
            tokens = str.split(',')
            val    = int(tokens[tokens.index('Wg') + 1])
            return float(val)
        except (ValueError, IndexError):
            raise Exception("invalid weight data")

#
# End of File
#

