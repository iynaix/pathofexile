import json
import re
from decimal import Decimal

import click
from blessings import Terminal

from app import db
from models import Item, Modifier, Location, in_page_group
# from sqlalchemy import false

t = Terminal()


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
        mid = len(rest) // 2
        # there might be a few stats with an extra value, i.e. len(stats) !=
        # len(vals)
        self.stats = []
        self.values = []
        for stat, val in zip(rest[:mid], rest[-mid:]):
            # handle values as a range
            val = [int(v) for v in val.split(" to ")]

            stat = re.sub(r"^(Local )?(Base )?(?P<mod>.*)", r"\g<mod>", stat)
            if stat.endswith(" Permyriad"):
                stat = stat.replace(" Permyriad", stat)
                val = [Decimal(v) / 10000 for v in val]

            self.stats.append(stat)
            self.values.append(val)


def get_affixes():
    data = {}
    for l in open("item_data.json"):
        data.update(json.loads(l))

    ret = []
    for k in ("Prefixes", "Suffixes"):
        for affixes in data[k].values():
            ret.extend(Affix(*a) for a in affixes)
    return ret


def color_table(*args):
    """prints a nice table in pretty colors"""
    colors = (t.green, t.blue, t.yellow, t.red,)
    return "\t".join(color(str(s)) for color, s in zip(colors, args))


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


# # testing mods
# t = Terminal()
# for item in results:
#     for mod in item.numeric_mods:
#         match, ratio = process.extractOne(mod.original, affix_stats,
#                                           scorer=fuzz.token_set_ratio)
#         click.echo("\t".join((
#             t.green(mod.original),
#             t.blue(mod.normalized),
#             t.yellow(match),
#             t.red(str(ratio))
#         )))

x = set()
numeric_mods = Modifier.query.filter(
    Modifier.original != Modifier.normalized,
    # Modifier.normalized.like("%increased%"),
    # Modifier.normalized.like("%X - X%"),
).all()
for mod in numeric_mods:
    # X% increased
    new = re.sub(r"^\d+% increased (?P<mod>.*)", r"\g<mod> +%", mod.original)
    if mod.original != new:
        continue

    new = re.sub(r"Adds \d+-\d+ (?P<mod>.*) to Attacks",
                 r"Added \g<mod>", mod.original)
    if mod.original != new:
        continue

    print color_table(mod.original, mod.normalized)
    # print color_table(mod.original, new)


for a in x:
    print a
