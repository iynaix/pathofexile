from scrapy.selector import Selector

from . import BasePoESpider
from poe.items import TitleItem


class UniqueSpider(BasePoESpider):
    name = "uniques"
    start_urls = [
        "http://pathofexile.gamepedia.com/List_of_unique_items"
    ]

    def parse(self, response):
        sel = Selector(response)
        rows = sel.xpath("//table[contains(@class, 'wikitable')]//tr")
        for row in rows:
            try:
                item = TitleItem()
                item["title"] = row.xpath(".//a/text()").extract()[0]
                yield item
            except IndexError:
                pass
