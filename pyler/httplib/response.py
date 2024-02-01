import json
import re
from typing import Dict
from urllib.parse import urljoin as _urljoin

from parsel import Selector

from pyler.exceptions import DecodeFail
from pyler.httplib.request import Request


class Response:

    def __init__(
            self,
            url: str,
            *,
            request: Request,
            headers: Dict,
            body: bytes = b"",
            status: int = 200
    ):
        self.url = url
        self.request = request
        self.headers = headers
        self.body = body
        self.status = status
        self.encoding = self.request.encoding
        self._text_cache = None
        self._Selector = None

    def json(self):
        return json.loads(self.text)

    @property
    def text(self):
        if self._text_cache is not None:
            return self._text_cache
        try:
            self._text_cache = self.body.decode(self.encoding)
        except UnicodeDecodeError:
            _encoding_regexp = re.compile(r"charset=[\w-]+", flags=re.I)
            content_type = self.headers.get("Content-Type", "") or self.headers.get("content-type", "")
            _encoding = _encoding_regexp.search(content_type)
            if _encoding:
                _encoding = _encoding.group(1)
                try:
                    self._text_cache = self.body.decode(_encoding)
                except UnicodeDecodeError as exc:
                    raise UnicodeDecodeError(
                        exc.encoding,
                        exc.object,
                        exc.start,
                        exc.end,
                        f"{self.request}"
                    )
            else:
                raise DecodeFail(f"{self.request} {self.request.encoding} error.")
        return self._text_cache

    def urljoin(self, url):
        return _urljoin(self.url, url)

    def xpath(self, xpath_exp):
        if self._Selector is None:
            self._Selector = Selector(self.text)
        return self._Selector.xpath(xpath_exp)

    def __str__(self):
        return f"<{self.request.method} {self.url} {self.status}>"

    __repr__ = __str__

    @property
    def meta(self):
        return self.request.meta

