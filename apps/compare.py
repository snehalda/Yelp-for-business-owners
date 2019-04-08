from wordcloud import WordCloud, STOPWORDS
from collections import defaultdict
from IPython.core.display import HTML
import json
from bson import json_util
from bson.json_util import dumps
from pandas.io.json import json_normalize
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from flask import Flask, render_template, request
import webbrowser
import re
from app import business,reviews
from app import app,categories,indicator,get_categories,check_in
from dash.dependencies import Input, Output, State
from plotly.offline import iplot, init_notebook_mode
import plotly
import plotly.graph_objs as go
from plotly.offline import plot
import random

FIELDS = {'business_id': True, 'name': True, 'state': True, 'stars':1,'is_open': True, 'categories': True,'latitude':True, 'longitude': True, '_id': False}
rev_FIELDS = {'business_id':1,'text':1, 'stars': 1,'date': 1,'review_id':1,'_id': 0}
review = reviews.find(projection=rev_FIELDS, limit=100000)
rev_df = json_normalize(json.loads(dumps(review)))
bus = business.find(projection=FIELDS, limit=100000)
bus_df= json_normalize(json.loads(dumps(bus)))
bus_df = bus_df[bus_df.categories.str.contains("Restaurant", na=False)]

# rev_df = reviews_df
# bus_df = business_df
bid =''
layout = [

    # top controls
    html.Div(
        [
            html.Div(
                dcc.Dropdown(
                    id="states_c",
                    options=[{'label': i, 'value': i} for i in bus_df['state'].unique()],
                    value="NV",
                    clearable=False,
                ),
                className="two columns",
                style={"marginBottom": "10"},
            ),
            html.Div(

                dcc.Dropdown(
                    id="city_c",
                    value="Las Vegas",
                    clearable=False,
                ),
                className="two columns",
            ),
            html.Div(

                dcc.Dropdown(
                    id="restname_c",
                    value="Maria's Mexican Restaurant & Bakery",
                    clearable=False,
                ),
                className="two columns",
            ),
        ],
        className="row",
        style={},
    ),

    # indicators div
    html.Div(
        id="b_id_c",
        key="",
        style={"display": "none"},
    ),
    html.Div(
        [
            indicator(
                "#00cc96",
                "Category",
                "category_c",
            ),
            indicator(
                "#119DFF",
                "Stars",
                "star_c",
            ),
            indicator(
                "#EF553B",
                "Number of reviews",
                "review_c",
            )
        ],
        className="row",
    ),


    html.Div(
        [

            html.Div(
                [
                    html.P("Rating progress"),
                    dcc.Graph(
                        id="ratings",
                        style={"height": "87%", "width": "98%"},
                    ),
                ]
            ),
        ],
        className="row",
        style={"marginTop": "5px"},
    ),
    html.Div([
        html.Div([
                html.P("Reviews analysis"),
                dcc.Graph(
                    id="rev_analiz",
                    config=dict(displayModeBar=False),
                    style={"height": "100%", "width": "98%"},
                ),
            ],
                className="six columns chart_div",
                style={"height":"450px"}
            ),
        html.Div([
            dcc.Graph(
            id='compt'
            )
        ],className="six columns chart_div"
            )],className="row",
        style={"marginTop": "5px"},)
]

@app.callback(
    dash.dependencies.Output('city_c', 'options'),
    [dash.dependencies.Input('states_c', 'value')]
)
def update_city_dropdown(name):
    return [{'label': i, 'value': i} for i in bus_df[bus_df['state']==name]['city'].unique()]

@app.callback(
    dash.dependencies.Output('restname_c', 'options'),
    [dash.dependencies.Input('city_c', 'value'),dash.dependencies.Input('states_c', 'value')]
)
def update_rest_dropdown(city,state):
    print(city)
    print(state)
    dff = bus_df[bus_df['state']==state]
    dff = dff[dff.categories.str.contains("Restaurant", na=False)]
    dff = dff[dff['city']==city]
    dff.sort_values(by=['review_count', 'stars'])
    #print(dff)
    return [{'label': i, 'value': i} for i in dff[dff['city']==city]['name'].unique()]


@app.callback(
    Output("category_c", "children"),
[Input("states_c", "value"),
        Input("city_c", "value"),
        Input("restname_c", "value")]
)
def category_callback(state,city,rest):
    print('CAT')
    dff = bus_df[bus_df['state'] == state]
    dff = dff[dff['city'] == city]
    if rest =='all':
        bid=''
        return ''
    else:
        df = dff[dff['name'] == rest]
        bid = df['business_id'].item()
        #print(bus_df[bus_df['business_id'] == bid]['categories'])
    return bus_df[bus_df['business_id']==bid]['categories']

