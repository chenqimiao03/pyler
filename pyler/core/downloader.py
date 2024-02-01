from contextlib import asynccontextmanager
from typing import Final, Set, Optional
from abc import abstractmethod, ABCMeta


from aiohttp import ClientSession, TCPConnector, BaseConnector, ClientTimeout, ClientResponse, TraceConfig
import httpx

from pyler.httplib.request import Request
from pyler.httplib.response import Response
from pyler.utils.logger import get_logger


class ActiveRequests:

    def __init__(self):
        self._active: Final[Set] = set()

    def add(self, request):
        self._active.add(request)

    def remove(self, request):
        self._active.remove(request)

    @asynccontextmanager
    async def __call__(self, request):
        try:
            yield self.add(request)
        finally:
            self.remove(request)

    def __len__(self):
        return len(self._active)


class DownloaderMeta(ABCMeta):

    def __subclasscheck__(self, subclass):
        methods = ("fetch", "download", "create_instance", "close", "idle")
        return all(
            hasattr(subclass, method) and callable(getattr(subclass, method, None)) for method in methods
        )


class Downloader(metaclass=DownloaderMeta):

    def __init__(self, crawler):
        self.crawler = crawler
        self._active = ActiveRequests()
        self.logger = get_logger(self.__class__.__name__, self.crawler.settings.get("LOG_LEVEL"))

    @classmethod
    def create_instance(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def open(self):
        self.logger.info(
            f"{self.crawler.spider} using downloader: {type(self).__name__} "
            f"concurrency: {self.crawler.settings.getint('CONCURRENCY')}"
        )

    async def close(self):
        pass

    async def fetch(self, request):
        async with self._active(request):
            response = await self.download(request)
            return response

    @abstractmethod
    async def download(self, request: Request) -> Optional[Response]:
        pass

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self) -> int:
        return len(self._active)


class AIOHTTPDownloader(Downloader):

    def __init__(self, crawler):
        super().__init__(crawler)
        self.session: Optional[ClientSession] = None
        self.connector: Optional[BaseConnector] = None
        self._verify_ssl: Optional[bool] = None
        self._timeout: Optional[ClientTimeout] = None
        self.methods = {
            "get": self._get,
            "post": self._post
        }
        self._new_session: Optional[bool] = None
        self.trace_config: Optional[TraceConfig] = None

    def open(self):
        super().open()
        self._new_session = self.crawler.settings.getbool("NEW_SESSION")
        self._verify_ssl = self.crawler.settings.getbool("VERIFY_SSL")
        self._timeout = ClientTimeout(total=self.crawler.settings.getint("DOWNLOAD_TIMEOUT"))
        self.trace_config = TraceConfig()
        self.trace_config.on_request_start.append(self.request_start)
        if not self._new_session:
            self.connector = TCPConnector(verify_ssl=self._verify_ssl)
            self.session = ClientSession(connector=self.connector, timeout=self._timeout,
                                         trace_configs=[self.trace_config])

    async def download(self, request) -> Optional[Response]:
        try:
            if self._new_session:
                connector = TCPConnector(verify_ssl=self._verify_ssl)
                async with ClientSession(connector=connector, timeout=self._timeout,
                                         trace_configs=[self.trace_config]) as session:
                    response = await self.send(session, request)
                    body = await response.content.read()
            else:
                response = await self.send(self.session, request)
                body = await response.content.read()
        except Exception as exc:
            self.logger.error(f"download error: {exc}")
            return None
        return self.make(request, response, body)

    @staticmethod
    def make(request, response, body):
        return Response(
            url=response.url,
            body=body,
            request=request,
            headers=dict(response.headers),
            status=response.status
        )

    async def send(self, session, request) -> ClientResponse:
        response = await self.methods[request.method.lower()](session, request)
        return response

    @staticmethod
    async def _get(session, request) -> ClientResponse:
        response = await session.get(
            request.url, headers=request.headers, cookies=request.cookies, proxy=request.proxy
        )
        return response

    @staticmethod
    async def _post(session, request) -> ClientResponse:
        response = await session.get(
            request.url, data=request.body, headers=request.headers, cookies=request.cookies, proxy=request.proxy
        )
        return response

    async def request_start(self, _session, _trace_config_ctx, params):
        self.logger.debug(f"request downloading: {params.url}, method: {params.method}")

    async def close(self):
        if self.connector:
            await self.connector.close()
        if self.session:
            await self.session.close()


class HTTPXDownloader(Downloader):

    def __init__(self, crawler):
        super().__init__(crawler)
        self._client: Optional[httpx.AsyncClient] = None
        self._timeout: Optional[httpx.Timeout] = None

    def open(self):
        super().open()
        self._timeout = httpx.Timeout(timeout=self.crawler.settings.getint("DOWNLOAD_TIMEOUT"))

    async def download(self, request):
        try:
            proxy = request.proxy
            async with httpx.AsyncClient(timeout=self._timeout, proxies=proxy) as client:
                self.logger.debug(f"request downloading: {request.url}, method: {request.method}")
                response = await client.request(
                    request.method,
                    request.url,
                    headers=request.headers,
                    cookies=request.cookies,
                    data=request.body
                )
                body = await response.aread()
        except Exception as exc:
            self.logger.error(f"download error: {exc}")
            return None
        return self.make(request, response, body)

    @staticmethod
    def make(request, response, body):
        return Response(
            url=response.url,
            body=body,
            request=request,
            headers=dict(response.headers),
            status=response.status_code
        )
