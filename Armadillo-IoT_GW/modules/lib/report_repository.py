import asyncio
from abc import ABC, abstractmethod
from time import time
from modules.const import Const


class ReportRepository(ABC):
    @abstractmethod
    async def process_report(self, report):
        pass

    async def process_reports(self, reports):
        return False

    @abstractmethod
    async def process_alarm(self, alarm):
        pass


    """
    Returns:
        True: done operation
        False: no operation
    """
    @abstractmethod
    async def dispatch_operation(self):
        pass

    def __init__(self, report_queue, alarm_queue):
        self._report_queue = report_queue
        self._alarm_queue = alarm_queue
        self._enable_posting_multi_measurement = False
        self._quit_requested = False

    def __sleep_interval(self, processing_time=0.0):
        if self.__interval_no_alarm <= processing_time:
            self.__interval_no_alarm = 0.0
            return 0.0
        else:
            self.__interval_no_alarm -= processing_time

        interval = self.__interval_no_alarm
        if interval > 1.0:
            interval = 1.0
            self.__interval_no_alarm -= 1.0
        else:
            self.__interval_no_alarm = 0.0

        return interval

    async def __async_loop(self, timeout=None):
        if timeout is not None:
            started_at = int(time())

        self.__interval_no_alarm = 0.0
        while not self._quit_requested:
            started_at_proc = int(time())
            if self._alarm_queue.size() > 0:
                while True:
                    alarm = self._alarm_queue.pop()
                    if alarm is None:
                        break
                    if not self.process_alarm(alarm):
                        self._alarm_queue.push_top(alarm)
            else:
                if self.__interval_no_alarm > 0.0:
                    end_at_proc = int(time())
                    interval = self.__sleep_interval(end_at_proc - started_at_proc)
                    if interval > 0.0:
                        await asyncio.sleep(interval)
                        continue

            while True:
                if not self.dispatch_operation():
                    break

            if self._enable_posting_multi_measurement:
                if self._report_queue.size() == 1:
                    report = self._report_queue.pop()
                    if not self.process_report(report):
                        self._report_queue.push_top(report)
                elif self._report_queue.size() > 1:
                    while True:
                        reports = self._report_queue.pop_multi(Const.BULK_REPORT_COUNT)
                        if reports is None:
                            break

                        if not self.process_reports(reports):
                            self._report_queue.push_top_multi(reports)
                            break
            else:
                while True:
                    report = self._report_queue.pop()
                    if report is None:
                        break

                    if not self.process_report(report):
                        self._report_queue.push_top(report)
                        break

            now = int(time())
            if timeout is not None and now - started_at >= timeout:
                break

            if now - started_at_proc < self.__interval:
                self.__interval_no_alarm = self.__interval - (now - started_at_proc)
            else:
                interval_current = now - started_at_proc - self.__interval
                while interval_current > self.__interval:
                    interval_current = interval_current - self.__interval
                self.__interval_no_alarm = interval_current

            interval = self.__sleep_interval()
            await asyncio.sleep(interval)

    def start_loop(self, timeout=None):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__async_loop(timeout))

    def request_stop(self):
        self._quit_requested = True

    def interval(self):
        return self.__interval

    def set_interval(self, interval):
        self.__interval = interval
