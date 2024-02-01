from typing import Callable, Optional


class Request:

    def __init__(
            self,
            url: str,
            callback: Optional[Callable] = None,
            method: str = 'GET',
            headers: Optional[dict] = None,
            body: Optional[dict] = None,
            cookies: Optional[dict] = None,
            encoding: str = 'utf-8',
            priority: int = 0,
            proxy: Optional[dict] = None,
            meta: Optional[dict] = None
    ):
        self.url = url
        self.callback = callback
        self.method = method
        self.headers = headers
        self.body = body
        self.cookies = cookies
        self.encoding = encoding
        self.priority = priority
        self.proxy = proxy
        self._meta = meta if meta is not None else {}

    def __lt__(self, other):
        return self.priority < other.priority

    def __repr__(self) -> str:
        return f"<{self.method} {self.url}>"

    @property
    def meta(self) -> dict:
        return self._meta

    __str__ = __repr__

