from typing import List

from pyler.httplib.request import Request
from pyler.httplib.response import Response


class Spider:

    def __init__(self):
        if not hasattr(self, 'start_urls'):
            self.start_urls: List[str] = []
        self.crawler = None

    @classmethod
    def create_instance(cls, crawler) -> 'Spider':
        o = cls()
        o.crawler = crawler
        return o

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, self.parse)

    def parse(self, response: Response):
        raise NotImplementedError(
            f"{self.__class__.__name__}.parse callback is not defined"
        )

    def __str__(self):
        return self.__class__.__name__
