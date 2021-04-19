import asyncio
import threading

from modules.lib.report_queue import ReportQueue
from modules.lib.reporter_manager import ReporterManager

from modules.azure.report_repository import AzureReportRepository
from modules.azure.iot_pnp_client import IoTPnPClient
from modules.azure.model_config_base import ModelConfigBase
from modules.azure.model_dev_base import ModelDevBase


class AzureIoT:
    def __init__(self, loop):
        modelConfig = ModelConfigBase("./config.json")
        modelDev    = ModelDevBase(modelConfig)
        self._iotPnpClient = IoTPnPClient(modelConfig, modelDev)
        self._modelConfig  = modelConfig
        self._modelDev     = modelDev

    async def start(self):
        if not await self._iotPnpClient.auth_and_connect():
            printf("Error! Could not connect to the Azure IoT.")
            return False

        queue = ReportQueue()
        alaramQueue = ReportQueue()
        reportRepository = AzureReportRepository(
            queue, alaramQueue, self._iotPnpClient, asyncio.get_event_loop()
        )
        manager = ReporterManager(queue, alaramQueue)
        reporters = self._modelDev.make_reporters(self._modelConfig)
        for reporter in reporters:
            manager.listen_to(reporter)
        reportRepository.set_interval(self._modelConfig.send_interval())
        self.threads = []
        loopables = [reportRepository, manager]
        for loopable in loopables:
            thread = threading.Thread(target=loopable.start_loop)
            thread.start()
            self.threads.append(thread)
        self._manager = manager
        self._reportRepository = reportRepository
        return True

    def iot_pnp_client(self):
        return self._iotPnpClient

    def stop_threads(self):
        self._manager.request_stop()
        self._reportRepository.request_stop()
        for thread in self.threads:
            thread.join()

    async def shutdown(self):
        # stop threads
        self._manager.request_stop()
        self._reportRepository.request_stop()
        for thread in self.threads:
            thread.join()
        print("all threads are quitted, then shutdown the IoT client...")

        # shutdown the device client
        await self._iotPnpClient.shutdown()

def stdin_listener():
    while True:
        selection = input("Press Q to quit\n")
        if selection == 'Q' or selection == 'q':
            print("Quitting...")
            break

async def mainloop():
    loop = asyncio.get_event_loop()
    azure_iot = AzureIoT(loop)
    if not await azure_iot.start():
        return
    user_finished = loop.run_in_executor(None, stdin_listener)
    await user_finished
    await azure_iot.shutdown()

def main():
    asyncio.run(mainloop())

if __name__ == '__main__':
    main()
