import asyncio
import platform
import subprocess

from modules.azure.azure_iot import AzureIoT, mainloop
from modules.azure.model_config_envmonitor import ModelConfigEnvMonitor
from modules.azure.model_dev_a6_envmonitor import ModelDevA6EnvMonitor


def main():
    if platform.system() == "Linux":
        subprocess.getoutput(
            "echo 0590 00D4 >/sys/bus/usb-serial/drivers/ftdi_sio/new_id"
        )
    asyncio.run(mainloop(
        ModelDevA6EnvMonitor, ModelConfigEnvMonitor, "a6_envmon_config.json"))

if __name__ == '__main__':
    main()

#
# End of File
#

