import asyncio
import platform
import subprocess

from modules.lib.agent_utils import get_mac
from modules.lib.agent_utils import run_on_bash
from abc import ABC, abstractmethod

from modules.lib.report_queue import ReportQueue
from modules.lib.reporter_manager import ReporterManager

from modules.azure.cpu_temp_reporter import CpuTempReporter
from modules.azure.model_config_base import ModelConfigBase
from modules.azure.report_repository import AzureReportRepository


class ModelDevBase(ABC):
    def __init__(self, modelConfig, component_name=None):
        self._props = {}
        if platform.system() == "Windows":
            self._uniqueID = "armadillo-" + get_mac()
        else:
            self._uniqueID = subprocess.getoutput(
                "cat /proc/cpuinfo | grep Serial | sed \
                -e 's/ //g' | sed -e 's/\t//g' | cut -c 8-"
            )
        self._props["serialNumber"] = self._uniqueID
        if component_name is not None:
            props = self._props
            props["__t"] = "c"
            self._props = {}
            self._props[component_name] = props
            self._component_name = component_name
        else:
            self._component_name = None
        self._loopables    = []
        self._modelConfig  = modelConfig
        self._tempReporter = None

    def props(self):
        tmpProps = self._props.copy()
        for (k, v) in self._aux_props():
            tmpProps[k] = v
        return tmpProps

    def set_prop(self, name, value):
        if name == ModelConfigBase.THERMAL_SENSE_INTERVAL:
            value = self._modelConfig.set_thermal_sense_interval(value)
            if self._tempReporter:
                self._tempReporter.set_interval(value)
        elif name in self._props:
            self._props[name] = value
        return value

    @abstractmethod
    def model_id(self):
        pass

    def unique_id(self):
        return self._uniqueID

    def setup_reporters(self, config, iot_pnp_client, loop):
        queue        = ReportQueue()
        alaram_queue = ReportQueue()
        report_repository = AzureReportRepository(queue, alaram_queue, iot_pnp_client, loop)
        report_repository.set_interval(config.send_interval())
        manager = ReporterManager(queue, alaram_queue)
        reporters = self._make_reporters(self._modelConfig)
        for reporter in reporters:
            manager.listen_to(reporter)
        self._loopables.append(report_repository)
        self._loopables.append(manager)
        active_reporters = self._make_active_reporters(self._modelConfig, queue, report_repository)
        for reporter in active_reporters:
            self._loopables.append(reporter)

    def loopables(self):
        return self._loopables

    def report_repository(self):
        return self._loopables[0]

    async def execute_commnad(self, name, params):
        command_method = self._get_command_method(name)
        return await command_method(params) if command_method else None

    def is_valid_command(self, name):
        return True if self._get_command_method(name) else (False, None)

    def _aux_props(self):
        return [
            (ModelConfigBase.THERMAL_SENSE_INTERVAL, self._modelConfig.thermal_sense_interval())
        ]

    def _make_reporters(self, config):
        reporters = []

        tempReporter = CpuTempReporter()
        tempReporter.set_interval(config.thermal_sense_interval())
        reporters.append(tempReporter)
        self._tempReporter = tempReporter

        return reporters

    def _make_active_reporters(self, config, report_queue, report_repository):
        return []

    def _get_command_method(self, name):
        if self._component_name is not None:
            if (name in ('reboot', self._component_name + '*reboot')):
                return self._command_reboot
        elif (name == 'reboot'):
            return self._command_reboot
        else:
            return None

    async def _command_reboot(self, params):
        if not params:
            print("Error; no payload for reboot command")
            return False
        elif type(params) == int:
            delay = params
        elif type(params) == dict:
            if 'delay' not in params:
                print("Error; invalid command payload: ", params)
                return (False, None)
            delay = params['delay']

        print("Rebooting after delay of {delay}secs".format(delay=delay))
        await asyncio.sleep(delay)
        if platform.system() == "Windows":
            return (True, None)
        if self._modelConfig.disable_reboot():
            return (True, None)

        output = None
        (returncode, output) = run_on_bash('which reboot')
        if returncode != 0:
            print("Error; Could not execute system reboot command.")
            return (False, None)
        return (True, self._do_reboot)

    def _do_reboot(self):
         run_on_bash('reboot&')

#
# End of File
#
