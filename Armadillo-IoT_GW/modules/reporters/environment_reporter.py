from crcmod.predefined import mkPredefinedCrcFun
from crcmod.predefined import PredefinedCrc
from serial import Serial
from serial.tools.list_ports import comports

from modules.lib.report import Report
from modules.lib.reporter import Reporter
from modules.azure.report_repository import AzureReportRepository


def get_port(vid, pid):
    for dev in comports():
        if (dev.vid == vid) and (dev.pid == pid):
            return dev.device
    return None

def read16bit_value(bytes, pos, unit):
    val = bytes[pos] + (bytes[pos + 1] << 8)
    return (val * unit)

def read32bit_value(bytes, pos, unit):
    val = bytes[pos] + (bytes[pos + 1] << 8) + (bytes[pos + 2] << 16) + (bytes[pos + 3] << 24)
    return (val * unit)


class EnvSensor:
    def __init__(self, port):
        if port:
            self._com = Serial(port, baudrate=115200, timeout=1.0)
            if self._com is None:
                raise Exception("environment sensor is not found")
        else:
            raise Exception("no such environment sensor COM port")
        self._crc16func = mkPredefinedCrcFun('crc-16')
        self._crc16obj  = PredefinedCrc('crc-16')

    def read_datas(self):
        datas = None
        self._send_command_for_read(0x5012)
        resp = self._recv_response()
        if resp:
            datas = EnvSensor._parse_latest_sensing_data(resp)
        self._send_command_for_read(0x5013)
        resp = self._recv_response()
        if resp:
            calc_datas = EnvSensor._parse_latest_calculation_data(resp)
            if datas:
                datas.update(calc_datas)
            else:
                datas = calc_datas

        return datas

    def _send_command_for_read(self, addr):
        command = bytearray([0x52, 0x42, 0x05, 0x00, 0x01, (addr & 0xFF), (addr >> 8)])
        crc = self._crc16func(command, crc=0xFFFF)
        command.append(crc & 0xFF)
        command.append(crc >> 8)
        self._com.write(command)

    def _recv_response(self):
        resp_header = self._com.read(5)
        if (resp_header[0] != 0x52) or (resp_header[1] != 0x42):
            return None
        resp_len = resp_header[2] + (resp_header[3] << 8)
        if (resp_header[4] & 0x80):
            ignore_bytes = self._com.read(resp_len - 1)
            return None  # error response
        payload_len = resp_len - 2
        resp_body = self._com.read(payload_len - 1)
        self._crc16obj.crcValue = 0xFFFF
        self._crc16obj.update(resp_header)
        self._crc16obj.update(resp_body)
        resp_crc = (self._com.read())[0] + ((self._com.read())[0] << 8)
        if (resp_crc != self._crc16obj.crcValue):
            print("unexpected CRC value on response: ", resp_crc)
            return None

        return resp_body

    @staticmethod
    def _parse_latest_sensing_data(resp):
        datas = {}

        # skip addr and sequence number
        pos = 2   # skip addr
        pos += 1  # sequence number

        # read rest fields
        datas["temperature"]  = read16bit_value(resp, pos, 0.01)
        pos += 2
        datas["humidity"]     = read16bit_value(resp, pos, 0.01)
        pos += 2
        datas["illuminance"]  = read16bit_value(resp, pos, 1)
        pos += 2
        datas["air_pressure"] = read32bit_value(resp, pos, 0.001)
        pos += 4
        datas["sound_noise"]  = read16bit_value(resp, pos, 0.01)
        pos += 2
        datas["e_tvoc"] = read16bit_value(resp, pos, 1)
        pos += 2
        datas["e_co2"]  = read16bit_value(resp, pos, 1)

        return datas

    @staticmethod
    def _parse_latest_calculation_data(resp):
        datas = {}

        # skip addr and sequence number
        pos = 2
        pos += 1

        # read rest fields
        datas["discomfort_index"]      = read16bit_value(resp, pos, 0.01)
        pos += 2
        datas["heat_stroke_alarmness"] = read16bit_value(resp, pos, 0.01)
        pos += 2
        datas["vibr_info"] = resp[pos]

        return datas


class EnvironmentReporter(Reporter):
    def __init__(self):
        self._env_sensor = EnvSensor(get_port(0x0590, 0x00D4))

    def data_type(self):
        return "environment"

    def report(self):
        env_datas = self._env_sensor.read_datas()
        if env_datas:
            report = Report.report_now(
               'measurement',
               type=AzureReportRepository.BAG_OF_REPORT,
               key="",
               value=env_datas,
               unit=""
            )
        else:
            report = None
        return (report, None)

#
# End of File
#
