import asyncio
from abc import ABC, abstractmethod


class ActiveReporter(ABC):
    def __init__(self, report_queue, report_repository):
        self._quit_requested    = False
        self._report_queue      = report_queue
        self._report_repository = report_repository
        self._curr_state        = None

    def start_loop(self, timeout=None):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_loop(timeout))

    def request_stop(self):
        self._quit_requested = True

    async def _async_loop(self, timeout=None):
        if timeout is not None:
            started_at = int(time())

        self._before_loop()
        while not self._quit_requested:
            self._handle_state()
 
            if timeout is not None:
                now = int(time())
                if (now - started_at) >= timeout:
                    break
        self._after_loop()

    def _transit_state(self, next_state):
        self._do_transit_action(next_state)
        self._curr_state = next_state

    @abstractmethod
    def _before_loop(self):
        pass

    @abstractmethod
    def _after_loop(self):
        pass

    @abstractmethod
    def _handle_state(self):
        pass

    @abstractmethod
    def _do_transit_action(self, next_state):
        pass

#
# End of File
#

