import asyncio
from typing import Optional
from pyler.httplib.request import Request


class PriorityQueue(asyncio.PriorityQueue):

    def __init__(self, maxsize=0):
        super().__init__(maxsize=maxsize)

    async def get(self) -> Optional[Request]:
        fut = super().get()
        try:
            request = await asyncio.wait_for(
                fut,
                timeout=0.1
            )
            return request
        except asyncio.TimeoutError:
            return None
