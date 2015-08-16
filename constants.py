# -*- coding: utf-8 -*-
import json
from utils import norm

# """
# #normalize to lower case
# #cast to tuple for easy application for startswith and endswith
# # UNIQUES = tuple([norm(x) for x in UNIQUES])

# """force a fetch of all the constants"""
# CONSTANTS = [
#     "UNIQUES",

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


def get_weapon_constants(data):
    """returns all the weapon constants"""
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

    return {k: v for k, v in locals().iteritems() if k.upper() == k}


def get_armor_constants(data):
    """returns all the weapon constants"""
    BOOTS = groupby_stat_type(data["Armour"]["Boots"])
    SHIELDS = groupby_stat_type(data["Armour"]["Shield"])
    GLOVES = groupby_stat_type(data["Armour"]["Gloves"])
    HELMS = groupby_stat_type(data["Armour"]["Helmet"])
    ARMORS = groupby_stat_type(data["Armour"]["Body Armour"])

    ret = {"ARMORS_ALL": []}
    for k, v in locals().iteritems():
        if k.upper() != k:
            continue
        ret[k] = v
        ret["ARMORS_ALL"].extend(v.keys())
    return ret


def get_gamepedia_constants(data):
    DIVINATION_CARDS = [x[0] for x in data["List of divination cards"]]
    BELTS = [x[0] for x in data["Belts"]]
    QUIVERS = [x[0] for x in data["Quivers"]]
    QUIVERS.extend([x[0] for x in data["Old quivers"]])

    # merge everything into a giant central dict
    return {k: v for k, v in locals().iteritems() if k.upper() == k}

# process item data from official PoE site
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

GEMS = {}
for key in ("Strength", "Dexterity", "Intelligence", "Support Gems"):
    for k, v in data[key]:
        GEMS[k] = v

# dynamically add the variables to the module namespace
vars().update(get_weapon_constants(data))
vars().update(get_armor_constants(data))

# process item data from gamepedia
data = {}
with open("gamepedia.json") as fp:
    for line in fp:
        data.update(json.loads(line))

vars().update(get_gamepedia_constants(data))
