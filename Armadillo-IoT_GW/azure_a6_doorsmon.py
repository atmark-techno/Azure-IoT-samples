import asyncio

from modules.azure.azure_iot import mainloop
from modules.azure.model_config_base import ModelConfigBase
from modules.azure.model_config_doorsmonitor import ModelConfigDoorsMonitor
from modules.azure.model_dev_a6_doorsmonitor import ModelDevA6DoorsMonitor


def main():
    asyncio.run(mainloop(ModelDevA6DoorsMonitor, ModelConfigDoorsMonitor, "./a6_doorsmon_config.json"))
if __name__ == '__main__':
    main()

#
# End of File
#
