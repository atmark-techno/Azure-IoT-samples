import threading

from collections import deque


class ReportQueue:
    def __init__(self):
        self.__queue = deque()
        self.__lock = threading.Lock()

    def __empty(self):
        return True if len(self.__queue) <= 0 else False

    def push(self, report):
        with self.__lock:
            self.__queue.append(report)

    def push_top(self, report):
        with self.__lock:
            self.__queue.appendleft(report)

    def push_top_multi(self, reports):
        with self.__lock:
            for report in reversed(reports):
                self.__queue.appendleft(report)

    def pop(self):
        with self.__lock:
            if self.__empty():
                return None

            return self.__queue.popleft()

    def pop_multi(self, count):
        with self.__lock:
            if count <= 0:
                return None

            if self.__empty():
                return None

            reports = []
            for i in range(count):
                reports.append(self.__queue.popleft())
                if self.__empty():
                    break

            return reports

    def size(self):
        with self.__lock:
            return len(self.__queue)

    def clear(self):
        with self.__lock:
            while not self.empty():
                self.__queue.clear()
