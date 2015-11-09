# runs the spider and dumps the data about the characters and the stash into
# the database

import json
import re
import subprocess
from collections import defaultdict
from decimal import Decimal
from pprint import pprint

from blessings import Terminal
import click

from app import db
from models import Item, Requirement, Property, Location, Modifier

MOD_NUM_RE = re.compile(r"[-+]?[0-9\.]+?[%]?")
RANGE_MOD_RE = re.compile(r"(\d+)-(\d+)")
NORM_MOD_RE = re.compile(r"""[-+]?  # possible sign
                             (?P<num>(\d+\.)?\d+)  # actual number
                         """, re.VERBOSE)
WHITESPACE_RE = re.compile('\s+')


def mod_tsvector(mod):
    """normalizes a mod for full text search by removing the numbers"""
    return WHITESPACE_RE.sub(' ', MOD_NUM_RE.sub("", mod).strip()).lower()


def mod_norm(mod):
    """
    normalizes the numeric values for mods, replacing them with an 'X'
    returns a tuple (normalized mod string, list of numeric mod values)
    """
    if re.search(r"\d", mod) is None:
        return (mod, [])

    # double values, is a range
    m = RANGE_MOD_RE.search(mod)
    if m:
        return (RANGE_MOD_RE.sub(r"X - X", mod),
                [float(n) for n in m.groups()])

    # single value
    m = NORM_MOD_RE.search(mod)
    return (NORM_MOD_RE.sub("X", mod),
            [Decimal(m.groupdict()["num"])])


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
        # strip the strange metadata
        return re.sub(r"<.*>", "", self.data.get("name", ""))

    @property
    def type_(self):
        # strip the strange metadata
        return re.sub(r"<.*>", "", self.data["typeLine"])

    @property
    def requirements(self):
        """reformats the requirements into a simple dict"""
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
    def mods(self):
        """reformats the modifiers with normalization into a list of dicts"""
        ret = []
        for m in self.data.get("implicitMods", []):
            normalized, values = mod_norm(m)
            ret.append({
                "original": m,
                "normalized": normalized,
                "values": values,
                "is_implicit": True,
            })
        for m in self.data.get("explicitMods", []):
            normalized, values = mod_norm(m)
            ret.append({
                "original": m,
                "normalized": normalized,
                "values": values,
                "is_implicit": False,
            })
        return ret

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
        returns a string of the rarity of the item, based on frameType
        """
        return (
            "normal",
            "magic",
            "rare",
            "unique",
            "gem",
            "currency",
            "divination_card",
            "quest",
        )[self.data["frameType"]]

    def full_text(self):
        """
        returns a textual representation of the item for full text search
        """
        out = []
        # handle title, type and sockets
        if self.name:
            out.append(self.name)
        out.append(self.type_)
        if self.socket_str:
            out.append(self.socket_str)
        if self.data["identified"]:
            for prop in self.properties:
                if prop["value"]:
                    out.append(
                        mod_tsvector("%s: %s" % (prop["name"], prop["value"])))
                else:
                    out.append(mod_tsvector(prop["name"]))
            for mod in self.data.get('implicitMods', []):
                out.append(mod_tsvector(mod))
            for mod in self.data.get('explicitMods', []):
                out.append(mod_tsvector(mod))
        return "\n".join(out)

    def sql_dump(self, location, **kwargs):
        """
        returns an Item suitable for adding to the database
        """
        league = self.data.get("league", getattr(self, "league", "Standard"))
        try:
            return Item(
                name=self.name,
                type_=self.type_,
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
                mods=[Modifier(**m) for m in self.mods],
                requirements=[Requirement(**r) for r in self.requirements],
                properties=[Property(**p) for p in self.properties],
                socketed_items=[
                    ItemData(x, league=league).sql_dump(location) for x in
                    self.data.get("socketedItems", [])
                ],
                location=location,
                **kwargs
            )
        # show some debugging output
        except:
            raise
            pprint.pprint(self.data)


def dump_items(pages):
    for page in pages:
        loc = Location(**page.pop("location"))
        for item in page["items"]:
            try:
                item = ItemData(item)
                sql = item.sql_dump(loc)
            except AssertionError:
                # nice to have debugging info
                pprint(item.data)
                raise
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
@click.option('--leagues', default="all", type=str,
              help="Leagues(s) to fetch. Use 'all' to fetch all leagues")
@click.option('--fetch/--no-fetch', default=True,
              help="Performs fetching of data from Path of Exile.")
@click.option('--page-group', '--page-groups', default="", type=str,
              help="comma separated list of page groups to fetch")
@click.option('--page', '--pages', default="", type=str,
              help="comma separated list of pages to fetch")
@click.option('--debug/--no-debug', default=False,
              help="Enable scrapy's log for debugging")
def run(leagues, fetch, page_groups, pages, debug):
    t = Terminal()

    # run the spider
    if fetch:
        click.echo(t.green("FETCHING ITEMS..."))
        run_scraper(
            "main",
            debug=debug,
            page_groups=page_groups.strip(),
            leagues=leagues.strip(),
        )

    # drop and recreate the database
    click.echo(t.green("WRITING TO DATABASE..."))
    db.drop_all()
    db.create_all()

    # actual parsing and writing of items to the database
    dump_items(read_jsonlines("main"))
    db.session.commit()

    click.echo(t.green("%d Items Written" % (Item.query.count())))


if __name__ == "__main__":
    run()
