# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import flask
import plotly.plotly as py
from plotly import graph_objs as go
import math
from app import app
from apps import EDA, map, restaurant,rest,compare,map2


app.layout = html.Div(
    [
        # header
        html.Div([

            html.Span("Yelp for Business owners", className='app-title'),
        ],
            className="row header"
        ),

        # tabs
        html.Div([

            dcc.Tabs(
                id="tabs",
                style={"height": "20", "verticalAlign": "middle"},
                children=[

                    dcc.Tab(label="Map", value="map_tab"),
                    dcc.Tab(label="Map - ratings", value="map2_tab"),
                    dcc.Tab(id="Analysis", label="Restaurant Analysis", value="rest_tab"),
                    dcc.Tab(label="Compare my business", value="compare_tab"),
                    dcc.Tab(label="Comparative study", value="rest2_tab"),
                    dcc.Tab(label="EDA", value="eda_tab"),
                ],
                value="map_tab",
            )

        ],
            className="row tabs_div"
        ),

        # divs that save dataframe for each tab
        html.Div(
            id="opportunities_df",
            style={"display": "none"},
        ),
        #html.Div(sf_manager.get_leads().to_json(orient="split"), id="leads_df", style={"display": "none"}),  # leads df
        #html.Div(sf_manager.get_cases().to_json(orient="split"), id="cases_df", style={"display": "none"}),  # cases df

        # Tab content
        html.Div(id="tab_content", className="row", style={"margin": "2% 3%"}),

        html.Link(href="https://use.fontawesome.com/releases/v5.2.0/css/all.css", rel="stylesheet"),
        html.Link(
            href="https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",
            rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Open+Sans", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Ubuntu", rel="stylesheet"),
        html.Link(
            href="https://cdn.rawgit.com/amadoukane96/8a8cfdac5d2cecad866952c52a70a50e/raw/cd5a9bf0b30856f4fc7e3812162c74bfc0ebe011/dash_crm.css",
            rel="stylesheet")
    ],
    className="row",
    style={"margin": "0%"},
)


@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "EDA_tab":
        return EDA.layout
    elif tab == "map_tab":
        return map.layout
    elif tab == "map2_tab":
        return map2.layout
    elif tab == "rest_tab":
        return rest.layout
    elif tab == "rest2_tab":
        return restaurant.layout
    elif tab == "compare_tab":
        return compare.layout
    else:
        return EDA.layout


if __name__ == "__main__":
    app.run_server(debug=True)
