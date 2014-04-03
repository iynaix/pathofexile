from scrapy.spider import Spider


class BasePoESpider(Spider):
    allowed_domains = ["pathofexile.gamepedia.com"]
