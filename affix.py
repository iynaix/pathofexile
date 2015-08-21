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
        self.stats = rest[:(len(args) / 2)]
        self.values = rest[(len(args) / 2):]


def get_affixes():
    data = {}
    for l in open("item_data.json"):
        data.update(json.loads(l))

    ret = []
    for k in ("Prefixes", "Suffixes"):
        for affixes in data[k].values():
            ret.extend(Affix(*a) for a in affixes)
    return ret


from pprint import pprint

# try the stats thing on a bow
results = Item.query.filter(
    # Item.name.like("%Tempest Wing%"),
    # Item.type == "Citadel Bow",
    Item.type.like("%Bow%"),
).all()

# print bow.numeric_mods

AFFIXES = get_affixes()
affix_stats = []
for a in AFFIXES:
    affix_stats.extend(a.stats)

from fuzzywuzzy import fuzz, process
from blessings import Terminal


t = Terminal()
for item in results:
    for mod in item.numeric_mods:
        mod = mod.original
        match, ratio = process.extractOne(mod, affix_stats, scorer=fuzz.QRatio)
        click.echo("%s\t%s\t%s" % (t.green(mod), t.yellow(match), t.red(str(ratio))))
