from scrapy.spider import Spider
from scrapy.selector import Selector

from . import BasePoESpider
from poe.items import GemItem


class GemSpider(BasePoESpider):
    name = "gems"
    start_urls = [
        "http://pathofexile.gamepedia.com/Skills"
    ]

    def parse(self, response):
        sel = Selector(response)
        tables = sel.xpath("//table[contains(@class, 'wikitable')]")

        #we discard the first table on sockets
        COLORS = "RGBW"
        vaal_tables = tables[1:1 + 3]  # 3 tables
        active_tables = tables[1 + 3:1 + 3 + 4]  # 4 tables, 1 for colorless
        support_tables = tables[1 + 3 + 4:1 + 3 + 4 + 3]   # 3 tables

        items = []
        for color_idx, tbl in enumerate(vaal_tables):
            items.extend(self.parse_table(tbl, color=COLORS[color_idx],
                                          vaal=True, support=False))

        for color_idx, tbl in enumerate(active_tables):
            items.extend(self.parse_table(tbl, color=COLORS[color_idx],
                                          vaal=False, support=False))

        for color_idx, tbl in enumerate(support_tables):
            items.extend(self.parse_table(tbl, color=COLORS[color_idx],
                                          vaal=False, support=True))
        return items

    def parse_table(self, table, **kwargs):
        gems = table.xpath(
                        ".//tr//span[contains(@class, 'gem-link')]/a/text()")
        items = []
        for gem in gems.extract():
            item = GemItem()
            item["name"] = gem
            item.update(**kwargs)
            items.append(item)
        return items
