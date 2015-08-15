# runs the spider and dumps the data about the characters and the stash into
# the database

from __future__ import print_function
import json
import pprint
import re
import subprocess
from collections import defaultdict

from blessings import Terminal
import click

from app import db
from models import Item, Requirement, Property, Location

MOD_NUM_RE = re.compile(r"[-+]?[0-9\.]+?[%]?")
WHITESPACE_RE = re.compile('\s+')


def norm_mod(mod):
    # normalizes a mod by removing the numbers
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

    def __init__(self, data, **kwargs):
        self.data = data
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return pprint.pformat(self.data)

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def keys(self):
        return list(self.data.keys())

    def values(self):
        return list(self.data.keys())

    def items(self):
        return list(self.data.items())

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
        # sort and join the groups
        grps = [''.join(sorted(x)) for x in list(grps.values())]
        return ' '.join(sorted(grps, key=lambda g: (-len(g), g)))

    def char_location(self):
        if "inventoryId" not in self.data:
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

    @property
    def rarity(self):
        """
        returns a string representing the rarity of the item, possible values
        are: normal, magic, rare, unique
        """
        if self.data["frameType"] == 3:
            return "unique"
        if self.data["frameType"] == 1:
            return "magic"
        if self.data["frameType"] == 2:
            return "rare"
        return "normal"

    def full_text(self):
        """
        returns a textual representation of the item for full text search
        """
        out = []
        # handle title, type and sockets
        if self.name:
            out.append(self.name)
        out.append(self.type)
        if self.socket_str:
            out.append(self.socket_str)
        if self.data["identified"]:
            for prop in self.properties:
                if prop["value"]:
                    out.append(
                        norm_mod("%s: %s" % (prop["name"], prop["value"])))
                else:
                    out.append(norm_mod(prop["name"]))
            for mod in self.mods:
                out.append(norm_mod(mod))
        return "\n".join(out)

    def sql_dump(self, location, **kwargs):
        """
        returns an Item suitable for adding to the database
        """
        league = self.data.get("league", getattr(self, "league", "Standard"))
        try:
            return Item(
                name=self.name,
                type=self.type,
                x=self.data.get("x", None),
                y=self.data.get("y", None),
                w=self.data["w"],
                h=self.data["h"],
                rarity=self.rarity,
                icon=self.data["icon"],
                num_sockets=self.num_sockets(),
                socket_str=self.socket_str,
                is_identified=self.data["identified"],
                is_corrupted=self.data["corrupted"],
                char_location=self.char_location(),
                full_text=db.func.to_tsvector(self.full_text()),
                league=league,
                mods=self.mods,
                requirements=[Requirement(**r) for r in self.requirements],
                properties=[Property(**p) for p in self.properties],
                socketed_items=[
                    ItemData(x, league=league).sql_dump(location) for x in
                    self.data.get("socketedItems", [])
                ],
                location=Location(**location),
                **kwargs
            )
        # show some debugging output
        except:
            raise
            pprint.pprint(self.data)


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


def dump_items(pages):
    for page in pages:
        loc = page.pop("location")
        for item in page["items"]:
            sql = ItemData(item).sql_dump(loc)
            # click.echo(sql)
            db.session.add(sql)


def run_scraper(crawler_name, debug=False, **kwargs):
    """runs the given scraper and writes the jsonlines output"""
    outfile = "%s.json" % crawler_name
    open(outfile, 'w').close()  # truncate the output file

    cmd = ["scrapy", "crawl"]
    if not debug:
        cmd.append("--nolog")
    cmd.append(crawler_name)

    # pass in extra keyword args as needed
    for k, v in kwargs.iteritems():
        cmd += ['-a', "%s=%s" % (k, v)]

    cmd += ["-t", "jsonlines", "-o", outfile]
    # click.echo(" ".join(cmd))
    subprocess.call(cmd)


def read_jsonlines(crawler_name):
    """returns the fetched data as a list of dicts"""
    with open("%s.json" % crawler_name) as fp:
        return [json.loads(line) for line in fp]


@click.command()
@click.option('--leagues', default="all",
              help="Leagues(s) to fetch. Use 'all to fetch all leagues'")
@click.option('--debug/--no-debug', default=False,
              help="Enable scrapy's log for debugging")
def run(leagues, debug):
    t = Terminal()
    # drop and recreate the database
    destroy_database(db.engine)
    db.create_all()

    # leagues = set([l.strip().lower() for l in leagues.split(",")])

    # run the spider and fetch the data, we never cache
    click.echo(t.green("RUNNING SPIDER..."))
    # run_scraper("main")  # , debug=True)
    dump_items(read_jsonlines("main"))

    # final commit
    click.echo(t.green("WRITING TO DATABASE..."))
    db.session.commit()
    click.echo(t.green("%d Items Written" % (Item.query.count())))


if __name__ == "__main__":
    run()
