module Rates where

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


ratesHtml : Html
ratesHtml =
    Html.form
        []
        [ div
            [ class "form-group" ]
            [ input
                [ type' "email",
                  class "form-control input-lg text-center",
                  placeholder "e.g. wtb 500 alts 1 ex" ]
                []
            ]
        ]



view : Signal.Address Action -> Model -> Html
view address model =
    ratesHtml


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
