
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
import os
from app import business,reviews,app,check_in

FIELDS = {'business_id': True, 'name': True, 'state': True, 'stars':1,'is_open': True, 'categories': True,'latitude':True, 'longitude': True, '_id': False}

bus = business.find(projection=FIELDS, limit=100000)
df= json_normalize(json.loads(dumps(bus)))
df = df[df.categories.str.contains("Restaurant", na=False)]
# path = "C:\\Users\\Snehal\Downloads\\yelp_checkin.csv"
# check_in = pd.read_csv(path)
rev_FIELDS = {'business_id':1,'text':1, 'stars': 1,'date': 1,'review_id':1,'_id': 0}
review = reviews.find(projection=rev_FIELDS, limit=100000)
rev_df = json_normalize(json.loads(dumps(review)))
#rev_df =reviews_df
# df = business_df

#print(df)
@app.server.route('/home')
def serve_static():
    abc='world'
    return render_template('index.html',abc=abc)

scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]
layout = html.Div([
    html.H1('Yelp businesses'),
html.Div([
    html.Div(id='text-content',style={'width': '40%','display': 'inline-block'}),
    # html.Div(
    #             dcc.Dropdown(
    #                 id="states",
    #                 options=[{'label': i, 'value': i} for i in df['state'].unique()],
    #                 value="all",
    #                 clearable=False,
    #             ),
    #             className="two columns",
    #             style={'width': '49%', 'float': 'right'}
    #         ),
    html.Div(dcc.Graph(id='map', figure={
        'data': [{
            'locationmode': 'USA-states',
            'lat': df['latitude'],
            'lon': df['longitude'],
            'marker': {
                'color': df['stars'],
                'size': 8,
                'opacity': 0.6
            },
            'customdata': df['business_id'],
            'type': 'scattermapbox'
        }],
        'layout': {
            'mapbox': {
                'accesstoken': 'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3MDBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw',
                'bearing': 0,
                'center': {
                    'lat': 33.5,
                    'lon':-111.9
                },
                 'pitch':0,
                'zoom': 9
            },
            'hovermode': 'closest',

            'margin': {'l': 0, 'r': 0, 'b': 0, 't': 0}
        }
    }),style={'width': '60%','float':'left', 'display': 'inline-block'}),
],className="row",
        style={"marginTop": "5px"})

])


@app.callback(
    dash.dependencies.Output('text-content', 'children'),
    [dash.dependencies.Input('map', 'hoverData')])
def update_text(hoverData):
    if hoverData['points'][0]['customdata']=='':
        return ''
    s = df[df['business_id'] == hoverData['points'][0]['customdata']]

    return html.Div([
        html.H2("{}".format(s.iloc[0]['name'])),
        html.H3("Location: {},{}".format(s.iloc[0]['city'],s.iloc[0]['state'])),
        html.H3("Ratings: {}".format(s.iloc[0]['stars'])),
        html.H3("Category: {}".format(s.iloc[0]['categories']))
    ])
    # return html.H3('{} \n  {} {}. \n Ratings: {}. \n Categories: {}'.format(
    #         s.iloc[0]['name'],
    #         s.iloc[0]['city'],
    #         s.iloc[0]['state'],
    #         s.iloc[0]['stars'],
    #         s.iloc[0]['categories']
    #     ))




# @app.callback(dash.dependencies.Output('map', 'figure'),[dash.dependencies.Input('states', 'value')])
# def plot_basin(selection):
#     print(selection)
#     if selection is None:
#         return {}
#     else:
#         if selection == 'all':
#             dff = df
#             colors = ["rgb(0,116,217)", "rgb(255,65,54)", "rgb(133,20,75)", "rgb(255,133,27)", "lightgrey"]
#         else:
#             dff = df[df['state'] == selection]
#             color='green'
#         print('I am here')
#         data =  [{
#         'lat': df['latitude'],
#         'lon': df['longitude'],
#         'marker': go.scattergeo.Marker(
#             size = dff['stars'],
#             color = colors,
#             line = go.scattergeo.marker.Line(
#                 width=0.5, color='rgb(40,40,40)'
#             )),
#         'customdata': df['business_id'],
#         'type': 'scattermapbox'
#         }]
#         layout= {
#         'mapbox': {
#             'accesstoken': 'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3MDBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw'
#         },
#         'hovermode': 'closest',
#         'margin': {'l': 0, 'r': 0, 'b': 0, 't': 0}
#         }
#         return {'data': data, 'layout': layout}


##############################

# this will open a PLOT in new tab in the browser


