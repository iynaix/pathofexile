module ItemList where

import Effects exposing (Effects, Never)
import Html exposing (..)
import Html.Events exposing (..)
import Html.Attributes exposing (..)
import Html.Shorthand exposing (..)
import Task exposing (..)

import StartApp

-- Utilities for working with PoE items
import Item exposing (..)

-- MODEL

type alias Model =
    { items : Items
    }


init : (Model, Effects Action)
init =
    let
        fetchPage url =
            fetchItems url
                |> Task.toMaybe
                |> Task.map NewItems
                |> Effects.task
    in
        ( { items = [] },
          (fetchPage "/api/locations/rare")
        )


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
