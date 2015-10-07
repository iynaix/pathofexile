from flask.ext.restful import Resource, fields, marshal_with
from app import db
from models import Item, Location


requirement_fields = dict(
    name=fields.String,
    value=fields.Integer(default=None),
)

property_fields = dict(
    name=fields.String,
    value=fields.String(default=None),
)

modifier_fields = dict(
    original=fields.String,
    is_implicit=fields.Boolean,
)

location_fields = dict(
    id=fields.Integer,
    name=fields.String,
    page_no=fields.Integer,
    is_premium=fields.Boolean,
    is_character=fields.Boolean,
    location_str=fields.String(attribute=lambda x: str(x)),
)

item_fields = dict(
    name=fields.String,
    type=fields.String,
    x=fields.Integer(default=None),
    y=fields.Integer(default=None),
    w=fields.Integer,
    h=fields.Integer,
    rarity=fields.String,
    image_url=fields.String,
    num_sockets=fields.Integer,
    socket_str=fields.String,
    is_identified=fields.Boolean,
    char_location=fields.String,
    # full_text=fields.String,
    is_corrupted=fields.Boolean,
    is_deleted=fields.Boolean,
    league=fields.String,
    # relationships
    implicit_mods=fields.List(fields.Nested(modifier_fields)),
    explicit_mods=fields.List(fields.Nested(modifier_fields)),
    requirements=fields.List(fields.Nested(requirement_fields)),
    properties=fields.List(fields.Nested(property_fields)),
    location=fields.Nested(location_fields),

    # # socketed items use these for the parent item
    # parent_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    # parent_item = db.relationship('Item', remote_side=[id],
    #                               backref="socketed_items")
)


class ItemResource(Resource):
    @marshal_with(item_fields)
    def get(self, item_id):
        return Item.query.filter(
            Item.id == item_id,
        ).first()


class ItemListResource(Resource):
    @marshal_with(item_fields)
    def get(self, **kwargs):
        return Item.query.filter(
            Item.socket_str != "",
        ).all()[:20]


class LocationResource(Resource):
    @marshal_with(item_fields)
    def get(self, slug):
        loc = Location.query.filter(
            db.func.lower(Location.name) == slug.lower()
        ).one()
        return Item.query.filter(Item.location == loc).order_by(
            Item.x, Item.y
        ).all()


class LocationListResource(Resource):
    @marshal_with(location_fields)
    def get(self, **kwargs):
        return Location.query.order_by(
            Location.is_character,
            Location.page_no,
        ).all()
