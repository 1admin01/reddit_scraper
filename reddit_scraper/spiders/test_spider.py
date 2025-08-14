import scrapy

class TestSpider(scrapy.Spider):
    name = "test_spider"
    start_urls = ["https://www.reddit.com"]

    def parse(self, response):
        yield {"title": response.xpath("//title/text()").get()}

