import csv
import re
from decimal import Decimal


class RateProvider(object):
    """Base class for a provider of poe exchange rates"""
    csv_filename = ""
    headers = ""

    def __init__(self):
        fp = open(self.csv_filename)
        self.rows = list(csv.reader(fp))
        self.columns = []
        # normalize the headets
        for h in self.headers.strip().lower().splitlines():
            h = h.replace("orb", "").replace("of", "").replace("'", "").strip()
            self.columns.append(h)

    def __str__(self):
        raise NotImplementedError

    def norm_orb(self, s):
        """returns the orb given a fuzzy search string"""
        # strip plurals
        s = s.rstrip("s")

        # hangle common exceptional abbreviations
        if s == "c":
            return "chaos"
        if s == "gcp":
            return "gemcutters prism"
        if s.startswith("fuse"):
            return "fusing"
        if s.startswith("chrome"):
            return "chromatic"
        if s.startswith("chi"):
            return "cartographers chisel"

        # look for orbs that start with the given input
        res = [c for c in self.columns if c.startswith(s)]
        if not res:
            raise LookupError("No matches found for '%s'." % s)
        elif len(res) == 1:
            return res[0]
        else:
            raise LookupError(">1 orbs found for '%s'" % s)

    def rate(self, from_orb, to_orb):
        """
        returns the rate from the poerates spreadsheet
        assumes that from_orb and to_orb have both been normalized
        """
        from_orb = self.norm_orb(from_orb)
        to_orb = self.norm_orb(to_orb)

        # noop
        if from_orb == to_orb:
            return Decimal(1)

        row_no = self.columns.index(from_orb) + 1
        col_no = self.columns.index(to_orb) + 1
        ratio = self.rows[row_no][col_no].replace(" ", "").split(":")
        a, b = [Decimal(n.replace(",", ".")) for n in ratio]
        return a / b


class PoeRatesProvider(RateProvider):
    """Rates provider for http://tinyurl.com/poerates/"""
    csv_filename = "poerates.csv"
    headers = """
        Chromatic Orb
        Orb of Alteration
        Jeweller's Orb
        Orb of Chance
        Cartographer's Chisel
        Orb of Fusing
        Alchemy Orb
        Orb of Scouring
        Blessed Orb
        Chaos Orb
        Orb of Regret
        Vaal Orb
        Regal Orb
        Gemcutter's Prism
        Divine Orb
    """

    def __str__(self):
        return "PoE Rates"


class PoeExProvider(RateProvider):
    """Rates provider for http://www.poeex.info/"""
    csv_filename = "poeex.csv"
    headers = """
        Chromatic Orb
        Orb of Alteration
        Jeweller's Orb
        Orb of Chance
        Cartographer's Chisel
        Orb of Fusing
        Orb of Alchemy
        Orb of Scouring
        Blessed Orb
        Chaos Orb
        Orb of Regret
        Regal Orb
        Gemcutter's Prism
        Divine Orb
        Exalted Orb
        Eternal Orb
        Vaal Orb
    """

    def __str__(self):
        return "PoE Ex"


def norm_low_orbs(match):
    """
    handles the lower orbs (transmutations and augmentations) which are not in
    the rates tables, but the vendor rates can be used

    takes a match object from the parsed rate string
    """
    if match["from_orb"].startswith("aug"):
        match["from_orb"] = "alt"
        match["from_rate"] = match["from_rate"] / 4
    elif match["from_orb"].startswith("tran"):
        match["from_orb"] = "alt"
        match["from_rate"] = match["from_rate"] / 16

    if match["to_orb"].startswith("aug"):
        match["to_orb"] = "alt"
        match["to_rate"] = match["to_rate"] / 4
    elif match["to_orb"].startswith("tran"):
        match["to_orb"] = "alt"
        match["to_rate"] = match["to_rate"] / 16

    return match


def parse_rate_str(s):
    """
    returns a dict with the following keys: txn, to_orb, from_rate, from_orb,
    to_rate, rate raises a NotFound exception otherwise
    """
    DEC_RE = r"(\d+(.\d+)?)?"  # qty is optional, defaults to 1
    SPACE_RE = r"[\s:=]*"
    s = s.lower()
    s = s.replace("for", "")
    s = re.sub(r"\s*:\s*", " ", s)

    CONV_RE = re.compile(r"""
        (?P<txn>(wtb|wtt|wte|wts))
        {1}
        (?P<from_rate>{0})
        {1}
        (?P<from_orb>\w+)
        {1}
        (?P<to_rate>{0})
        \s*(?P<to_orb>\w+)
    """.format(DEC_RE, SPACE_RE), re.X)

    m = CONV_RE.match(s)
    if m is None:
        raise LookupError("Invalid rate string.")
    m = m.groupdict()

    # the qtys are optional, defaults to 1
    m["from_rate"] = Decimal(m["from_rate"] or 1)
    m["to_rate"] = Decimal(m["to_rate"] or 1)

    # wts is the other direction
    if m["txn"] == "wtb":
        m["from_orb"], m["to_orb"] = m["to_orb"], m["from_orb"]
        m["from_rate"], m["to_rate"] = m["to_rate"], m["from_rate"]

    # handle low orbs augmentation and transmutations
    m = norm_low_orbs(m)

    m["rate"] = m["from_rate"] / m["to_rate"]
    return m


if __name__ == "__main__":
    d = parse_rate_str("wtb 540 alt 1 ex")

    given_rate = d["rate"]
    for provider in (PoeRatesProvider(), PoeExProvider()):
        actual_rate = provider.rate(d["from_orb"], d["to_orb"])

        print str(provider).lower()
        print "Actual rate: %s" % actual_rate
        percent = (given_rate - actual_rate) / actual_rate * 100
        if percent < 0:
            print "Loss: %.2f%%" % (-percent)
        else:
            print "Profit: %.2f%%" % percent
        print
