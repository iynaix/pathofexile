from scrapy.selector import Selector

from . import BasePoESpider
from poe.items import ItemStatItem


class BaseStatItemSpider(BasePoESpider):
    """
    Spider that fetches ItemStatItem

    Gets the title above the table as well as the text of the first cells of
    each row of each table and returns the item
    """
    #type of item used to instantiate
    item_class = ItemStatItem
    #dict of extra keys and values to be set for each yielded item
    item_kwargs = {}
    #is the text to be extracted in the table cell a link?
    is_link = True
    #tables that will be parsed, specified as a list of args to be passed to
    #slice
    table_slice = []
    #there are items for Str, Dex, Int combination
    has_triple_stat_item = False

    def parse(self, response):
        sel = Selector(response)
        tables = sel.xpath("//table[contains(@class, 'wikitable')]")

        if self.table_slice:
            tables = tables[slice(*self.table_slice)]

        stat_types = ["Str", "Dex", "Int", "Str, Dex", "Str, Int", "Dex, Int"]
        if self.has_triple_stat_item:
            stat_types.append("Str, Dex, Int")
        for idx, table in enumerate(tables):
            for row in table.xpath(".//tr"):
                try:
                    item = self.item_class()
                    item.update(self.item_kwargs)
                    if self.is_link:
                        row_xpath = ".//td//a/text()"
                    else:
                        row_xpath = ".//td/text()"
                    try:
                        item["stat_type"] = stat_types[idx]
                        item["title"] = self.process_title(
                            row.xpath(row_xpath).extract()[0]
                        )
                        yield item
                    except ValueError:
                        continue
                except IndexError:
                    pass

    def process_title(self, title):
        """
        hook to allow processing of the title before saving, raise ValueError
        if the title is invalid
        """
        return title.strip()


class GloveSpider(BaseStatItemSpider):
    name = "gloves"
    start_urls = [
        "http://pathofexile.gamepedia.com/Gloves"
    ]


class BootSpider(BaseStatItemSpider):
    name = "boots"
    start_urls = [
        "http://pathofexile.gamepedia.com/Boots"
    ]


#TODO: helms and shields

class ShieldSpider(BaseStatItemSpider):
    name = "shields"
    start_urls = [
        "http://pathofexile.gamepedia.com/Shields"
    ]


class HelmSpider(BaseStatItemSpider):
    name = "helms"
    start_urls = [
        "http://pathofexile.gamepedia.com/Helmets"
    ]


class ArmorSpider(BaseStatItemSpider):
    name = "armors"
    start_urls = [
        "http://pathofexile.gamepedia.com/Body_Armour"
    ]
    has_triple_stat_item = True
