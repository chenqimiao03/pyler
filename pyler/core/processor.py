import asyncio
from typing import Union

from pyler.httplib.request import Request
from pyler.item import Item


class Processor:

    def __init__(self, crawler):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.crawler = crawler

    async def process(self):
        while not self.idle():
            result = await self.queue.get()
            if isinstance(result, Request):
                await self.crawler.engine.enqueue_request(result)
            else:
                assert isinstance(result, Item)
                await self.process_item(result)

    async def process_item(self, item):
        print(item)

    async def enqueue(self, output: Union[Request, Item]):
        await self.queue.put(output)
        await self.process()

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return self.queue.qsize()