@app.callback(
    Output("star_c", "children"),
[Input("states_c", "value"),
        Input("city_c", "value"),
        Input("restname_c", "value")]
)
def star_callback(state,city,rest):
    print('STARS')
    dff = bus_df[bus_df['state'] == state]
    dff = dff[dff['city'] == city]
    if rest == 'all':
        bid = ''
        return ''
    else:
        df = dff[dff['name'] == rest]
        bid = df['business_id'].item()
        #print(bus_df[bus_df['business_id']==bid]['stars'])
        return bus_df[bus_df['business_id']==bid]['stars']

@app.callback(
    Output("review_c", "children"),
[Input("states_c", "value"),
        Input("city_c", "value"),
        Input("restname_c", "value")]
)
def review_callback(state,city,rest):
    print('REVIEWS')
    dff = bus_df[bus_df['state'] == state]
    dff = dff[dff['city'] == city]
    if rest == 'all':
        bid = ''
        return ''
    else:
        df = dff[dff['name'] == rest]
        bid = df['business_id'].item()
        #print(bus_df[bus_df['business_id'] == bid]['review_count'])
        return bus_df[bus_df['business_id']==bid]['review_count']

@app.callback(
    Output("b_id_c", "key"),
[Input("states_c", "value"),
        Input("city_c", "value"),
        Input("restname_c", "value")]
)
def bid_callback(state,city,rest):
    print('BID')
    dff = bus_df[bus_df['state'] == state]
    dff = dff[dff['city'] == city]
    if rest == 'all':
        bid = ''
        return ''
    else:
        df = dff[dff['name'] == rest]
        bid = df['business_id'].item()
        print(bid)
        return bid
#
#
# @app.callback(
#     Output("middle_cases_indicator", "children"), [Input("cases_df", "children")]
# )
# def middle_cases_indicator_callback(df):
#     df = pd.read_json(df, orient="split")
#     medium = len(df[(df["Priority"] == "Medium") & (df["Status"] == "New")]["Priority"].index)
#     return medium
#
#
# @app.callback(
#     Output("right_cases_indicator", "children"), [Input("cases_df", "children")]
# )
# def right_cases_indicator_callback(df):
#     df = pd.read_json(df, orient="split")
#     high = len(df[(df["Priority"] == "High") & (df["Status"] == "New")]["Priority"].index)
#     return high




# @app.callback(
#     Output("word_cloud", "figure"),
#     [
#         Input("b_id", "children")
#     ],
# )
# def wordcloud(bid):
#
#     init_notebook_mode(connected=True)
#     review_list = reviews[[reviews['business_id']==bid]]['reviews']
#     json_reviews = []
#     for review in reviews:
#         json_reviews.append(review)
#     print(json_reviews)
#     text = "Wikipedia was launched on January 15, 2001, by Jimmy Wales and Larry Sanger.[10] Sanger coined its name,[11][12] as a portmanteau of wiki[notes 3] and 'encyclopedia'. Initially an English-language encyclopedia, versions in other languages were quickly developed. With 5,748,461 articles,[notes 4] the English Wikipedia is the largest of the more than 290 Wikipedia encyclopedias. Overall, Wikipedia comprises more than 40 million articles in 301 different languages[14] and by February 2014 it had reached 18 billion page views and nearly 500 million unique visitors per month.[15] In 2005, Nature published a peer review comparing 42 science articles from Encyclopadia Britannica and Wikipedia and found that Wikipedia's level of accuracy approached that of Britannica.[16] Time magazine stated that the open-door policy of allowing anyone to edit had made Wikipedia the biggest and possibly the best encyclopedia in the world and it was testament to the vision of Jimmy Wales.[17] Wikipedia has been criticized for exhibiting systemic bias, for presenting a mixture of 'truths, half truths, and some falsehoods',[18] and for being subject to manipulation and spin in controversial topics.[19] In 2017, Facebook announced that it would help readers detect fake news by suitable links to Wikipedia articles. YouTube announced a similar plan in 2018."  ### taken from Wikipedia: https://en.wikipedia.org/wiki/Wikipedia
#
#     return iplot(pwc(text))

# @app.callback(
#     Output("cases_types", "figure"),
#     [
#         Input("priority_dropdown", "value"),
#         Input("origin_dropdown", "value"),
#         Input("cases_df", "children"),
#     ],
# )
# def cases_types_callback(priority, origin, df):
#     df = pd.read_json(df, orient="split")
#     return pie_chart(df, "Type", priority, origin)
#
#
# @app.callback(
#     Output("cases_by_period", "figure"),
#     [
#         Input("cases_period_dropdown", "value"),
#         Input("origin_dropdown", "value"),
#         Input("priority_dropdown", "value"),
#         Input("cases_df", "children"),
#     ],
# )
# def cases_period_callback(period, origin, priority, df):
#     df = pd.read_json(df, orient="split")
#     return cases_by_period(df, period, priority, origin)
#
#
@app.callback(
    Output("ratings", "figure"),
    [
        Input("b_id_c", "key"),
    ],
)
def ratings_callback(bid):
    return getRatings(bid)

