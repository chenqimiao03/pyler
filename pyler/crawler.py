import asyncio
from typing import Type, Final, Set, Optional

from pyler.core.engine import Engine
from pyler.spiders import Spider
from pyler.settings import Settings
from pyler.utils import update_settings


class Crawler:

    def __init__(self, spidercls, settings): # noqa
        self.spidercls = spidercls # noqa
        self.spider: Optional[Spider] = None
        self.engine: Optional[Engine] = None
        self.settings: Settings = settings.copy()

    async def crawl(self):
        self.spider = self._create_spider()
        self.engine = self._create_engine()
        await self.engine.start(self.spider)

    def _create_spider(self) -> Spider:
        spider = self.spidercls.create_instance(self)
        self.update_settings(spider=spider)
        return spider

    def _create_engine(self) -> Engine:
        engine = Engine(self)
        return engine

    def update_settings(self, spider):
        update_settings(spider=spider, settings=self.settings)


class CrawlerProcess:

    def __init__(self, settings=None):
        self.crawlers: Final[Set] = set()
        self._active: Final[Set] = set()
        self.settings = settings

    async def crawl(self, spider: Type[Spider]):
        crawler: Crawler = self._create_crawler(spider)
        self.crawlers.add(crawler)
        task = await self._crawl(crawler)
        self._active.add(task)

    @staticmethod
    async def _crawl(crawler):
        return asyncio.create_task(crawler.crawl())

    async def start(self):
        await asyncio.gather(*self._active)

    def _create_crawler(self, spidercls) -> Crawler: # noqa
        if isinstance(spidercls, str):
            raise TypeError(f'{type(self)}.crawl args: String is not supported')
        return Crawler(spidercls, self.settings) # noqa
