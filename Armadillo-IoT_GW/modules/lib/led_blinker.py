
import asyncio
from enum import IntEnum

from modules.lib.agent_utils import run_on_bash


class BlinkPattern(IntEnum):
     NORMAL_SLOW = 1,  # -----__________
     NORMAL_FAST = 2,  # --__
     SUCESS      = 3,  # __--_--_--_____
     ERROR       = 4,  # -_-_-_-_-___________
     STOPPED     = 5

on_off_patterns = [
    [(True, 0.5), (False, 1.0)],
    [(True, 0.2), (False, 0.2)],
    [
        (False, 0.2),
        (True, 0.2), (False, 0.1),
        (True, 0.2), (False, 0.1),
        (True, 0.2), (False, 0.5)
    ],
    [
        (True, 0.1), (False, 0.1),
        (True, 0.1), (False, 0.1),
        (True, 0.1), (False, 0.1),
        (True, 0.1), (False, 0.1),
        (True, 0.1), (False, 1.1)
    ],
    [(False, 1.0)]
]

class LedBlinker:
    def __init__(self, target, other_targets=None):
        self._targets = [target]
        if other_targets is not None:
            self._targets.extend(other_targets)
        self._curr_state = BlinkPattern.STOPPED
        self._next_state = self._curr_state
        self._quit_requested = False

    async def run(self):
        while not self._quit_requested:
            while self._next_state == self._curr_state:
                pattern = on_off_patterns[int(self._curr_state) - 1]
                await self._exec_pattern(pattern)
                if (self._curr_state == BlinkPattern.SUCESS):
                    self._next_state = BlinkPattern.NORMAL_SLOW
            self._curr_state = self._next_state

    def start_blink(self):
        self._next_state = BlinkPattern.NORMAL_SLOW

    def request_stop(self):
        self._quit_requested = True

    def change_state(self, next_state):
        self._next_state = next_state

    async def _exec_pattern(self, pattern):
        for (on, duration) in pattern:
            c = '1' if on else '0'
            print(c, end="", flush=True)
            await asyncio.sleep(duration)
            if self._quit_requested or (self._next_state != self._curr_state):
                return

#
# End of File
#
