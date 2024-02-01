from typing import Optional

from pyler.httplib.request import Request
from pyler.utils.pqueue import PriorityQueue


class Scheduler:

    def __init__(self) -> None:
        self.pq: PriorityQueue = PriorityQueue()

    async def next_request(self) -> Optional[Request]:
        """获取下一个 Request 对象"""
        return await self.pq.get()

    async def enqueue_request(self, request: Request) -> None:
        """将 Request 对象放入优先级队列"""
        # todo 实现去重
        await self.pq.put(request)

    def idle(self) -> bool:
        """调度器是否处于空闲状态"""
        return len(self) == 0

    def __len__(self):
        return self.pq.qsize()