def getRatings(bid):
    cases = rev_df[rev_df['business_id'] == bid]
    cases['date'] = pd.to_datetime(cases['date'])
    cases = cases.sort_values('date')
    trace = go.Scatter(x=list(cases.date),
                       y=list(cases.stars),
                       line=dict(width=1.5,shape='spline')
                       )
    data = [trace]  # x could be any column value since its a count

    layout = go.Layout(
        margin=dict(l=210, r=25, b=20, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                         label='YTD',
                         step='year',
                         stepmode='todate'),
                    dict(count=1,
                         label='1y',
                         step='year',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        ),
        yaxis=dict(title='Stars')
    )

    return {"data": data, "layout": layout}
#
#
# def cases_by_period(df, period, priority, origin):
#     df = df.dropna(subset=["Type", "Reason", "Origin"])
#     stages = df["Type"].unique()
#
#     # priority filtering
#     if priority != "all_p":
#         df = df[df["Priority"] == priority]
#
#     # period filtering
#     df["CreatedDate"] = pd.to_datetime(df["CreatedDate"], format="%Y-%m-%d")
#     if period == "W-MON":
#         df["CreatedDate"] = pd.to_datetime(df["CreatedDate"]) - pd.to_timedelta(
#             7, unit="d"
#         )
#     df = df.groupby([pd.Grouper(key="CreatedDate", freq=period), "Type"]).count()
#
#     dates = df.index.get_level_values("CreatedDate").unique()
#     dates = [str(i) for i in dates]
#
#     co = {  # colors for stages
#         "Electrical": "#264e86",
#         "Other": "#0074e4",
#         "Structural": "#74dbef",
#         "Mechanical": "#eff0f4",
#         "Electronic": "rgb(255, 127, 14)",
#     }
#
#     data = []
#     for stage in stages:
#         stage_rows = []
#         for date in dates:
#             try:
#                 row = df.loc[(date, stage)]
#                 stage_rows.append(row["IsDeleted"])
#             except Exception as e:
#                 stage_rows.append(0)
#
#         data_trace = go.Bar(
#             x=dates, y=stage_rows, name=stage, marker=dict(color=co[stage])
#         )
#         data.append(data_trace)
#
#     layout = go.Layout(
#         barmode="stack",
#         margin=dict(l=40, r=25, b=40, t=0, pad=4),
#         paper_bgcolor="white",
#         plot_bgcolor="white",
#     )
#
#     return {"data": data, "layout": layout}
#
#
@app.callback(
    dash.dependencies.Output('compt', 'figure'),
    [Input("states_c", "value"),
        Input("city_c", "value"),
        Input("restname_c", "value"),Input("b_id_c", "key")])
def update_graph(state,city,rest,bid):
    #print('graph')
    # print(df)
    # print('year value')
    # print(year_value)
    dff = bus_df[bus_df['state'] == state]
    dff = dff[dff['city'] == city]
    if bid =='all':
        return {}
    #print(dff)
    return {
        'data': [go.Scatter(
            y=dff['stars'],
            x=dff['review_count'],
            text=dff['name'],
            selectedpoints= '',
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'},
                'reversescale':True
            }
        ),go.Scatter(
            y=dff[dff['business_id']==bid]['stars'],
            x=dff[dff['business_id']==bid]['review_count'],
            text=dff[dff['business_id']==bid]['name'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'red'},
                'color':'red'
            }
        )],
        'layout': go.Layout(
            title='Compare with my competitors',
            xaxis={
                'title':'Reviews',
                'type': 'linear' if '' == 'Linear' else 'log'
            },
            yaxis={
                'title': 'Stars',
                'type': 'linear' if '' == 'Linear' else 'log'
            },
            margin={'l': 200, 'b': 30, 't': 60, 'r': 40},
            hovermode='closest'
        )
    }
@app.callback(
    dash.dependencies.Output('rev_analiz', 'figure'),
    [Input("b_id_c", "key")])
def update_graph(bid):

    if bid == 'all':
        return {}
    rev_a = rev_df[rev_df['business_id']==bid]
    rev_a.date = pd.to_datetime(rev_a.date)
    rev_a = rev_a.groupby(rev_a.date.dt.year)[['useful','funny','cool']].sum()
    print('rev analiz')
    #print(rev_a)
    return  rev_a.iplot(asFigure=True,xTitle='Year',yTitle='Reviews',title='Yearly Review Analysis')