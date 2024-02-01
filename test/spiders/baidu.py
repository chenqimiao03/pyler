from pyler.spiders import Spider


class BaiduSpider(Spider):

    start_urls = ['https://www.baidu.com123']
    custom_settings = {'CONCURRENCY': 8}

    def parse(self, response):
        print('parse', response.text)
