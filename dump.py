import json
import pprint
import re
from collections import defaultdict, OrderedDict
from clint.textui import colored
from affixes import PREFIXES, SUFFIXES, UNIQUES, QUEST_ITEMS
from utils import norm
from path import path

import q

CHROMATIC_RE = re.compile(r"B+G+R+")
MOD_NUM_RE = re.compile(r"[-+]?[0-9\.]+?[%]?")
WHITESPACE_RE = re.compile('\s+')


def norm_mod(mod):
    #normalizes a mod by removing the numbers
    return WHITESPACE_RE.sub(' ', MOD_NUM_RE.sub("", mod).strip()).lower()


def iter_items():
    """returns a generator that yields items across all stash page"""
    #get the data from the stash pages
    fp = open("data/stash_1.json")
    tabs = json.load(fp)["tabs"]
    for page_no, t in enumerate(tabs):
        page = Tab(t).create_stash_page()
        for item in page.items:
            yield Item(item, "Stash_%s" % (page_no + 1))

    #get the data from the characters
    for f in path("data").listdir():
        if f.name.startswith("items_"):
            char_name = f.basename().split("_").pop().split(".")[0]
            for item in json.load(open(f))["items"]:
                yield Item(item,
                           "%s_%s" % (char_name, item["inventoryId"].lower()))


class Tab(object):
    """Object representing a stash tab"""

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return pprint.pformat(self.data)

    def is_premium(self):
        #see if the name is numeric
        try:
            int(self.data["n"])
        except ValueError:
            return True
        if self.data['colour'] != {'b': 54, 'g': 84, 'r': 124}:
            return True
        return False

    @property
    def index(self):
        return self.data["i"]

    @property
    def name(self):
        return self.data["n"]

    def create_stash_page(self):
        """returns a StashPage object for the tab"""
        fname = "data/stash_%s.json" % (self.index + 1)
        return StashPage(json.load(open(fname))["items"], self)


class StashPage(object):
    """Object representing a stash page"""

    def __init__(self, items, tab):
        """takes the items and the associated tab object"""
        self.tab = tab
        self.items = [Item(item, "Stash_%s" % (self.index + 1)) for
                      item in items]

    def __repr__(self):
        return pprint.pformat(self.items)

    def __iter__(self):
        return self.items.__iter__()

    def __getitem__(self, idx):
        return self.items.__getitem__(idx)

    def __len__(self):
        return len(self.items)

    @property
    def index(self):
        return self.tab.index

    @property
    def name(self):
        return self.tab.name

    def find_holes(self):
        """returns the coordinates that have not been used"""
        #a page is 12 * 12
        page = []
        for i in range(12):
            page.append([0] * 12)

        for item in self.items:
            for x in range(item["x"], item["x"] + item["w"]):
                for y in range(item["y"], item["y"] + item["h"]):
                    page[y][x] = 1

        holes = []
        for y in range(12):
            for x in range(12):
                if not page[y][x]:
                    holes.append((x, y))
        return holes

    def is_filled(self):
        """is the page filled?"""
        return not bool(self.find_holes())


