# runs the spider and dumps the data about the characters and the stash into
# the database

from __future__ import print_function
import json
import itertools
import re
import pprint
import collections

from app import db
from blessings import Terminal
import click
from sqlalchemy import or_

from models import Item, Requirement, Property, Location

RESIST_RE = re.compile(r"\+(\d+)% to (.*) Resistances?")


def get_item_resists(item):
    ret = collections.Counter()
    for mod in item.mods:
        m = RESIST_RE.match(mod)
        if not m:
            continue
        amt, resist_types = m.groups()
        amt = int(amt)

        if resist_types == "all Elemental":
            ret.update({
                'Fire': amt,
                'Cold': amt,
                'Lightning': amt,
            })
        else:
            for rtype in resist_types.split(" and "):
                # don't care about chaos for now, remove if it matters
                if rtype == "Chaos":
                    continue
                ret[rtype] = amt
    return ret


t = Terminal()

jewelry = Item.query.filter(
    or_(Item.type.op('~')(r'\yRing\y'),
        Item.type.op('~')(r'\yAmulet\y')),
)

amulets, rings = [], []
for item in jewelry:
    resists = get_item_resists(item)
    if not resists:
        continue

    # group them
    if " Amulet" in item.type:
        amulets.append((item, resists))
    else:
        rings.append((item, resists))

click.echo(t.green("Rings: %s" % len(rings)))
click.echo(t.green("Amulets: %s" % len(amulets)))

max_combi = {
    "amulet": None,
    "ring1": None,
    "ring2": None,
    "resists": {},
    "total": -1,
}
i = 0
for amulet in amulets:
    for ring1, ring2 in itertools.combinations(rings, 2):
        i += 1
        resists = amulet[1] + ring1[1] + ring2[1]
        total = sum(resists.values()) * 1.0 / len(resists)
        if total > max_combi["total"]:
            max_combi = {
                "amulet": amulet,
                "ring1": ring1,
                "ring2": ring2,
                "resists": resists,
                "total": total,
            }

click.echo(pprint.pformat(max_combi))
click.echo(i)
