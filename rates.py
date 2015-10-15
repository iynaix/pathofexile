import csv
import re


CURRENCIES = (
    "Chromatic",
    "Alteration",
    "Jeweller's",
    "Chance",
    "Cartographer's Chisel",
    "Fusing",
    "Alchemy",
    "Scouring",
    "Blessed",
    "Chaos",
    "Regret",
    "Vaal",
    "Regal",
    "Gemcutter's Prism",
    "Divine",
    "Exalted",
)
CURRENCIES = [c.lower().replace("'", "") for c in CURRENCIES]


def get_poe_rates():
    rates = []
    with open('poerates.csv') as fp:
        reader = csv.reader(fp)
        reader.next()
        for row_no, row in enumerate(reader):
            from_orb = CURRENCIES[row_no]
            for to_orb, cell in zip(CURRENCIES, row[1:]):
                rate, _ = [float(n.strip()) for n in cell.split(":")]
                print "%s is %s %s" % (to_orb, rate, from_orb)


s = "14 alts for : 1.5c"
DEC_RE = r"\d+(.\d+)?"
s = re.sub(r"\s*for\s*", " ", s)
s = re.sub(r"\s*:\s*", " ", s)

a = re.compile(r"""(?P<from_rate>\d+(.\d+)?)
                   \s*
                   (?P<from_orb>\w+)
                   \s*
                   (?P<to_rate>\d+(.\d+)?)
                   \s*(?P<to_orb>\w+)""",
               re.X)

print a.match(s).groupdict()
