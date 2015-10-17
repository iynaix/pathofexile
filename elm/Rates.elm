module Rates where

import Effects exposing (Effects, Never)
import Html exposing (..)
import Html.Events exposing (..)
import Html.Attributes exposing (..)
import Html.Shorthand exposing (..)
import Task exposing (..)

import StartApp
import Http
import Json.Decode as Json exposing ((:=))


-- MODEL

type alias Result =
    { poerates: Float,
      poeex: Float
    }

type alias Model =
    { result: Result,
      query: String
    }


init : (Model, Effects Action)
init =
    ( { result = { poerates = 0, poeex = 0 },
        query = ""
        },
        Effects.none
    )


-- UPDATE


type Action
    = FetchResult String
    | UpdateModel (Maybe Result)


update : Action -> Model -> (Model, Effects Action)
update action model =
    case action of
        FetchResult query ->
            (model, fetchResp query)
        UpdateModel res ->
            case res of
                Nothing ->
                    init
                Just r ->
                    ({ model | result <- r }, Effects.none)


-- VIEW


ratesHtml : Signal.Address Action -> Model -> Html
ratesHtml address model =
    Html.form
        []
        [ div
            [ class "form-group" ]
            [ input
                [ type' "text",
                  class "form-control input-lg text-center",
                  placeholder "e.g. wtb 500 alts 1 ex",
                  on "change" targetValue (\txt -> Signal.message address (FetchResult txt))
                ]
                []
            ]
        ]



view : Signal.Address Action -> Model -> Html
view address model =
    ratesHtml address model


-- EFFECTS


decodeResult : Json.Decoder Result
decodeResult =
    Json.object2 Result
        ("poerates" := Json.float)
        ("poeex" := Json.float)


fetchResp: String -> Effects Action
fetchResp query =
    Http.get decodeResult "."
        |> Task.toMaybe
        |> Task.map UpdateModel
        |> Effects.task


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
