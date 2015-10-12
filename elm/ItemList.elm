module ItemList where

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Json.Decode as Json exposing ((:=))
import Signal exposing (Address)
import Task exposing (..)

import Debug
import Http
import StartApp.Simple as StartApp

-- MODEL

{-
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
-}

type alias Model =
    {}

initialModel : Model
initialModel =
    {}

-- UPDATE

type Action
  = NoOp

update : Action -> Model -> Model
update action model =
  case action of
    NoOp ->
      model

-- VIEW

view : Address Action -> Model -> Html
view address model =
  h1
    []
    [ text "Hello World!" ]

-- WIRE THE APP TOGETHER!

main =
  StartApp.start
    { model = initialModel,
      view = view,
      update = update
    }
