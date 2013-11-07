# -*- coding: utf-8 -*-
from utils import norm

#misc data dumps from the wiki

PREFIXES = [
    "Lacquered",
    "Reinforced",
    "Reinforced",
    "Layered",
    "Layered",
    "Studded",
    "Lobstered",
    "Lobstered",
    "Ribbed",
    "Buttressed",
    "Fortified",
    "Fortified",
    "Thickened",
    "Plated",
    "Plated",
    "Thickened",
    "Solid",
    "Carapaced",
    "Girded",
    "Carapaced",
    "Impregnable",
    "Beetle's",
    "Crab's",
    "Armadillo's",
    "Rhino's",
    "Elephant's",
    "Base Damage",
    "Glinting",
    "Burnished",
    "Polished",
    "Honed",
    "Gleaming",
    "Annealed",
    "Razor Sharp",
    "Tempered",
    "Flaring",
    "Heated",
    "Smoldering",
    "Smoking",
    "Burning",
    "Flaming",
    "Scorching",
    "Incinerating",
    "Blasting",
    "Cremating",
    "Frosted",
    "Chilled",
    "Icy",
    "Frigid",
    "Freezing",
    "Frozen",
    "Glaciated",
    "Polar",
    "Entombing",
    "Humming",
    "Buzzing",
    "Snapping",
    "Crackling",
    "Sparking",
    "Arcing",
    "Shocking",
    "Discharging",
    "Electrocuting",
    "Glinting",
    "Burnished",
    "Polished",
    "Honed",
    "Gleaming",
    "Annealed",
    "Razor Sharp",
    "Tempered",
    "Flaring",
    "Heavy",
    "Serrated",
    "Wicked",
    "Vicious",
    "Bloodthirsty",
    "Cruel",
    "Tyrannical",
    "Thorny",
    "Spiny",
    "Barbed",
    "Jagged",
    "Squire's",
    "Journeyman's",
    "Reaver's",
    "Mercenary's",
    "Champion's",
    "Conqueror's",
    "Emperor's",
    "Shining",
    "Protective",
    "Glimmering",
    "Glittering",
    "Strong-Willed",
    "Glowing",
    "Radiating",
    "Resolute",
    "Pulsing",
    "Seething",
    "Fearless",
    "Seething",
    "Fearless",
    "Blazing",
    "Blazing",
    "Dauntless",
    "Scintillating",
    "Scintillating",
    "Dauntless",
    "Incandescent",
    "Incandescent",
    "Indomitable",
    "Unconquerable",
    "Resplendent",
    "Resplendent",
    "Unassailable",
    "Pixie's",
    "Gremlin's",
    "Boggart's",
    "Naga's",
    "Djinn's",
    "Seraphim's",
    "Agile",
    "Shade's",
    "Dancer's",
    "Ghost's",
    "Acrobat's",
    "Spectre's",
    "Fleet",
    "Wraith's",
    "Blurred",
    "Blurred",
    "Phantasm's",
    "Phased",
    "Phased",
    "Nightmare's",
    "Nightmare's",
    "Mosquito's",
    "Moth's",
    "Butterfly's",
    "Wasp's",
    "Dragonfly's",
    "Perpetual",
    "Ample",
    "Cautious",
    "Sapping",
    "Caustic",
    "Panicked",
    "Seething",
    "Bubbling",
    "Catalysed",
    "Surgeon's",
    "Avenger's",
    "Recovering",
    "Inspiring",
    "Fletcher's",
    "Sharpshooter's",
    "Frost Weaver's",
    "Winterbringer's",
    "Flame Spinner's",
    "Lava Caller's",
    "Paragon's",
    "Thunder Lord's",
    "Tempest King's",
    "Combatant's",
    "Weaponmaster's",
    "Reanimator's",
    "Summoner's",
    "Protective",
    "Reinforced",
    "Shade's",
    "Strong-Willed",
    "Layered",
    "Ghost's",
    "Resolute",
    "Lobstered",
    "Spectre's",
    "Fearless",
    "Buttressed",
    "Wraith's",
    "Dauntless",
    "Thickened",
    "Phantasm's",
    "Pixie's",
    "Beetle's",
    "Mosquito's",
    "Gremlin's",
    "Crab's",
    "Moth's",
    "Boggart's",
    "Armadillo's",
    "Butterfly's",
    "Naga's",
    "Rhino's",
    "Wasp's",
    "Djinn's",
    "Elephant's",
    "Dragonfly's",
    "Thief's",
    "Magpie's",
    "Pirate's",
    "Looter's",
    "Dragon's",
    "Pillager's",
    "Healthy",
    "Sanguine",
    "Stalwart",
    "Stout",
    "Robust",
    "Rotund",
    "Virile",
    "Athlete's",
    "Fecund",
    "Vigorous",
    "Remora's",
    "Lamprey's",
    "Vampire's",
    "Beryl",
    "Cobalt",
    "Azure",
    "Sapphire",
    "Cerulean",
    "Aqua",
    "Opalescent",
    "Gentian",
    "Chalybeous",
    "Mazarine",
    "Blue",
    "Thirsty",
    "Parched",
    "Runner's",
    "Sprinter's",
    "Stallion's",
    "Gazelle's",
    "Cheetah's",
    "Chanter's",
    "Mage's",
    "Sorceror's",
    "Thaumaturgist's",
    "Wizard's",
    "Catalyzing",
    "Infusing",
    "Empowering",
    "Unleashed",
    "Frosted",
    "Chilled",
    "Icy",
    "Frigid",
    "Freezing",
    "Frozen",
    "Glaciated",
    "Polar",
    "Entombing",
    "Heated",
    "Smoldering",
    "Smoking",
    "Burning",
    "Flaming",
    "Scorching",
    "Incinerating",
    "Blasting",
    "Cremating",
    "Humming",
    "Buzzing",
    "Snapping",
    "Crackling",
    "Sparking",
    "Arcing",
    "Shocking",
    "Discharging",
    "Electrocuting",
    "Apprentice's",
    "Adept's",
    "Scholar's",
    "Professor's",
    "Occultist's",
    "Incanter's",
    "Glyphic",
    "Caster's",
    "Magician's",
    "Wizard's",
    "Warlock's",
    "Mage's",
    "Archmage's",
]

