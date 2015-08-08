import re

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

    def parse(self, resp):
        quest_items = set()
        for quest_item in resp.css("table a::text").extract():
            quest_item = re.sub(r' \(.*\)', '', quest_item)
            if quest_item.endswith("/ko"):
                continue
            quest_items.add(quest_item)

        return {"QUEST_ITEMS": sorted(quest_items)}
