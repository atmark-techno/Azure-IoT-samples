import asyncio

from modules.azure.azure_iot import mainloop
from modules.azure.model_config_base import ModelConfigBase
from modules.azure.model_dev_a6_weighingmachine import ModelDevA6WeighingMachine

def main():
    asyncio.run(mainloop(ModelDevA6WeighingMachine, ModelConfigBase, "./a6_weighingmachine_config.json"))
if __name__ == '__main__':
    main()

#
# End of File
#
