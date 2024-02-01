from pyler.spiders import Spider


class HttpbinSpider(Spider):

    start_urls = ['http://www.httpbin.org/get']

    def parse(self, response):
        print('parse', response.text)
        print('parse', response.json())




