import json
from collections import namedtuple, Counter, defaultdict

from app import db
from models import Item, Modifier, Location, in_page_group, Property
from sqlalchemy import cast, Integer


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


def find_dup_uniques():
    for item, cnt in Counter(item.name for item in Item.query.filter(
        Item.rarity == "unique",
        *in_page_group("uniques")
    )).most_common():
        if cnt <= 1:
            break
        print item, cnt


currencies = db.session.query(
    Item.type_,
    cast(db.func.split_part(Property.value, "/", 1), Integer)
).join(Property).filter(
    Item.rarity == "currency",
    Property.name.startswith("Stack"),
    *in_page_group("$")
).distinct().all()

counts = defaultdict(int)
for currency, stack in currencies:
    counts[currency] += stack

print counts
