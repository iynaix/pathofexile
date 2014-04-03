from scrapy.item import Item, Field


class TitleItem(Item):
    """
    only single attribute for the given item, calling it 'title' for
    convenience
    """
    title = Field()


class GemItem(Item):
    name = Field()
    color = Field()
    support = Field()
    vaal = Field()
