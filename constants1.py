# -*- coding: utf-8 -*-
import json
from collections import OrderedDict
from utils import norm, get_constant

# """
# #normalize to lower case
# #cast to tuple for easy application for startswith and endswith
# # UNIQUES = tuple([norm(x) for x in UNIQUES])

# """force a fetch of all the constants"""
# CONSTANTS = [
#     "UNIQUES",
#     "GEMS",

#     "QUIVERS",
#     "BELTS",

#     "FLASK_SIZES",
#     "MISC_FLASKS",
# ]
# for c in CONSTANTS:
#     get_constant(c)


def stat_type(item):
    ret = []
    # get the stat type
    try:
        req_str, req_dex, req_int = item[-3:]
        if int(req_str):
            ret.append("Str")
        if int(req_dex):
            ret.append("Dex")
        if int(req_int):
            ret.append("Int")
    # not a valid entry, ignore
    except ValueError:
        return
    return ", ".join(ret)


def groupby_stat_type(items):
    ret = {}
    for x in items:
        res = stat_type(x)
        if res:
            ret[x[0]] = res
    return ret


if __name__ == "__main__":
    data = {}
    with open("item_data.json") as fp:
        for line in fp:
            data.update(json.loads(line))

    CURRENCIES = {x[2]: x[4] for x in data["Currency"].values()[0]}

    PREFIXES = []
    for prefix_type, prefixes in data["Prefixes"].iteritems():
        PREFIXES.extend([p[0] for p in prefixes])

    SUFFIXES = []
    for suffix_type, suffixes in data["Suffixes"].iteritems():
        SUFFIXES.extend([p[0] for p in suffixes])

    BOOTS = groupby_stat_type(data["Armour"]["Boots"])
    SHIELDS = groupby_stat_type(data["Armour"]["Shield"])
    GLOVES = groupby_stat_type(data["Armour"]["Gloves"])
    HELMS = groupby_stat_type(data["Armour"]["Helmet"])
    ARMORS = groupby_stat_type(data["Armour"]["Body Armour"])

    from pprint import pprint
    BOWS = [x[0] for x in data["Weapons"]["Bow"] if stat_type(x)]
    WANDS = [x[0] for x in data["Weapons"]["Wand"] if stat_type(x)]
    CLAWS = [x[0] for x in data["Weapons"]["Claw"] if stat_type(x)]
    DAGGERS = [x[0] for x in data["Weapons"]["Dagger"] if stat_type(x)]
    STAVES = [x[0] for x in data["Weapons"]["Staff"] if stat_type(x)]

    SWORDS = {}
    for sword_type in ("One Hand Sword", "Two Hand Sword",
                       "Thrusting One Hand Sword"):
        for x in data["Weapons"][sword_type]:
            if stat_type(x):
                SWORDS[x[0]] = sword_type

    MACES = {}
    for mace_type in ("One Hand Mace", "Two Hand Mace", "Sceptre"):
        for x in data["Weapons"][mace_type]:
            if stat_type(x):
                MACES[x[0]] = mace_type

    AXES = {}
    for axe_type in ("One Hand Axe", "Two Hand Axe"):
        for x in data["Weapons"][axe_type]:
            if stat_type(x):
                AXES[x[0]] = axe_type

    # get all the one handed weapons
    ONE_HANDED_WEAPONS = CLAWS + DAGGERS + WANDS
    TWO_HANDED_WEAPONS = BOWS + STAVES

    for w in [AXES, MACES, SWORDS]:
        for k, v in w.items():
            if "TWO" in v:
                TWO_HANDED_WEAPONS.append(k)
            else:
                ONE_HANDED_WEAPONS.append(k)

    # merge all the weapons into a giant central dict
    WEAPONS = BOWS + CLAWS + DAGGERS + STAVES + WANDS
    for w in AXES, MACES, SWORDS:
        WEAPONS.extend(w.keys())

    ARMORS = HELMS + ARMORS + GLOVES + BOOTS + SHIELDS
