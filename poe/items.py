from scrapy.item import Item, Field


class BaseItem(Item):
    def __setattr__(self, name, val):
        if isinstance(val, basestring):
            val = val.strip()
        super(BaseItem, self).__setattr__(name, val)


class TitleItem(BaseItem):
    """
    only single attribute for the given item, calling it 'title' for
    convenience
    """
    title = Field()


class GemItem(BaseItem):
    title = Field()
    color = Field()
    support = Field()
    vaal = Field()


class CurrencyItem(BaseItem):
    title = Field()
    description = Field()


class ItemTypeItem(BaseItem):
    """
    crappy name, but a generic representation of a generic item type, e.g.
    {"title": "Leather Belt", "type": "Belt"}
    """
    title = Field()
    type_ = Field()


class ItemSubtypeItem(BaseItem):
    """
    crappy name, but a generic representation of a generic item type, e.g.
    {"title": "Leather Belt", "type": "Belt"}
    """
    title = Field()
    type_ = Field()
    subtype = Field()


class ItemStatItem(BaseItem):
    """
    Item with a stat type, e.g. {"title": "Iron Gauntlets", "stat_type": "Str"}
    """
    title = Field()
    stat_type = Field()


class MainItem(BaseItem):
    name = Field()
    type_ = Field()
    x = Field()
    y = Field()
    w = Field()
    h = Field()
    rarity = Field()
    num_sockets = Field()
    socket_str = Field()
    is_identified = Field()
    is_corrupted = Field()
    char_location = Field()
    full_text = Field()
    league = Field()
    mods = Field()
    requirements = Field()
    properties = Field()
    socketed_items = Field()
    location = Field()
