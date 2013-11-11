import json
import pprint
import re
from collections import defaultdict
from clint.textui import colored
from constants import PREFIXES, SUFFIXES, UNIQUES
from path import path
from utils import norm

from app import db
from models import Item, Requirement, Property, Location

MOD_NUM_RE = re.compile(r"[-+]?[0-9\.]+?[%]?")
WHITESPACE_RE = re.compile('\s+')


def norm_mod(mod):
    #normalizes a mod by removing the numbers
    return WHITESPACE_RE.sub(' ', MOD_NUM_RE.sub("", mod).strip()).lower()


# def find_holes(self):
#     """returns the coordinates that have not been used"""
#     #a page is 12 * 12
#     page = []
#     for i in range(12):
#         page.append([0] * 12)

#     for item in self.items:
#         for x in range(item["x"], item["x"] + item["w"]):
#             for y in range(item["y"], item["y"] + item["h"]):
#                 page[y][x] = 1

#     holes = []
#     for y in range(12):
#         for x in range(12):
#             if not page[y][x]:
#                 holes.append((x, y))
#     return holes

# def is_filled(self):
#     """is the page filled?"""
#     return not bool(self.find_holes())


class ItemData(object):
    """Object representing an item"""

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return pprint.pformat(self.data)

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def iteritems(self):
        return self.data.iteritems()

    def __contains__(self, val):
        return self.data.__contains__(val)

    def num_sockets(self):
        return len(self.data["sockets"])

    @property
    def name(self):
        return self.data.get("name", "")

    @property
    def type(self):
        return self.data["typeLine"]

    @property
    def requirements(self):
        """reformats the requirements into a simple dictionary"""
        reqs = []
        for r in self.data.get("requirements", []):
            v = r["values"][0][0]
            if r["name"] == "Level":
                v = int(v.split()[0])
            else:
                v = int(v)
            reqs.append({"name": r["name"], "value": v})
        return reqs

    @property
    def properties(self):
        """returns a list of properties"""
        item_props = self.data.get('properties', []) + \
                self.data.get('additionalProperties', [])

        props = []
        for p in item_props:
            v = p["values"]
            if not v:
                v = ""
            else:
                v = v[0][0]
            props.append({"name": p["name"], "value": v})
        return props

    @property
    def mods(self):
        """returns a list of mods"""
        return self.data.get('implicitMods', []) + \
            self.data.get('explicitMods', [])

    @property
    def socket_str(self):
        """
        shows the available sockets from longest link to shortest, separated
        by spaces, e.g. 'BGR GR'
        """
        if not self.num_sockets:
            return ""

        grps = defaultdict(list)
        for s in self.data["sockets"]:
            if s["attr"] == "D":
                grps[s["group"]].append("G")
            elif s["attr"] == "I":
                grps[s["group"]].append("B")
            elif s["attr"] == "S":
                grps[s["group"]].append("R")
        #sort and join the groups
        grps = [''.join(sorted(x)) for x in grps.values()]
        return ' '.join(sorted(grps, key=lambda g: (-len(g), g)))

    def char_location(self):
        if not "inventoryId" in self.data:
            return None

        x = self.data["inventoryId"]
        if x.startswith("Stash"):
            return None

        if x.endswith("2"):
            x = x[:-1]
        if x == "BodyArmour":
            return "Armour"
        if x == "MainInventory":
            return "Inventory"
        return x

    def is_magic(self):
        #normalize to lower case
        if self.name:
            return False

        t = norm(self.type)
        return t.startswith(PREFIXES) or t.endswith(SUFFIXES)

    def is_rare(self):
        if self.is_unique() or self.is_magic():
            return False
        return bool(self.name)

    def is_unique(self):
        name = norm(self.name)
        if not name:
            return False
        return name in UNIQUES

    def is_normal(self):
        return not (self.is_magic() or self.is_rare() or self.is_unique())

    @property
    def rarity(self):
        """
        returns a string representing the rarity of the item, possible values
        are: normal, magic, rare, unique
        """
        if self.is_unique():
            return "unique"
        if self.is_magic():
            return "magic"
        #check if item is rare
        #we're not using the is_rare() method as that would compute the
        #is_unique() and is_magic() methods again
        if self.name:
            return "rare"
        return "normal"

    def title_contains(self, search_str):
        """
        utility function, does the given search string exist within the item
        name or type?
        """
        search_str = norm(search_str)
        return search_str in norm(self.name) or search_str in norm(self.type)

    def sql_dump(self, location, **kwargs):
        """
        returns an Item suitable for adding to the database
        """
        return Item(
            name=self.name,
            type=self.type,
            x=self.data.get("x", None),
            y=self.data.get("y", None),
            w=self.data["w"],
            h=self.data["h"],
            rarity=self.rarity,
            num_sockets=self.num_sockets(),
            socket_str=self.socket_str,
            is_identified=self.data["identified"],
            char_location=self.char_location(),
            mods=self.mods,
            requirements=[Requirement(**r) for r in self.requirements],
            properties=[Property(**p) for p in self.properties],
            socketed_items=[ItemData(x).sql_dump(location) for x in
                            self.data.get("socketedItems", [])],
            location=location,
            **kwargs
        )


