from scrapy.selector import Selector

from . import BasePoESpider
from poe.items import CurrencyItem


class CurrencySpider(BasePoESpider):
    """
    Spider that fetches currency information
    """
    name = "currencies"
    start_urls = [
        "http://pathofexile.gamepedia.com/Currency"
    ]

    def parse(self, response):
        sel = Selector(response)
        tables = sel.xpath("//table[contains(@class, 'wikitable')]")

        for row in tables[0].xpath(".//tr"):
            try:
                item = CurrencyItem()
                try:
                    cells = row.xpath(".//td")
                    item["title"] = \
                        cells[0].xpath("a/text()").extract()[0].strip()
                    item["description"] = \
                        cells[2].xpath("span/text()").extract()[0].strip()
                    yield item
                except ValueError:
                    continue
            except IndexError:
                pass
