from sqlalchemy.dialects import postgres
from app import db
from affixes import QUEST_ITEMS
from utils import norm


class Item(db.Model):
    """
    Model representing an item
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(255), nullable=False)
    x = db.Column(db.SmallInteger(), nullable=False, default=0)
    y = db.Column(db.SmallInteger(), nullable=False, default=0)
    w = db.Column(db.SmallInteger(), nullable=False, default=1)
    h = db.Column(db.SmallInteger(), nullable=False, default=1)
    rarity = db.Column(db.Enum('normal', 'magic', 'rare', 'unique',
                                name='rarities'))
    num_sockets = db.Column(db.SmallInteger(), nullable=False, default=0)
    socket_str = db.Column(db.String(20), nullable=False, default="")

    #funky stuff for item properties, mods etc
    # properties = db.Column(postgres.HSTORE())
    mods = db.Column(postgres.ARRAY(db.String))
    requirements = db.relationship("Requirement", backref="item",
                                   lazy="joined")
    properties = db.relationship("Property", backref="item",
                                lazy="joined")
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    def __repr__(self):
        return self.name + self.type

    @db.validates('num_sockets')
    def validate_num_sockets(self, key, num_sockets):
        assert 0 <= num_sockets <= 6, num_sockets
        return num_sockets

    @db.validates('x')
    def validate_x(self, key, x):
        assert 0 <= x <= 11, x
        return x

    @db.validates('y')
    def validate_y(self, key, y):
        assert 0 <= y <= 11, y
        return y

    @db.validates('w')
    def validate_w(self, key, w):
        assert 1 <= w <= 2, w
        return w

    @db.validates('h')
    def validate_h(self, key, h):
        assert 1 <= h <= 4, h
        return h

    #various helpers for the model
    def is_gem(self):
        for p in self.properties:
            if p.name == "Experience":
                return True
        return False

    def is_quest_item(self):
        return norm(self.type).startswith(QUEST_ITEMS)

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


class Property(db.Model):
    """
    Model representing a single property of an item
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))


class Requirement(db.Model):
    """
    Model representing a single requirement of an item
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.SmallInteger(), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))


class Location(db.Model):
    """
    Model representing the location of an item, which might be a stash page
    or a character
    """
    def __str__(self):
        if self.is_character:
            return self.name
        out = "Stash %s" % self.page_no
        if self.is_premium:
            out += " (%s)" % self.name
        return out

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    page_no = db.Column(db.SmallInteger())
    is_premium = db.Column(db.Boolean, nullable=False, default=False)
    is_character = db.Column(db.Boolean, nullable=False, default=False)
    items = db.relationship("Item", backref="location", lazy="joined")
