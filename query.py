import json
import re
import click
from collections import namedtuple

from app import db
from models import Item, Modifier, Location, in_page_group
# from sqlalchemy import false


def find_gaps(loc):
    """returns the coordinates that have not been used"""
    # a page is 12 * 12
    page = []
    for i in range(12):
        page.append([0] * 12)


    for item in Item.query.filter(Item.location == loc).all():
        for x in range(item.x, item.x + item.w):
            for y in range(item.y, item.y + item.h):
                page[y][x] = 1

    gaps = []
    for y in range(12):
        for x in range(12):
            if not page[y][x]:
                gaps.append((x, y))
    return gaps


items = Item.query.join(Item.location).filter(
    *in_page_group("gems")
).all()
from collections import Counter
gem_counts = Counter(item.type.replace("Superior ", "") for item in items)

for gem, cnt in gem_counts.most_common():
    if cnt < 4:
        break
    print gem, cnt

exit()


data = {}
for l in open("item_data.json"):
    data.update(json.loads(l))

from pprint import pprint

# namedtuples are easier to work with
Affix = namedtuple('Affix', ('name', 'lvl', 'stat', 'value'))

AFFIXES = []
for k in ("Prefixes", "Suffixes"):
    for affixes in data[k].values():
        for a in affixes:
            a[1] = int(a[1])
            if len(a) == 4:
                AFFIXES.append(
                    Affix(*a)
                )
            # has min and max stats
            elif len(a) == 6:
                AFFIXES.append(
                    Affix(a[0], a[1], a[2:4], a[4:])
                )
            elif len(a) == 8:
                AFFIXES.append(
                    Affix(a[0], a[1], a[2:5], a[5:])
                )

# try the stats thing on a bow
bow = Item.query.filter(
    Item.name.like("%Tempest Wing%"),
    Item.type == "Citadel Bow",
).one()

print bow.numeric_mods
