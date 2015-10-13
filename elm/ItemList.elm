module ItemList where

import Effects exposing (Effects, Never)
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Json.Decode as Json exposing ((:=))
import Task exposing (..)

import Debug
import Http
import StartApp

-- Utility functions

-- Decoding large json objects
-- http://www.troikatech.com/blog/2015/08/17/decoding-larger-json-objects-in-elm
-- https://groups.google.com/forum/m/#!topic/elm-discuss/2LxEUVe0UBo
apply : Json.Decoder (a -> b) -> Json.Decoder a -> Json.Decoder b
apply func value =
    Json.object2 (<|) func value


-- MODEL

type alias Requirement =
    { name : String,
      value: Maybe Int
    }


type alias Property =
    { name : String,
      value: Maybe String
    }


type alias Modifier =
    { original : String,
      is_implicit : Bool
    }


type alias Location =
    { id : Int,
      name : String,
      page_no : Int,
      is_premium : Bool,
      is_character : Bool,
      location_str : String
    }


type alias Item =
    { name : Maybe String,
      type_ : String,
      x : Maybe Int,
      y : Maybe Int,
      w : Int,
      h : Int,
      rarity : String,
      image_url : String,
      num_sockets : Int,
      socket_str : String,
      is_identified : Bool,
      char_location : Maybe String,
      is_corrupted : Bool,
      is_deleted : Bool,
      league : String

      -- relationships
      -- implicit_mods: List Modifier,
      -- explicit_mods: List Modifier,
      -- requirements: List Requirement,
      -- properties: List Property,
      -- location: Location

      -- socketed items use these for the parent item
      -- parent_id = db.Column(db.Integer, db.ForeignKey('item.id'))
      -- parent_item = db.relationship('Item', remote_side=[id],
      --                               backref="socketed_items")
}


-- MODEL

type alias Items = List Item

type alias Model =
    { items : Items
    }


init : (Model, Effects Action)
init =
    ( { items = [] }, fetchItems )


-- UPDATE

type Action
    = NewItems (Maybe Items)


update : Action -> Model -> (Model, Effects Action)
update action model =
    case action of
        NewItems items ->
            ( { items = Maybe.withDefault [] items }
            , Effects.none
            )


-- VIEW

type alias NodeFunc = List Attribute -> List Html -> Html

itemLocation : NodeFunc -> Item -> Html
itemLocation outertag item =
    outertag
        []
        [ a
            [ href "itemlocation" ]
            [ text "item location" ]
        ]



itemImage : Item -> Html
itemImage item =
    img
        [ src item.image_url,
          alt item.type_
        ]
        []


itemHtml : Item -> Html
itemHtml item =
    li
        [ class "list-group-item" ]
        [ itemLocation h4 item,
          itemImage item
          -- text (toString item)
        ]


view : Signal.Address Action -> Model -> Html
view address model =
    ul
        [ class "list-group item_listing" ]
        (List.map itemHtml model.items)


-- EFFECTS


fetchItems : Effects Action
fetchItems =
  Http.get (Json.list decodeItem) "/api/locations/rare"
    |> Task.toMaybe
    |> Task.map NewItems
    |> Effects.task


decodeItem : Json.Decoder Item
decodeItem =
    Json.map Item ("name" := Json.maybe Json.string)
        `apply` ("type_" := Json.string)
        `apply` ("x" := Json.maybe Json.int)
        `apply` ("y" := Json.maybe Json.int)
        `apply` ("w" := Json.int)
        `apply` ("h" := Json.int)
        `apply` ("rarity" := Json.string)
        `apply` ("image_url" := Json.string)
        `apply` ("num_sockets" := Json.int)
        `apply` ("socket_str" := Json.string)
        `apply` ("is_identified" := Json.bool)
        `apply` ("char_location" := Json.maybe Json.string)
        `apply` ("is_corrupted" := Json.bool)
        `apply` ("is_deleted" := Json.bool)
        `apply` ("league" := Json.string)


app =
    StartApp.start
        { init = init
        , update = update
        , view = view
        , inputs = []
        }


main =
    app.html


-- Kickstart the initial fetch
port tasks : Signal (Task.Task Never ())
port tasks =
    app.tasks
