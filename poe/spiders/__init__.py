from scrapy.spiders import Spider
from scrapy.selector import Selector

from poe.items import TitleItem, ItemTypeItem, ItemSubtypeItem


class BasePoESpider(Spider):
    allowed_domains = ["pathofexile.gamepedia.com"]


class BaseTitleSpider(BasePoESpider):
    """
    Spider that fetches TitleItems

    Gets the text of the first cells of each row of each table and returns the
    item
    """
    # type of item used to instantiate
    item_class = TitleItem
    # dict of extra keys and values to be set for each yielded item
    item_kwargs = {}
    # is the text to be extracted in the table cell a link?
    is_link = True
    # tables that will be parsed, specified as a list of args to be passed to
    # slice
    table_slice = []

    def parse(self, response):
        sel = Selector(response)
        tables = sel.xpath("//table[contains(@class, 'wikitable')]")
        if self.table_slice:
            tables = tables[slice(*self.table_slice)]

        for table_idx, table in enumerate(tables):
            for row in table.xpath(".//tr"):
                try:
                    item = self.item_class()
                    item.update(self.get_item_kwargs(table_idx))
                    if self.is_link:
                        row_xpath = ".//td//a/text()"
                    else:
                        row_xpath = ".//td/text()"
                    try:
                        item["title"] = self.process_title(
                                            row.xpath(row_xpath).extract()[0])
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

    def get_item_kwargs(self, table_idx):
        """
        hook to allow processing of extra item kwargs before saving
        """
        return self.item_kwargs


class UniqueSpider(BaseTitleSpider):
    name = "uniques"
    start_urls = [
        "http://pathofexile.gamepedia.com/List_of_unique_items"
    ]


class QuiverSpider(BaseTitleSpider):
    name = "quivers"
    start_urls = [
        "http://pathofexile.gamepedia.com/Quiver"
    ]
    item_class = ItemTypeItem
    item_kwargs = {"type": "Quiver"}


class BeltSpider(BaseTitleSpider):
    name = "belts"
    start_urls = [
        "http://pathofexile.gamepedia.com/Belt"
    ]
    item_class = ItemTypeItem
    item_kwargs = {"type": "Belt"}


class WandSpider(BaseTitleSpider):
    name = "wands"
    start_urls = [
        "http://pathofexile.gamepedia.com/Wand"
    ]
    item_class = ItemTypeItem
    item_kwargs = {"type": "Wand"}


class StaveSpider(BaseTitleSpider):
    name = "staves"
    start_urls = [
        "http://pathofexile.gamepedia.com/Staff"
    ]
    item_class = ItemTypeItem
    item_kwargs = {"type": "Stave"}


class DaggerSpider(BaseTitleSpider):
    name = "daggers"
    start_urls = [
        "http://pathofexile.gamepedia.com/Dagger"
    ]
    item_class = ItemTypeItem
    item_kwargs = {"type": "Dagger"}
    table_slice = [1]


class ClawSpider(BaseTitleSpider):
    name = "claws"
    start_urls = [
        "http://pathofexile.gamepedia.com/Claw"
    ]
    item_class = ItemTypeItem
    item_kwargs = {"type": "Claw"}
    table_slice = [2]


class BowSpider(BaseTitleSpider):
    name = "bows"
    start_urls = [
        "http://pathofexile.gamepedia.com/Bow"
    ]
    item_class = ItemTypeItem
    item_kwargs = {"type": "Bow"}
    table_slice = [1]


class PrefixSpider(BaseTitleSpider):
    name = "prefixes"
    start_urls = [
        "http://pathofexile.gamepedia.com/Item_Affix"
    ]
    is_link = False

    def process_title(self, title):
        title = super(PrefixSpider, self).process_title(title)
        if title.startswith("of "):
            raise ValueError
        return title


class SuffixSpider(BaseTitleSpider):
    name = "suffixes"
    start_urls = [
        "http://pathofexile.gamepedia.com/Item_Affix"
    ]
    is_link = False

    def process_title(self, title):
        title = super(SuffixSpider, self).process_title(title)
        if not title.startswith("of "):
            raise ValueError
        return title


class FlaskSizeSpider(BaseTitleSpider):
    name = "flask_sizes"
    start_urls = [
        "http://pathofexile.gamepedia.com/Flask",
    ]

    def process_title(self, title):
        title = super(FlaskSizeSpider, self).process_title(title)
        if not title.endswith(" Life Flask"):
            raise ValueError
        return title.rsplit(' ', 2)[0]


class MiscFlaskSpider(BaseTitleSpider):
    name = "misc_flasks"
    start_urls = [
        "http://pathofexile.gamepedia.com/Flask",
    ]

    def process_title(self, title):
        title = super(MiscFlaskSpider, self).process_title(title)
        if not title.endswith("Flask"):
            raise ValueError
        if title.endswith((" Life Flask", " Mana Flask", " Hybrid Flask")):
            raise ValueError
        return title.rsplit(' ', 1)[0]


class AxeSpider(BaseTitleSpider):
    name = "axes"
    start_urls = [
        "http://pathofexile.gamepedia.com/Axe"
    ]
    item_class = ItemSubtypeItem
    table_slice = [2]

    def get_item_kwargs(self, table_idx):
        """
        hook to allow processing of extra item kwargs before saving
        """
        if table_idx == 0:
            return dict(type="Axe", subtype="One Handed Axe")
        elif table_idx == 1:
            return dict(type="Axe", subtype="Two Handed Axe")


class MaceSpider(BaseTitleSpider):
    name = "maces"
    start_urls = [
        "http://pathofexile.gamepedia.com/Mace"
    ]
    item_class = ItemSubtypeItem
    table_slice = [3]

    def get_item_kwargs(self, table_idx):
        """
        hook to allow processing of extra item kwargs before saving
        """
        if table_idx == 0:
            return dict(type="Mace", subtype="Mace")
        elif table_idx == 1:
            return dict(type="Mace", subtype="Sceptre")
        elif table_idx == 2:
            return dict(type="Mace", subtype="Maul")


class SwordSpider(BaseTitleSpider):
    name = "swords"
    start_urls = [
        "http://pathofexile.gamepedia.com/Sword"
    ]
    item_class = ItemSubtypeItem
    table_slice = [3]

    def get_item_kwargs(self, table_idx):
        """
        hook to allow processing of extra item kwargs before saving
        """
        if table_idx == 0:
            return dict(type="Sword", subtype="One Handed Sword")
        elif table_idx == 1:
            return dict(type="Sword", subtype="Rapier")
        elif table_idx == 2:
            return dict(type="Sword", subtype="Two Handed Sword")
