
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

scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]
dff = df.groupby('state')[['stars']].mean().reset_index()
data_map = [go.Choropleth(
        colorscale=scl,
        autocolorscale=False,
        locations=dff['state'],
        z= dff['stars'],
        customdata= dff['state'],
        locationmode='USA-states',
        # text = meandata.stars.astype('str', copy=False),
        marker=go.choropleth.Marker(
            line=go.choropleth.marker.Line(
                color='rgb(255,255,255)',
                width=2
            )
        ),
        colorbar=go.choropleth.ColorBar(
            title="Mean Rating"
        )
    )]

layout_map = go.Layout(
        geo=go.layout.Geo(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(255, 255, 255)'),

    )
layout = html.Div([
    html.H1('Yelp businesses'),
html.Div([
    dcc.Graph(id='map_star', figure=dict(data=data_map, layout=layout_map),
                        config=dict(displayModeBar=False), style={'width': '48%','float':'left', 'display': 'inline-block'}
    ),
    dcc.Graph(id='state_star',
                        config=dict(displayModeBar=False), style={'width': '48%','float':'right', 'display': 'inline-block'})
    ,],className="row",
        style={"marginTop": "5px"})

])

@app.callback(
    dash.dependencies.Output("map_star", "figure"),
    [dash.dependencies.Input('map', 'figure')],
)
def mapmydraw(hover):
    dff = df.groupby('state')[['stars']].mean().reset_index()

    data = [go.Choropleth(
        colorscale=scl,
        autocolorscale=False,
        locations=dff['state'],
        z= dff['stars'],
        customdata= dff['state'],
        locationmode='USA-states',
        # text = meandata.stars.astype('str', copy=False),
        marker=go.choropleth.Marker(
            line=go.choropleth.marker.Line(
                color='rgb(255,255,255)',
                width=2
            )
        ),
        colorbar=go.choropleth.ColorBar(
            title="Mean Rating"
        )
    )]

    layout = go.Layout(
        geo=go.layout.Geo(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(255, 255, 255)'),

    )
    return dict(data=data, layout=layout)


    # return html.H3('{} \n  {} {}. \n Ratings: {}. \n Categories: {}'.format(
    #         s.iloc[0]['name'],
    #         s.iloc[0]['city'],
    #         s.iloc[0]['state'],
    #         s.iloc[0]['stars'],
    #         s.iloc[0]['categories']
    #     ))


@app.callback(
    dash.dependencies.Output('state_star', 'figure'),
    [dash.dependencies.Input('map_star', 'hoverData')])
def update_text(hoverData):
    print(hoverData)
    st = hoverData['points'][0]['customdata']
    if st == '':
        st = 'NV'
    s = df[df['state'] == hoverData['points'][0]['customdata']]
    s = s[['name','business_id','city']]

    r = rev_df[rev_df['stars']==5]
    r = r.groupby(['business_id'])[['review_id']].count().reset_index()
    r['review_id'] = r['review_id'].astype(int)

    r = r.sort_values('review_id',ascending=False)
    #print(r)
    result = pd.merge(r, s, on='business_id',how='inner', suffixes=['_l', '_r'])
    result = result.sort_values('review_id', ascending=False)
    result=result.iloc[0:20]
    #print(result[['business_id','review_id']])
    data = [go.Bar(x=result['review_id'], y=result['name'],orientation="h",hovertext=result['city'],marker=go.bar.Marker(
                color='rgb(55, 83, 109)',reversescale=True
            ))]  # x could be any column value since its a count

    layout = go.Layout(
        barmode="stack",
        title='Top 5 star rated restaurants in'+ st,
        margin=dict(l=210, r=30, b=30, t=30, pad=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(title='Review Count'),
        yaxis=dict(title='Restaurants')
    )

    return {"data": data, "layout": layout}


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


