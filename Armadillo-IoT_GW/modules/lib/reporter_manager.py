import asyncio
from queue import PriorityQueue
from queue import Queue
from time import time


class ReporterManager:
    def __append(self, reporter):
        index = len(self.__reporters)
        self.__reporters.append(reporter)
        return index

    def listen_to(self, reporter):
        index = self.__append(reporter)
        report_at = int(time()) + reporter.interval()
        self.__put(report_at, index)

    def add_nop(self, reporter):
        index = self.__append(reporter)
        self.__put_nop(index)

    def __reporter(self, index):
        return self.__reporters[index]

    def __put(self, report_at, index):
        self.__reporter_queue.put((report_at, index))

    def __get(self):
        return self.__reporter_queue.get()

    def __empty(self):
        return self.__reporter_queue.empty()

    def __put_nop(self, index):
        self.__reporter_nop_queue.put_nowait(index)

    def __get_nop(self):
        return self.__reporter_nop_queue.get_nowait()

    def __empty_nop(self):
        return self.__reporter_nop_queue.empty()

    def __size_nop(self):
        return self.__reporter_nop_queue.qsize()

    def __check_nop_queue(self):
        if self.__empty_nop():
            return

        nop_size = self.__size_nop()
        for i in range(nop_size):
            index = self.__get_nop()
            reporter = self.__reporter(index)
            if reporter.interval() > 0:
                report_at = int(time()) + reporter.interval()
                self.__put(report_at, index)
            else:
                self.__put_nop(index)

    async def __async_loop(self, timeout=None):
        if timeout is not None:
            started_at = int(time())

        self.__curr_task = asyncio.current_task()
        while not self.__quit_requested:
            self.__check_nop_queue()
            if self.__empty():
                await asyncio.sleep(Const.SLEEP_NO_REPORT_SEC)
                continue

            now = int(time())
            (report_at, index) = self.__get()
            reporter = self.__reporter(index)

            if (timeout is not None
                    and max(now, report_at) - started_at >= timeout):
                break

            if reporter.interval() <= 0:
                self.__put_nop(index)
                if self.__empty():
                    await asyncio.sleep(Const.SLEEP_NO_REPORT_SEC)
                continue

            if report_at >= now:
                await asyncio.sleep(report_at - now)
                [report, alarm] = reporter.report()
                self.__report_queue.push(report)
                if alarm is not None:
                    self.__alarm_queue.push(alarm)

            self.__put(report_at + reporter.interval(), index)

    def start_loop(self, timeout=None):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.__async_loop(timeout))
        except:
            pass

    def request_stop(self):
        self.__quit_requested = True
        self.__curr_task.cancel()

    def __init__(self, report_queue, alarm_queue):
        self.__reporter_queue = PriorityQueue()
        self.__reporter_nop_queue = Queue()
        self.__report_queue = report_queue
        self.__reporters = []
        self.__alarm_queue = alarm_queue
        self.__quit_requested = False
