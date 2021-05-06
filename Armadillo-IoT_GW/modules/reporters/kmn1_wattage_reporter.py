from time import sleep
from pymodbus.client.sync import ModbusSerialClient
from modules.lib.alarm_machine import AlarmMachine
from modules.lib.reporter import Reporter
from modules.lib.report import Report

class Kmn1WattageReporter(Reporter):
    def data_type(self):
        return 'wattage'

    def report(self):
        value = round(self.wattage(), 4)
        report= Report.report_now(
            'measurement',
            type='wattage',
            key='kmn1',
            value=value,
            unit='W'
        )

        alarm = None
        if self.alarm_machine() is not None:
            alarm = self.alarm_machine().judge('wattage', value, report.reported_at)

        return report, alarm

    def __init__(self, port='/dev/ttymxc0', baudrate=9600, unit=1,
                    parity="E", waittime=20, stopbits=1):
        super().__init__()
        self.client = ModbusSerialClient(
                            method='rtu',
                            port=port,
                            baudrate=baudrate,
                            parity=parity,
                            stopbits=stopbits)

        self.unit = unit
        self.waittime = waittime / 100

    def voltage(self):
        data = self.client.read_holding_registers(0x0000, 2, unit=self.unit)
        sleep(self.waittime)
        return (data.registers[0] * 65536 + data.registers[1]) / 10

    def current(self):
        data = self.client.read_holding_registers(0x0006, 2, unit=self.unit)
        sleep(self.waittime)
        return (data.registers[0] * 65536 + data.registers[1]) / 1000

    def wattage(self):
        voltage = self.voltage()
        current = self.current()
        return voltage * current
