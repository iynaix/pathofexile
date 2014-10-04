# -*- coding: utf-8 -*-
from collections import OrderedDict
from utils import norm, get_constant

# QUEST_ITEMS = [
#     "Alira's Amulet",
#     "Allflame",
#     "Ammonite Glyph",
#     "Baleful Gem",
#     "Book of Regrets",
#     "Book of Skill",
#     "Bust of Gaius Sentari",
#     "Bust of Hector Titucius",
#     "Bust of Marceus Lioneye",
#     "Chitus' Plum",
#     "Decanter Spiritus",
#     "Golden Hand",
#     "Golden Page",
#     "Haliotis Glyph",
#     "Infernal Talc",
#     "Kraityn's Amulet",
#     "Maligaro's Spike",
#     "Medicine Chest",
#     "Oak's Amulet",
#     "Ribbon Spool",
#     "Roseus Glyph",
#     "Sewer Keys",
#     "Thaumetic Emblem",
#     "Thaumetic Sulphite",
#     "The Apex",
#     "Tolman's Bracelet",
#     "Tower Key",
# ]

# CURRENCIES = OrderedDict([
#     ("Scroll of Wisdom", "Identifies an item"),
#     ("Portal Scroll", "Creates a portal to town"),
#     ("Armourer's Scrap", "Improves the quality of an armour"),
#     ("Blacksmith's Whetstone", "Improves the quality of a weapon"),
#     ("Glassblower's Bauble", "Improves the quality of a flask"),
#     ("Cartographer's Chisel", "Improves the quality of a map"),
#     ("Gemcutter's Prism", "Improves the quality of a gem"),
#     ("Jeweller's Orb", "Reforges the number of sockets on an item"),
#     ("Chromatic Orb", "Reforges the colour of sockets on an item"),
#     ("Orb of Fusing", "Reforges the links between sockets on an item"),
#     ("Orb of Transmutation", "Upgrades a normal item to a magic item"),
#     ("Orb of Chance", "Upgrades a normal item to a random rarity"),
#     ("Orb of Alchemy", "Upgrades a normal item to rare item"),
#     ("Regal Orb", "Upgrades a magic item to rare item"),
#     ("Orb of Augmentation", "Enchants a magic item with a new random property"),
#     ("Exalted Orb", "Enchants a rare item with a new random property"),
#     ("Orb of Alteration", "Reforges a magic item with new random properties"),
#     ("Chaos Orb", "Reforges a rare item with new random properties"),
#     ("Blessed Orb", "Randomises the numeric values of the implicit properties of an item"),
#     ("Divine Orb", "Randomises the numeric values of the random properties of an item"),
#     ("Orb of Scouring", "Removes all properties from an item"),
#     ("Mirror of Kalandra", "Creates a mirrored copy of an item"),
#     ("Eternal Orb", "Creates an imprint of an item for later restoration"),
#     ("Orb of Regret", "Grants a passive skill refund point"),
# ])

"""
#normalize to lower case
#cast to tuple for easy application for startswith and endswith
# PREFIXES = tuple([norm(x) for x in PREFIXES])
# SUFFIXES = tuple([norm(x) for x in SUFFIXES])
# UNIQUES = tuple([norm(x) for x in UNIQUES])
QUEST_ITEMS = tuple([norm(x) for x in QUEST_ITEMS])

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


if __name__ == "__main__":
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
        print "FETCHING CONSTANT '%s'" % c
        get_constant(c)
