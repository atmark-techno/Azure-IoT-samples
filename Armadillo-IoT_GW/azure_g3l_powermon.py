import asyncio

from modules.azure.azure_iot import AzureIoT, mainloop
from modules.azure.model_config_powermonitor import ModelConfigPowerMonitor
from modules.azure.model_dev_g3l_powermonitor import ModelDevG3LPowerMonitor


def main():
    asyncio.run(mainloop(
        ModelDevG3LPowerMonitor, ModelConfigPowerMonitor, "g3l_powermon_config.json"))

if __name__ == '__main__':
    main()

#
# End of File
#