SUFFIXES = [
    "of Calm",
    "of Steadiness",
    "of Accuracy",
    "of Precision",
    "of the Sniper",
    "of the Marksman",
    "of the Deadeye",
    "of the Ranger",
    "of the Assassin",
    "of Shining",
    "of Light",
    "of Radiance",
    "of Skill",
    "of Ease",
    "of Mastery",
    "of Renown",
    "of Acclaim",
    "of Fame",
    "of Infamy",
    "of Grandmastery",
    "of Celebration",
    "of the Clouds",
    "of the Mongoose",
    "of the Pupil",
    "of the Brute",
    "of the Sky",
    "of the Lynx",
    "of the Student",
    "of the Wrestler",
    "of the Meteor",
    "of the Gazelle",
    "of the Prodigy",
    "of the Bear",
    "of the Comet",
    "of the Panther",
    "of the Augur",
    "of the Lion",
    "of the Heavens",
    "of the Leopard",
    "of the Gorilla",
    "of the Philosopher",
    "of the Galaxy",
    "of the Cheetah",
    "of the Sage",
    "of the Goliath",
    "of the Universe",
    "of the Jaguar",
    "of the Savant",
    "of the Leviathan",
    "of the Virtuoso",
    "of the Phantasm",
    "of the Titan",
    "of the Infinite",
    "of Talent",
    "of Nimbleness",
    "of Expertise",
    "of Legerdemain",
    "of Prestidigitation",
    "of Sortilege",
    "of Needling",
    "of Ire",
    "of Menace",
    "of Stinging",
    "of Anger",
    "of Havoc",
    "of Disaster",
    "of Piercing",
    "of Rage",
    "of Calamity",
    "of Puncturing",
    "of Fury",
    "of Penetrating",
    "of Ferocity",
    "of Ruin",
    "of Incision",
    "of Incision",
    "of Destruction",
    "of Destruction",
    "of Unmaking",
    "of Embers",
    "of Sparks",
    "of Snow",
    "of Coals",
    "of Static",
    "of Sleet",
    "of Ice",
    "of Cinders",
    "of Electricity",
    "of Rime",
    "of Flames",
    "of Voltage",
    "of Floe",
    "of Immolation",
    "of Discharge",
    "of Arcing",
    "of Glaciation",
    "of Ashes",
    "of Resolve",
    "of Fortitude",
    "of Will",
    "of Calm",
    "of Concentration",
    "of Focus",
    "of Study",
    "of Clear Mind",
    "of Fending",
    "of Iron Skin",
    "of Dousing",
    "of Heat",
    "of Reflexes",
    "of Gluttony",
    "of Craving",
    "of Animation",
    "of Adrenaline",
    "of Resistance",
    "of Steadiness",
    "of Staunching",
    "of Grounding",
    "of Refilling",
    "of Sipping",
    "of Savouring",
    "of Warding",
    "of Collecting",
    "of Plunder",
    "of Raiding",
    "of Gathering",
    "of Archaeology",
    "of Hoarding",
    "of Excavation",
    "of Amassment",
    "of Rejuvenation",
    "of Restoration",
    "of Regrowth",
    "of Nourishment",
    "of Success",
    "of Victory",
    "of Triumph",
    "of the Newt",
    "of the Lizard",
    "of the Starfish",
    "of the Hydra",
    "of the Troll",
    "of the Phoenix",
    "of Absorption",
    "of Osmosis",
    "of Consumption",
    "of Excitement",
    "of Joy",
    "of Elation",
    "of Bliss",
    "of Euphoria",
    "of Nirvana",
    "of Darting",
    "of Flight",
    "of Propulsion",
    "of the Zephyr",
    "of the Worthy",
    "of the Apt",
    "of the Inuit",
    "of the Whelpling",
    "of the Cloud",
    "of the Salamander",
    "of the Crystal",
    "of the Squall",
    "of the Seal",
    "of the Lost",
    "of the Drake",
    "of the Prism",
    "of the Storm",
    "of the Penguin",
    "of Banishment",
    "of the Kiln",
    "of the Kaleidoscope",
    "of the Thunderhead",
    "of the Yeti",
    "of Eviction",
    "of the Furnace",
    "of Variegation",
    "of the Tempest",
    "of the Walrus",
    "of Expulsion",
    "of the Polar Bear",
    "of the Volcano",
    "of the Maelstrom",
    "of the Rainbow",
    "of Exile",
    "of the Lightning",
    "of the Magma",
    "of the Ice",
    "of Intercepting",
    "of Walling",
    "of Impact",
    "of the Pugilist",
    "of Dazing",
    "of the Brawler",
    "of Stunning",
    "of the Boxer",
    "of Slamming",
    "of the Combatant",
    "of Staggering",
    "of the Gladiator",
    "of Thick Skin",
    "of Stone Skin",
    "of Iron Skin",
    "of Steel Skin",
    "of Adamantite Skin",
    "of Corundum Skin",
]

