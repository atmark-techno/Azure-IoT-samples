import asyncio
import threading

from modules.azure.iot_pnp_client import IoTPnPClient


class AzureIoT:
    def __init__(self, loop, dev_cls, config_cls, config_path):
        model_config = config_cls()
        if not model_config.load(config_path):
            return
        model_device   = dev_cls(model_config)
        iot_pnp_client = IoTPnPClient(model_config, model_device)
        model_device.setup_reporters(model_config, iot_pnp_client, loop)
        self._model_device   = model_device
        self._iot_pnp_client = iot_pnp_client

    async def start(self):
        if not await self._iot_pnp_client.auth_and_connect():
            print("Error! Could not connect to the Azure IoT.")
            return False
        self._threads = []
        for loopable in self._model_device.loopables():
            thread = threading.Thread(target=loopable.start_loop)
            thread.start()
            self._threads.append(thread)
        return True

    def stop_threads(self):
        for loopable in self._model_device.loopables():
            loopable.request_stop()
        for thread in self._threads:
            thread.join()

    async def shutdown(self):
        self.stop_threads()
        print("all threads are quited, then shutdown the IoT client...")

        await self._iot_pnp_client.shutdown()

def stdin_listener():
    while True:
        selection = input("Press Q to quit\n")
        if (selection == 'Q' or selection == 'q'):
            print("Quitting...")
            break

async def mainloop(dev_cls, config_cls, config_path):
    loop = asyncio.get_event_loop()
    azure_iot = AzureIoT(loop, dev_cls, config_cls, config_path)
    if not await azure_iot.start():
        return
    user_finished = loop.run_in_executor(None, stdin_listener)
    await user_finished
    await azure_iot.shutdown()

#
# End of File
#
