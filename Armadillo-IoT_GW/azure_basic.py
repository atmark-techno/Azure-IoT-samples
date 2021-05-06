import asyncio

from modules.azure.azure_iot import AzureIoT, mainloop
from modules.azure.model_config_base import ModelConfigBase
from modules.azure.model_dev_base import ModelDevBase


class ModelDevG3M1Basic(ModelDevBase):
    def __init__(self, modelConfig):
        super().__init__(modelConfig)

    def model_id(self):
        return "dtmi:atmark_techno:Armadillo:IoT_GW_G3M1;2"

def main():
    asyncio.run(mainloop(ModelDevG3M1Basic, ModelConfigBase, "./config.json"))

if __name__ == '__main__':
    main()

#
# End of File
#
