module ItemList where

import Effects exposing (Effects, Never)
import Html exposing (..)
import Html.Events exposing (..)
import Html.Attributes exposing (..)
import Html.Shorthand exposing (..)
import Json.Decode as Json exposing ((:=))
import Task exposing (..)

import Char
import String
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
      value: Int
    }


type alias Property =
    { name : String,
      value: String
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
      is_character : Bool
    }


type alias Item =
    { name : String,
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
      league : String,

      -- relationships
      requirements: List Requirement,
      properties: List Property,
      implicit_mods: List Modifier,
      explicit_mods: List Modifier
      -- location: Location

      -- socketed items use these for the parent item
      -- parent_id = db.Column(db.Integer, db.ForeignKey('item.id'))
      -- parent_item = db.relationship('Item', remote_side=[id],
      --                               backref="socketed_items")
}


-- MODEL

type alias Properties = List Property
type alias Modifiers = List Modifier
type alias Requirements = List Requirement
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


nbsp : Html
nbsp =
    Char.fromCode 160 |> String.fromChar |> text


-- Appends a hr if list is not empty
addHr : List Html -> List Html
addHr arr =
    (case arr of
        [] ->  []
        _ -> List.append arr [hr_]
    )



rarityClass : String -> String
rarityClass rarity =
    case rarity of
        "gem" -> "gem"
        "quest" -> "quest"
        "magic" -> "magic"
        "rare" -> "rare"
        "unique" -> "unique"
        _ -> "normal"


raritySpan: String -> String -> List Html
raritySpan rarity txt =
    case txt of
        "" ->
            []
        _ ->
            [ span
                [ class (rarityClass rarity) ]
                [ text txt ]
            ]


sockets : String -> List Html
sockets socket_str =
    let
        socket c =
            case c of
                'B' ->
                    span [ class "label label-primary" ] [ nbsp ]
                'G' ->
                    span [ class "label label-success" ] [ nbsp ]
                'R' ->
                    span [ class "label label-danger" ] [ nbsp ]
                _ ->
                    nbsp
    in
        case socket_str of
            "" ->
                []
            s ->
                [ span
                     [ style [ ("margin-left", "2em") ] ]
                     ( s |> String.toList |> List.map socket ) ]


itemHeader : Item -> List Html
itemHeader item =
    (raritySpan item.rarity item.name) ++
    (if item.name == "" then [] else [ br' ]) ++
    (raritySpan item.rarity item.type_) ++
    (sockets item.socket_str)


itemReqs : Requirements -> List Html
itemReqs reqs =
    let
        reqClass req =
            req.name |> String.left 3 |> String.toLower
        itemReq req =
            span
                [ style [ ("margin-right", "0.25em") ],
                  class (reqClass req)
                ]
                [ text (req.name ++ ": " ++ (toString req.value)) ]
    in
        (List.map itemReq reqs)


itemProps : Properties -> List Html
itemProps props =
    let
        propText prop =
            if prop.value == "" then prop.name else prop.name ++ ": " ++ prop.value
        itemProp prop =
            [ span_ [ text (propText prop) ],
              br'
            ]
    in
        (List.concatMap itemProp props)


itemMods : Modifiers -> List Html
itemMods mods =
    let
        itemMod mod =
            [ span
                [ class "magic" ]
                [ text mod.original ],
              br'
            ]
    in
        (List.concatMap itemMod mods)


itemImage : Item -> Html
itemImage item =
    img
        [ src item.image_url,
          alt item.type_
        ]
        []


itemInfo: Item -> Html
itemInfo item =
    case item.is_identified of
        False ->
            p
                [ class "unindentified" ]
                [ text "Unidentified" ]
        True ->
            div
                [ style [ ("margin-top", "0.5em") ] ]
                ( List.concat [
                    ((itemReqs item.requirements) |> addHr),
                    ((itemProps item.properties) |> addHr),
                    ((itemMods item.implicit_mods) |> addHr),
                    ((itemMods item.explicit_mods))
                  ] )


itemHtml : Item -> Html
itemHtml item =
    li
        [ class "list-group-item" ]
        ( [ h4
                [ classList [ ("unidentified", not item.is_identified) ] ]
                (itemHeader item),
            itemImage item,
            itemInfo item
          -- text (toString item)
          ]
        )


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


decodeRequirement : Json.Decoder Requirement
decodeRequirement =
    Json.object2 Requirement
        ("name" := Json.string)
        ("value" := Json.int)


decodeProperty : Json.Decoder Property
decodeProperty =
    Json.object2 Property
        ("name" := Json.string)
        ("value" := Json.string)


decodeModifier : Json.Decoder Modifier
decodeModifier =
    Json.object2 Modifier
        ("original" := Json.string)
        ("is_implicit" := Json.bool)


decodeItem : Json.Decoder Item
decodeItem =
    Json.map Item ("name" := Json.string)
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
        -- related fields
        `apply` ("requirements" := Json.list decodeRequirement )
        `apply` ("properties" := Json.list decodeProperty )
        `apply` ("implicit_mods" := Json.list decodeModifier )
        `apply` ("explicit_mods" := Json.list decodeModifier )


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
