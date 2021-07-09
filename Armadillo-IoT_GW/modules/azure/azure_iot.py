import asyncio
import threading
import urllib.request

from modules.azure.iot_pnp_client import IoTPnPClient
from modules.azure.iot_pnp_client import ErrorCode


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
        self._doCheckConnection  = True

    async def start(self):
        result = await self._iot_pnp_client.auth_and_connect()
        
        if result == ErrorCode.AuthenticationFailed:
            print("Error! Could not connect to the Azure IoT.")
            return False
        elif result == ErrorCode.ConnectionFailed:
            while result != ErrorCode.Success:
                 await asyncio.sleep(10)
                 result = await self._iot_pnp_client.auth_and_connect()
        
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
        self._doCheckConnection = False
        self.stop_threads()
        print("all threads are quited, then shutdown the IoT client...")
        await self._iot_pnp_client.shutdown()

    async def check_network(self):
        while self._doCheckConnection:
            try:
                urllib.request.urlopen('https://www.atmark-techno.com/', timeout=1)
                if not self._iot_pnp_client.is_connected():
                    await self._iot_pnp_client.auth_and_connect()
            except urllib.error.URLError as err:
                await self._iot_pnp_client.disconnect()
                await self._iot_pnp_client.auth_and_connect()
            await asyncio.sleep(10)

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
    connection_task = loop.create_task(azure_iot.check_network())
    await user_finished
    await azure_iot.shutdown()

#
# End of File
#
