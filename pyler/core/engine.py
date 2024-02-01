import asyncio
from typing import Callable, Optional
from inspect import iscoroutine, isgenerator, isasyncgen

from pyler.core.downloader import Downloader
from pyler.core.scheduler import Scheduler
from pyler.core.processor import Processor
from pyler.spiders import Spider
from pyler.httplib.request import Request
from pyler.taskmanager import TaskManager
from pyler.item import Item
from pyler.utils.logger import get_logger
from pyler.utils import load_instance


class Engine:

    def __init__(self, crawler):
        self.crawler = crawler
        self.settings = self.crawler.settings
        self.logger = get_logger(self.__class__.__name__)
        self.running: bool = False
        self.spider: Optional[Spider] = None
        self.downloader: Optional[Downloader] = None
        self.processor: Optional[Processor] = None
        self.scheduler: Optional[Scheduler] = None
        self.task_manager: Optional[TaskManager] = None

    async def start(self, spider: Spider):
        self.running = True
        self.logger.info(f"Starting spider {spider}")
        self.spider = spider
        downloader_cls = self._get_downloader()
        self.downloader = downloader_cls.create_instance(self.crawler)
        if hasattr(self.downloader, "open"):
            self.downloader.open()
        self.scheduler = Scheduler()
        self.processor = Processor(self.crawler)
        self.task_manager = TaskManager(maxconcurrency=self.settings.getint('CONCURRENCY'))
        await self._open_spider()

    def _get_downloader(self):
        downloader_cls = load_instance(self.settings.get('DOWNLOADER'))
        if not issubclass(downloader_cls, Downloader):
            raise TypeError(f"the downloader {downloader_cls.__name__} not fully implemented required interface")
        return downloader_cls

    async def _open_spider(self):
        task = asyncio.create_task(self.crawl())
        # 这里可以做其他的事情
        await task

    async def crawl(self):
        start_requests = iter(self.spider.start_requests())
        while self.running:
            if (request := await self.next_request()) is not None:
                await self._crawl(request)
            else:
                try:
                    start_request = next(start_requests)
                except StopIteration:
                    start_requests = None
                except Exception as e:
                    if await self._close_spider():
                        self.running = False
                    if start_requests is not None:
                        self.logger.error(f"start_requests is not empty, error: {e}")
                else:
                    await self.enqueue_request(start_request)
        if not self.running:
            await self.close()

    async def _crawl(self, request):
        async def create_task():
            outputs = await self.fetch(request)
            if outputs is not None:
                await self._handle_spider_output(outputs)
        # 使用 semaphore 实现并发
        await self.task_manager.semaphore.acquire()
        self.task_manager.create_task(create_task())

    async def _handle_spider_output(self, outputs): # noqa
        async for output in outputs:
            if isinstance(output, (Request, Item)):
                await self.processor.enqueue(output)
            else:
                raise TypeError(f"{type(self.spider)} must return Request or Item")

    async def enqueue_request(self, request: Request):
        await self.scheduler.enqueue_request(request)

    async def next_request(self):
        request = await self.scheduler.next_request()
        return request

    async def fetch(self, request):

        async def _transform(_outputs):
            if isgenerator(_outputs):
                for output in _outputs:
                    yield output
            elif isasyncgen(_outputs):
                async for output in _outputs:
                    yield output
            else:
                raise TypeError(f"callback return value must be `generator` or `asyncgen` but got {type(_outputs)}")

        async def _success(_response):
            callback: Callable = request.callback or self.spider.parse
            if _outputs := callback(_response):
                if iscoroutine(_outputs):
                    await _outputs
                else:
                    return _transform(_outputs)

        response = await self.downloader.fetch(request)
        if response is None:
            return None
        outputs = await _success(response)
        return outputs

    async def _close_spider(self) -> bool:
        if all((self.scheduler.idle(), self.downloader.idle(),
                self.task_manager.all_done(), self.processor.idle(), self.spider)):
            return True
        return False

    async def close(self):
        await self.downloader.close()
