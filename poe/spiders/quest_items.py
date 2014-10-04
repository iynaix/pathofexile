import re
from scrapy.selector import Selector

from . import BasePoESpider
from poe.items import TitleItem


class QuestItemSpider(BasePoESpider):
    """
    Spider that fetches quest items
    """
    name = "quest_items"
    start_urls = [
        "http://pathofexile.gamepedia.com/Category:Quest_items"
    ]

    def parse(self, response):
        sel = Selector(response)

        quest_items = set()
        for quest_item in sel.xpath("//table//li/a/text()").extract():
            quest_item = re.sub(r' \(.*\)', '', quest_item)
            if quest_item.endswith("/ko"):
                continue
            quest_items.add(quest_item)

        for quest_item in sorted(quest_items):
            item = TitleItem()
            item["title"] = quest_item
            yield item
