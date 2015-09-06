import json
import re
from decimal import Decimal

import click
from blessings import Terminal
from pprint import pprint

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


def dump_db_affixes():
    for affix in db.session.query(
        Modifier.normalized
    ).filter(
        # only want numeric mods
        Modifier.normalized.like('%X%'),
        # filter divination card stuff
        ~Modifier.normalized.like('<%'),
    ).distinct().order_by(Modifier.normalized).all():
        print affix[0]


def dump_scraped_affixes():
    affix_stats = []
    for affix in get_affixes():
        affix_stats.extend(affix.stats)

    for affix in sorted(set(affix_stats)):
        print affix

dump_db_affixes()
