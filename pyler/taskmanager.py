import asyncio
from typing import Coroutine, Final, Set


class TaskManager:

    def __init__(
            self,
            maxconcurrency: int = 16
    ):
        self._tasks: Final[Set] = set()
        self.semaphore: asyncio.Semaphore = asyncio.Semaphore(maxconcurrency)

    def create_task(self, coroutine: Coroutine) -> asyncio.Task:
        def done_callback(_fut: asyncio.Task) -> None:
            self._tasks.remove(task)
            self.semaphore.release()

        task = asyncio.create_task(coroutine)
        self._tasks.add(task)
        task.add_done_callback(done_callback)
        return task

    def all_done(self) -> bool:
        return len(self._tasks) == 0
