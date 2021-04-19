import asyncio
import platform
import subprocess

from modules.lib.agent_utils import get_mac
from modules.lib.agent_utils import run_on_bash

from modules.azure.cpu_temp_reporter import CpuTempReporter
from modules.azure.model_config_base import ModelConfigBase


class ModelDevBase:
    def __init__(self, modelConfig):
        self._props = {}
        if platform.system() == "Windows":
            self._uniqueID = "armadillo-" + get_mac()
        else:
            self._uniqueID = subprocess.getoutput(
                "cat /proc/cpuinfo | grep Serial | sed \
                -e 's/ //g' | sed -e 's/\t//g' | cut -c 8-"
            )
        self._props["serialNumber"] = self._uniqueID
        self._props[ModelConfigBase.THERMAL_SENSE_INTERVAL] = modelConfig.thermal_sense_interval()
        self._modelConfig  = modelConfig
        self._tempReporter = None

    def props(self):
        return self._props

    def set_prop(self, name, value):
        if name == ModelConfigBase.THERMAL_SENSE_INTERVAL:
            value = self._modelConfig.set_thermal_sense_interval(value)
            if self._tempReporter:
                self._tempReporter.set_interval(value)
        if name in self._props:
            self._props[name] = value
        return value

    def model_id(self):
        return "dtmi:atmark_techno:Armadillo:IoT_GW_G3M1;2"

    def unique_id(self):
        return self._uniqueID

    def make_reporters(self, config):
        reporters = []

        tempReporter = CpuTempReporter()
        tempReporter.set_interval(config.thermal_sense_interval())
        reporters.append(tempReporter)
        self._tempReporter = tempReporter

        return reporters

    async def execute_commnad(self, name, params):
        command_method = self._get_command_method(name)
        return await command_method(params) if command_method else None

    def is_valid_command(self, name):
        return True if self._get_command_method(name) else (False, None)

    def _get_command_method(self, name):
        if (name == 'reboot'):
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
