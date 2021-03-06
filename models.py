import hashlib

from sqlalchemy import types, true, false
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.databases import postgres

from app import db
import constants
from utils import norm, normfind, get_constant

GEMS = get_constant("GEMS", as_dict=True)


class tsvector(types.TypeDecorator):
    """
    using tsvectors for full text search in sqlalchemy, custom type definition

    http://stackoverflow.com/questions/13837111/
    """
    impl = types.UnicodeText


@compiles(tsvector, 'postgresql')
def compile_tsvector(element, compiler, **kw):
    return 'tsvector'


def in_page_group(group_name):
    premium_pages = Location.query.filter(
        Location.is_premium,
        Location.is_character == false(),
        ~Location.name.like("% (Remove-only)"),
        ~Location.name.op("~")(r"\d+"),  # page name shouldn't be an int
    ).order_by(Location.page_no).all()

    # longest non premium range are the rares
    grp_name = group_name.lower()
    for curr, nxt in zip(premium_pages, premium_pages[1:]):
        if curr.name.lower() == grp_name:
            return (Location.page_no >= curr.page_no,
                    Location.page_no < nxt.page_no)
    else:
        # is it the last premium page
        last = premium_pages[-1]
        if last.name.lower() == grp_name:
            return (Location.page_no >= last.page_no,)

    raise IndexError("'%s' group not found." % group_name)


class Item(db.Model):
    """
    Model representing an item
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(255), nullable=False)
    # x, y can be null for equipped or socketed items
    x = db.Column(db.SmallInteger())
    y = db.Column(db.SmallInteger())
    w = db.Column(db.SmallInteger(), nullable=False, default=1)
    h = db.Column(db.SmallInteger(), nullable=False, default=1)
    rarity = db.Column(db.Enum('normal', 'magic', 'rare', 'unique',
                                name='rarities'))
    icon = db.Column(db.String(500))
    num_sockets = db.Column(db.SmallInteger(), nullable=False, default=0)
    socket_str = db.Column(db.String(20), nullable=False, default="")
    is_identified = db.Column(db.Boolean, nullable=False, default=True)
    char_location = db.Column(db.String(20))
    full_text = db.Column(tsvector, nullable=False)
    is_corrupted = db.Column(db.Boolean, nullable=False, default=False)
    # or marking the item as deleted
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    league = db.Column(db.String(20), default="Standard")

    # funky stuff for item properties, mods etc
    mods = db.relationship("Modifier", backref="item", lazy="dynamic")
    requirements = db.relationship("Requirement", backref="item",
                                   lazy="dynamic")
    properties = db.relationship("Property", backref="item", lazy="dynamic")
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    # socketed items use these for the parent item
    parent_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    parent_item = db.relationship('Item', remote_side=[id],
                                  backref="socketed_items")

    def __repr__(self):
        if self.name:
            return "%s %s" % (self.name, self.type)
        else:
            return self.type

    @property
    def image_url(self):
        _, _, query = self.icon.rpartition("?")
        sha = hashlib.sha1(self.icon).hexdigest()
        return "images/full/%s.png?%s" % (sha, query)

    @property
    def implicit_mods(self):
        return self.mods.filter(Modifier.is_implicit == true()).all()

    @property
    def explicit_mods(self):
        return self.mods.filter(Modifier.is_implicit == false()).all()

    @property
    def numeric_mods(self):
        return self.mods.filter(
            Modifier.original != Modifier.normalized
        ).all()

    @db.validates('num_sockets')
    def validate_num_sockets(self, key, num_sockets):
        assert 0 <= num_sockets <= 6
        return num_sockets

    @db.validates('x')
    def validate_x(self, key, x):
        assert x is None or x >= 0
        return x

    @db.validates('y')
    def validate_y(self, key, y):
        assert y is None or y >= 0
        return y

    @db.validates('w')
    def validate_w(self, key, w):
        assert 1 <= w <= 2
        return w

    @db.validates('h')
    def validate_h(self, key, h):
        assert 1 <= h <= 4, h
        return h

    # various helpers for the model
    def is_gem(self):
        for p in self.properties:
            if p.name == "Experience":
                return True
        return False

    def is_quest_item(self):
        return norm(self.type).startswith(constants.QUEST_ITEMS)

    @property
    def identified(self):
        return self.query.filter(self.is_identified)

    def location_str(self):
        """Outputs a nicely formatted location string"""
        ret = "%s: " % str(self.location)
        if self.char_location:
            ret += self.char_location
        elif self.x is not None:
            ret += "(%s, %s)" % (self.x, self.y)
        if self.parent_item:
            ret += " [Socketed]"
        return ret

    def gem_color(self):
        """
        returns the letter for the color of the gem, if the item is not a gem,
        raises ValueError
        """
        for p in self.properties:
            if p.name == "Experience":
                break
        else:
            raise ValueError("Item is not a gem.")
        return normfind(GEMS, self.type)["color"]

    def item_group(self):
        """returns the major item grouping for an item, e.g. mace, armor etc"""
        own_type = self.type.lower()
        for g in ("axes", "bows", "claws", "daggers", "maces", "staves",
                  "swords", "wands", "helms", "armors", "gloves", "boots",
                  "shields", "belts", "quivers"):
            for k, v in get_constant(g.upper(), as_dict=True).items():
                if k.lower() in own_type:
                    # see if there is a subtype
                    if isinstance(v, str):
                        return g.title()
                    else:
                        return v.get("subtype", g.title())
        raise ValueError("%s is not a recognized item type." % self.type)

    @property
    def required_level(self):
        """
        convenience property that returns the required level for the item,
        None otherwise
        """
        for req in self.requirements:
            if req.name == "Level":
                return int(req.value)
        return None


class Property(db.Model):
    """Model representing a single property of an item"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))


class Requirement(db.Model):
    """Model representing a single requirement of an item"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.SmallInteger(), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))


class Modifier(db.Model):
    """Model representing a single modifier of an item"""
    id = db.Column(db.Integer, primary_key=True)

    # value = db.Column(db.String(255), nullable=False)
    # normalized = db.Column(db.String(255), nullable=False)

    # original mod text
    original = db.Column(db.String(255), nullable=False)
    normalized = db.Column(db.String(255), nullable=False)
    # numeric values (if any)
    values = db.Column(postgres.ARRAY(db.Float(asdecimal=True)))
    is_implicit = db.Column(db.Boolean, nullable=False, default=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))

    def __str__(self):
        return self.original

    def __repr__(self):
        return self.original


class Location(db.Model):
    """
    Model representing the location of an item, which might be a stash page
    or a character
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    page_no = db.Column(db.SmallInteger())
    is_premium = db.Column(db.Boolean, nullable=False, default=False)
    is_character = db.Column(db.Boolean, nullable=False, default=False)
    items = db.relationship("Item", backref="location")

    def __str__(self):
        if self.is_character:
            return self.name
        return "Stash: %s" % self.name

    def __repr__(self):
        return self.__str__()
