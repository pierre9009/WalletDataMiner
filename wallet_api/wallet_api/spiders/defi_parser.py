import scrapy


class DefiParserSpider(scrapy.Spider):
    name = "defi_parser"
    allowed_domains = ["s"]
    start_urls = ["https://s"]

    def parse(self, response):
        pass
