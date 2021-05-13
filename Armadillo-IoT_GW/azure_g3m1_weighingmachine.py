
import asyncio

from modules.azure.azure_iot import mainloop
from modules.azure.model_config_base import ModelConfigBase
from modules.azure.model_dev_g3m1_weighingmachine import ModelDevG3M1WeighingMachine


def main():
    asyncio.run(mainloop(ModelDevG3M1WeighingMachine, ModelConfigBase, "./config.json"))

if __name__ == '__main__':
    main()

#
# End of File
#
