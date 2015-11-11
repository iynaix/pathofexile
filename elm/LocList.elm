module LocList where

import Effects exposing (Effects, Never)
import Html exposing (..)
import Html.Events exposing (..)
import Html.Attributes exposing (..)
import Html.Shorthand exposing (..)
import Task exposing (..)
import String

-- Utilities for working with PoE items
import Item exposing (Location, Locations, fetchLocations)

import StartApp

-- MODEL

type alias Model =
    { locations : Locations
    }


init : (Model, Effects Action)
init =
    let
        fetchPage url =
            fetchLocations url
                |> Task.toMaybe
                |> Task.map NewLocations
                |> Effects.task
    in
        ( { locations = [] },
          (fetchPage "/api/locations")
        )


-- UPDATE


type Action
    = NewLocations (Maybe Locations)


update : Action -> Model -> (Model, Effects Action)
update action model =
    case action of
        NewLocations locs ->
            ( { locations = Maybe.withDefault [] locs }
            , Effects.none
            )


-- orderLocations : Locations -> Locations
orderLocations locs =
    -- sorts the stash locations followed by the characters
    List.sortBy .is_character locs


locLink : Location -> Html
locLink loc =
    li
        []
        [ a
            [ href ("/browse/" ++ String.toLower loc.name ) ]
            [ text loc.name ]
        ]


view : Signal.Address Action -> Model -> Html
view address model =
    li
        [ class "dropdown" ]
        [ a
            [ href "#",
              class "dropdown-toggle",
              attribute "data-toggle" "dropdown"
            ]
            [ text "Jump To...",
              b [ class "caret"] []
            ],
          ul
            [ class "dropdown-menu" ]
            (List.map locLink model.locations)
        ]



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