def destroy_database(engine):
    """
    completely destroys the database, copied from

    http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything
    """
    from sqlalchemy.engine import reflection
    from sqlalchemy.schema import (
        MetaData,
        Table,
        DropTable,
        ForeignKeyConstraint,
        DropConstraint,
    )

    conn = engine.connect()

    # the transaction only applies if the DB supports
    # transactional DDL, i.e. Postgresql, MS SQL Server
    trans = conn.begin()

    inspector = reflection.Inspector.from_engine(engine)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.
    metadata = MetaData()

    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(ForeignKeyConstraint((), (), name=fk['name']))
        t = Table(table_name, metadata, *fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))

    for table in tbs:
        conn.execute(DropTable(table))

    trans.commit()


def dump_stash_page(page_no, tab_data, dump=True):
    fname = "data/stash_%s.json" % (page_no + 1)

    #see if the name is numeric to determine if premium
    is_premium = False
    try:
        int(tab_data["n"])
    except ValueError:
        is_premium = True
    if tab_data['colour'] != {'b': 54, 'g': 84, 'r': 124}:
        is_premium = True

    #create the location
    loc = Location(
        name=tab_data["n"],
        page_no=page_no + 1,
        is_premium=is_premium,
        is_character=False,
    )

    for item in json.load(open(fname))["items"]:
        if dump:
            db.session.add(
                ItemData(item).sql_dump(loc)
            )


def dump_char(fname, dump=True):
    if not isinstance(fname, path):
        fname = path(fname)

    #create the location
    char_name = fname.split("_").pop().split(".")[0].capitalize()
    loc = Location(
        name=char_name,
        is_premium=False,
        is_character=True,
    )
    for item in json.load(open(fname))["items"]:
        if dump:
            db.session.add(
                ItemData(item).sql_dump(loc)
            )
        else:
            from pprint import pprint
            item = ItemData(item)
            # if item.data["socketedItems"]:
            #     for socketed_item in item.data["socketedItems"]:
            #         pprint(socketed_item)
            if not item.data["x"]:
                print(item.data["inventoryId"])


if __name__ == "__main__":
    dump = True
    import time
    start_time = time.time()

    #drop and recreate the database
    if dump:
        destroy_database(db.engine)
        db.create_all()

    #dump the data from the stash pages
    fp = open("data/stash_1.json")
    tabs = json.load(fp)["tabs"]
    for page_no, tab_data in enumerate(tabs):
        dump_stash_page(page_no, tab_data, dump=dump)

    #get the data from the characters
    for f in path("data").listdir():
        if not f.name.startswith("items_"):
            continue

        dump_char(f, dump=dump)

    #final commit
    if dump:
        db.session.commit()

        print
        print colored.green(len(Item.query.all())),
        print "ITEMS PROCESSED."
        print "DATA DUMP COMPLETED IN",
        print colored.green("%.4f SECONDS" % (time.time() - start_time))