class Item(object):
    """Object representing an item"""

    def __init__(self, data, location):
        """
        takes the items and the associated location, which might be a stash
        page or a location on a character
        """
        self.data = data
        self.location = location
        #cached value for socket_str
        self._socket_str = None

    def __repr__(self):
        return pprint.pformat(self.data)

    def __str__(self):
        out = []
        # if self.is_rare():
        #     out.append(colored.yellow(self.data["name"]).color_str)
        #     out.append(colored.yellow(self.data["typeLine"]).color_str)
        if self.name:
            out.append(self.name)
        else:
            out.append(self.type)
        out.append("({0}: {x}, {y})".format(self.location, **self.data))
        if self.socket_str:
            out.append("Sockets: %s" % self.socket_str_color())
        return "\n".join(out)

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

    def has_sockets(self):
        return bool(self.data["sockets"])

    def num_sockets(self):
        return len(self.data["sockets"])

    @property
    def name(self):
        return self.data.get("name", "")

    @property
    def type(self):
        return self.data["typeLine"]

    def _process_prop(self, prop_dict):
        """
        utility function that returns the needed tuple given a property
        dict
        """
        v = prop_dict["values"]
        if not v:
            v = ""
        else:
            v = v[0][0]
        return prop_dict["name"], v.replace("/", " / ")

    @property
    def requirements(self):
        """reformats the requirements into a simple dictionary"""
        reqs = []
        for r in self.data.get("requirements", []):
            reqs.append(self._process_prop(r))
        return OrderedDict(sorted(reqs))

    @property
    def properties(self):
        """returns a list of properties"""
        props = []
        for p in self.data.get('properties', []):
            props.append(self._process_prop(p))
        for p in self.data.get('additionalProperties', []):
            props.append(self._process_prop(p))
        return OrderedDict(sorted(props))

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
        if self._socket_str is not None:
            return self._socket_str

        if not self.has_sockets():
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
        self._socket_str = ' '.join(sorted(grps, key=lambda g: (-len(g), g)))
        return self._socket_str

    def socket_str_color(self):
        """
        returns the socket_str with colors suitable for output to a console
        """
        s = self.socket_str.replace("B", colored.cyan('B').color_str)
        s = s.replace("G", colored.green('G').color_str)
        return s.replace("R", colored.red('R').color_str)

    def socket_str_html(self):
        """
        returns the socket_str with colors suitable for output to html
        """
        out = []
        for c in self.socket_str:
            if c == "B":
                out.append('<span class="label label-primary">&nbsp;</span>')
            elif c == "G":
                out.append('<span class="label label-success">&nbsp;</span>')
            elif c == "R":
                out.append('<span class="label label-danger">&nbsp;</span>')
            else:
                out.append('&nbsp;')
        #join with hair spaces
        return "&#8202;".join(out)

    def is_chromatic(self):
        #must have at least 3 sockets
        if self.num_sockets() < 3:
            return False

        return bool(CHROMATIC_RE.search(self.socket_str))

    def is_magic(self):
        #normalize to lower case
        name = norm(self.name)
        t = norm(self.type)
        if name.endswith(SUFFIXES) or t.endswith(SUFFIXES):
            return True
        if name.startswith(PREFIXES) or t.startswith(PREFIXES):
            return True
        return False

    def is_rare(self):
        if self.is_unique() or self.is_magic():
            return False
        if not self.name:
            return False
        return True

    def is_unique(self):
        name = norm(self.name)
        if not name:
            return False
        return name in UNIQUES

    def is_normal(self):
        return not (self.is_magic() or self.is_rare() or self.is_unique())

    def is_gem(self):
        return "Experience" in self.properties.keys()

    @property
    def rarity(self):
        """
        returns a string representing the rarity of the item, possible values
        are: normal, magic, rare, unique
        """
        if self.is_unique():
            return "unique"
        if self.is_rare():
            return "rare"
        if self.is_magic():
            return "magic"
        return "normal"

    def title_contains(self, search_str):
        """
        utility function, does the given search string exist within the item
        name or type?
        """
        search_str = norm(search_str)
        return search_str in norm(self.name) or search_str in norm(self.type)

    def is_quest_item(self):
        return norm(self.type).startswith(QUEST_ITEMS)


def search_items():
    """
    Temporary function that just returns an iterator of search results
    """
    all_mods = set()
    for item in iter_items():
        if item.mods:
            all_mods.update(norm_mod(m) for m in item.mods)
            yield item

    for m in all_mods:
        q(m)
    q(len(all_mods))

    """
    u'name': 342,
    u'typeLine': 342,

    u'inventoryId': 342,

    #store as postgres rectangle
    u'x': 342,
    u'y': 342
    u'w': 342,
    u'h': 342,

    #add these together
    u'properties': 300,
    u'additionalProperties': 44,

    u'requirements': 303,

    #add these together
    u'implicitMods': 108,
    u'explicitMods': 253,

    #socket links?
    u'sockets': 342,

    #no data yet
    u'socketedItems': 342,
    """

if __name__ == "__main__":
    for item in search_items():
        print item
        print
