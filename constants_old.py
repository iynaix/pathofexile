# -*- coding: utf-8 -*-
from utils import get_constant

"""
#normalize to lower case
#cast to tuple for easy application for startswith and endswith
# PREFIXES = tuple([norm(x) for x in PREFIXES])
# SUFFIXES = tuple([norm(x) for x in SUFFIXES])
# UNIQUES = tuple([norm(x) for x in UNIQUES])

#merge all the weapons into a giant central dict
WEAPONS = {}
for w in [AXES, BOWS, CLAWS, DAGGERS, MACES, STAVES, SWORDS, WANDS]:
    WEAPONS.update(w)

ARMORS_ALL = {}
for w in [HELMS, ARMORS, GLOVES, BOOTS, SHIELDS]:
    ARMORS_ALL.update(w)

#get all the one handed weapons
ONE_HANDED_WEAPONS = {}
for w in [CLAWS, DAGGERS, WANDS]:
    ONE_HANDED_WEAPONS.update(w)
for w in [AXES, MACES, SWORDS]:
    for k, v in w.items():
        if v["subtype"].startswith(("One", "Mace", "Rapier", "Sceptre")):
            ONE_HANDED_WEAPONS[k] = v

#get all the two handed weapons
TWO_HANDED_WEAPONS = {}
for w in [BOWS, STAVES]:
    TWO_HANDED_WEAPONS.update(w)
for w in [AXES, MACES, SWORDS]:
    for k, v in w.items():
        if v["subtype"].startswith(("Two", "Maul")):
            TWO_HANDED_WEAPONS[k] = v
"""


"""force a fetch of all the constants"""
CONSTANTS = [
    "GEMS",
    "UNIQUES",
    "QUIVERS",
    "BELTS",
    "WANDS",
    "STAVES",
    "DAGGERS",
    "CLAWS",
    "GLOVES",
    "BOOTS",
    "SHIELDS",
    "HELMS",
    "ARMORS",
    "BOWS",
    "AXES",
    "MACES",
    "SWORDS",
    "PREFIXES",
    "SUFFIXES",
    "CURRENCIES",
    "FLASK_SIZES",
    "MISC_FLASKS",
    "QUEST_ITEMS",
]
for c in CONSTANTS:
    get_constant(c)
