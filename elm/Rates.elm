module Rates where

import Effects exposing (Effects, Never)
import Html exposing (..)
import Html.Events exposing (..)
import Html.Attributes exposing (..)
import Html.Shorthand exposing (..)
import Task exposing (..)
import Dict exposing (Dict)

import StartApp
import Http
import Json.Decode as Json exposing ((:=))


-- MODEL

type alias Rates = Dict String Float

type alias Model =
    { result: Rates,
      query: String
    }


init : (Model, Effects Action)
init =
    ( { result = Dict.empty,
        query = ""
        },
        Effects.none
    )


-- UPDATE


type Action
    = FetchResult String
    | UpdateModel (Maybe Rates)


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


-- js equivalent
toFixed : Int -> Float -> String
toFixed num_places f =
    let
        exp = 10 ^ num_places
    in
        (f * exp |> round |> toFloat) / exp |> toString


rateHtml : (String, Float) -> List Html
rateHtml (name, rate) =
    let
        profitLoss pct =
            if pct < 0 then
                [ span [class "label label-danger"] [ text "LOSS" ],
                  span [class "text-danger", style [("margin-left", "0.5em")] ] [text <| toFixed 2 (abs pct) ++ "%"]
                ]
            else
                [ span [class "label label-success"] [ text "PROFIT" ],
                  span [class "text-success", style [("margin-left", "0.5em")] ] [text <| toFixed 2 (abs pct) ++ "%"]
                ]
    in
        [ h3_ name,
          h3 [] (profitLoss rate)
        ]


resultsHtml : Rates -> List Html
resultsHtml rates =
    if Dict.isEmpty rates then
        []
    else
        Dict.toList rates |> List.concatMap rateHtml


ratesHtml : Signal.Address Action -> Model -> Html
ratesHtml address model =
    Html.form
        [ class "text-center" ]
        [ h1_ "PoE Exchange Rates",
          br',
          div
            [ class "form-group" ]
            [ input
                [ type' "text",
                  class "form-control input-lg text-center",
                  placeholder "e.g. wtb 500 alts 1 ex",
                  on "change" targetValue (\txt -> Signal.message address (FetchResult txt))
                ]
                []
            ],
          div
            [ class "container" ]
            ( resultsHtml model.result )
        ]



view : Signal.Address Action -> Model -> Html
view address model =
    ratesHtml address model


-- EFFECTS


decodeResult : Json.Decoder Rates
decodeResult =
    Json.dict Json.float
    -- Json.map Rates
    --     ("poeex" := Json.float)
    --     ("poerates" := Json.float)


constructUrl : String -> String
constructUrl query =
    Http.url "." <| [("q", query)]


fetchResp: String -> Effects Action
fetchResp query =
    Http.get decodeResult (constructUrl query)
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
