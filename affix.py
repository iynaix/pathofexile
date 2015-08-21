import json
import re
import click

from app import db
from models import Item, Modifier, Location, in_page_group
# from sqlalchemy import false


class Affix(object):
    def __init__(self, *args):
        """
        initialize using the arrays taken from the affixes from the output of
        the item_data scraper
        """
        self.name = args[0]
        self.lvl = int(args[1])

        # variable length depending on the number of mods
        rest = args[2:]
        self.stat = rest[:(len(args) / 2)]
        self.value = rest[(len(args) / 2):]


data = {}
for l in open("item_data.json"):
    data.update(json.loads(l))

from pprint import pprint

AFFIXES = []
for k in ("Prefixes", "Suffixes"):
    for affixes in data[k].values():
        AFFIXES.extend(Affix(*a) for a in affixes)

# try the stats thing on a bow
bow = Item.query.filter(
    Item.name.like("%Tempest Wing%"),
    Item.type == "Citadel Bow",
).one()

print bow.numeric_mods
