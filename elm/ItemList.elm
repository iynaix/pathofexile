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
    { -- name : String,
      -- type_ : String,
      -- x : Maybe Int,
      -- y : Maybe Int,
      -- w : Int
      -- h : Int,
      -- rarity : String,
      image_url : String
      -- num_sockets : Int,
      -- socket_str : String,
      -- is_identified : Bool,
      -- char_location : String,
      -- is_corrupted : Bool,
      -- is_deleted : Bool,
      -- league : String

      -- -- relationships
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

type alias Model =
    { gifUrl : String
    }


init : (Model, Effects Action)
init =
  ( Model "http://placehold.it/350x150"
  , getRandomGif
  )


-- UPDATE

type Action
    = NewGif (Maybe String)


update : Action -> Model -> (Model, Effects Action)
update action model =
  case action of
    NewGif maybeUrl ->
      ( Model (Maybe.withDefault model.gifUrl maybeUrl)
      , Effects.none
      )


-- VIEW

(=>) = (,)


view : Signal.Address Action -> Model -> Html
view address model =
    img
        [src model.gifUrl]
        []


-- EFFECTS

getRandomGif : Effects Action
getRandomGif =
  Http.get decodeUrl (randomUrl)
    |> Task.toMaybe
    |> Task.map NewGif
    |> Effects.task


randomUrl : String
randomUrl =
  Http.url "http://api.giphy.com/v1/gifs/random"
    [ "api_key" => "dc6zaTOxFJmzC"
    , "tag" => "funny cats"
    ]


decodeUrl : Json.Decoder String
decodeUrl =
  Json.at ["data", "image_url"] Json.string

app =
    StartApp.start
        { init = init
        , update = update
        , view = view
        , inputs = []
        }

main =
    app.html


port tasks : Signal (Task.Task Never ())
port tasks =
    app.tasks