"""
list of unique item names, fetched from (currently 191)
http://pathofexile.gamepedia.com/List_of_unique_items

the following javascript extracts the names as an array

items = $("table.wikitable tbody tr td:first-child a:first-child")
items = items.map(function(i, a) {return $(a).text()})
copy($.makeArray(items).join("\n"))
"""

UNIQUES = [
    "The Anvil",
    "Araku Tiki",
    "Astramentis",
    "Atziri's Foible",
    "Carnage Heart",
    "Daresso's Salute",
    "Demigod's Presence",
    "Eye of Chayula",
    "The Ignomon",
    "Karui Ward",
    "Sidhebreath",
    "Stone of Lazhwar",
    "Victario's Acuity",
    "Voll's Devotion",
    "Auxium",
    "Headhunter",
    "Immortal Flesh",
    "The Magnate",
    "Meginord's Girdle",
    "Perandus Blazon",
    "Sunblast",
    "Wurm's Molt",
    "Andvarius",
    "Berek's Grip",
    "Berek's Pass",
    "Berek's Respite",
    "Blackheart",
    "Death Rush",
    "Doedre's Damning",
    "Dream Fragments",
    "Gifts from Above",
    "Kaom's Sign",
    "Le Heup of All",
    "Lori's Lantern",
    "Ming's Heart",
    "Perandus Signet",
    "Shavronne's Revelation",
    "The Taming",
    "Thief's Torment",
    "Blackgleam",
    "Broadstroke",
    "Ambu's Charge",
    "Ashrend",
    "Bramblejack",
    "Bronn's Lithe",
    "Carcass Jack",
    "Cloak of Flame",
    "Cloak of Defiance",
    "The Covenant",
    "Death's Oath",
    "Foxshade",
    "Hyrri's Ire",
    "Icetomb",
    "Infernal Mantle",
    "Kaom's Heart",
    "Lightbane Raiment",
    "Lightning Coil",
    "Shavronne's Wrappings",
    "Soul Mantle",
    "Tabula Rasa",
    "Thousand Ribbons",
    "Voll's Protector",
    "Zahndethus' Cassock",
    "The Blood Dance",
    "Bones of Ullr",
    "Darkray Vectors",
    "Deerstalker",
    "Demigod's Stride",
    "Goldwyrm",
    "Lioneye's Paws",
    "Ondar's Flight",
    "Rainbowstride",
    "Shavronne's Pace",
    "Sin Trek",
    "Sundance",
    "Wake of Destruction",
    "Wanderlust",
    "Windscream",
    "Wondertrap",
    "Asenath's Gentle Touch",
    "Aurseize",
    "Deshret's Vise",
    "Doedre's Tenure",
    "Facebreaker",
    "Voidbringer",
    "Hrimsorrow",
    "Lochtonial Caress",
    "Maligaro's Virtuosity",
    "Ondar's Clasp",
    "Sadima's Touch",
    "Slitherpinch",
    "Thunderfist",
    "Abyssus",
    "Alpha's Howl",
    "Asenath's Mark",
    "The Bringer of Rain",
    "Chitus' Apex",
    "Crown of Thorns",
    "Deidbell",
    "Demigod's Triumph",
    "Devoto's Devotion",
    "Ezomyte Peak",
    "Fairgraves' Tricorne",
    "Geofri's Crest",
    "Goldrim",
    "The Gull",
    "Heatshiver",
    "Honourhome",
    "Hrimnor's Resolve",
    "Leer Cast",
    "Malachai's Simula",
    "Mindspiral",
    "The Peregrine",
    "Rat's Nest",
    "Rime Gaze",
    "Starkonja's Head",
    "Aegis Aurora",
    "Atziri's Mirror",
    "Chernobog's Pillar",
    "Crest of Perandus",
    "Daresso's Courage",
    "Kaltenhalt",
    "Lioneye's Remorse",
    "Matua Tupuna",
    "Prism Guardian",
    "Rathpith Globe",
    "Rise of the Phoenix",
    "Saffell's Frame",
    "Springleaf",
    "Titucius' Span",
    "Soul Taker",
    "Dyadus",
    "The Blood Reaper",
    "Kaom's Primacy",
    "Limbsplit",
    "Reaper's Pursuit",
    "Wideswing",
    "Chin Sol",
    "Darkscorn",
    "Death's Harp",
    "Infractem",
    "Lioneye's Glare",
    "Quill Rain",
    "Silverbranch",
    "Storm Cloud",
    "Voltaxic Rift",
    "Al Dhih",
    "Bloodseeker",
    "Cybil's Paw",
    "Essentia Sanguis",
    "Last Resort",
    "Mortem Morsu",
    "Divinarius",
    "Heartbreaker",
    "Mightflay",
    "Ungil's Gauche",
    "Brightbeak",
    "Mon'tregul's Grasp",
    "Nycta's Lantern",
    "The Supreme Truth",
    "Chober Chaber",
    "Geofri's Baptism",
    "Hrimnor's Hymn",
    "Kongor's Undying Rage",
    "Marohi Erqi",
    "Quecholli",
    "Voidhome",
    "Aurumvorax",
    "Ephemeral Edge",
    "Rebuke of the Vaal",
    "Redbeak",
    "The Goddess Bound",
    "The Goddess Scorned",
    "Queen's Decree",
    "Rigvald's Charge",
    "Shiversting",
    "Terminus Est",
    "Pillar of the Caged God",
    "The Searing Touch",
    "Taryn's Shiver",
    "Midnight Bargain",
    "Moonsorrow",
    "Void Battery",
    "Blood of the Karui",
    "Divination Distillate",
    "Lavianga's Spirit",
    "Acton's Nightmare",
    "The Coward's Trial",
    "Maelström of Chaos",
    "Poorjoy's Asylum",
    "Vaults of Atziri",
]

#normalize to lower case
#cast to tuple for easy application for startswith and endswith
PREFIXES = tuple([norm(x) for x in PREFIXES])
SUFFIXES = tuple([norm(x) for x in SUFFIXES])
UNIQUES = tuple([norm(x) for x in UNIQUES])
