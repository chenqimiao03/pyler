import asyncio

from pyler.crawler import CrawlerProcess
from pyler.utils import get_settings
from test.spiders.httpbin import HttpbinSpider


async def run():
    settings = get_settings("settings")
    process = CrawlerProcess(settings)
    await process.crawl(HttpbinSpider)
    await process.start()


if __name__ == '__main__':
    asyncio.run(run())
