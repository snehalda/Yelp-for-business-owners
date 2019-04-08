import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import cufflinks as cf
from app import app,check_in
from app import business,reviews
import plotly.graph_objs as go
import dash_wordcloud
import json
from bson import json_util
from bson.json_util import dumps
from pandas.io.json import json_normalize

FIELDS = {'business_id': True, 'name': True, 'state': True, 'is_open': True, 'categories': True,'latitude':True, 'longitude': True, '_id': False}
FIELDS = {'business_id': True, 'name': True, 'state': True, 'stars':1,'is_open': True, 'categories': True,'latitude':True, 'longitude': True, '_id': False}
rev_FIELDS = {'business_id':1,'text':1, 'stars': 1,'date': 1,'review_id':1,'_id': 0}
review = reviews.find(projection=rev_FIELDS, limit=100000)
rev_df = json_normalize(json.loads(dumps(review)))
bus = business.find(projection=FIELDS, limit=100000)
bus_df= json_normalize(json.loads(dumps(bus)))
bus_df = bus_df[bus_df.categories.str.contains("Restaurant", na=False)]

# rev_df = reviews_df
# bus_df = business_df


layout = html.Div([
    html.H1('Exploratory analysis'),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'NY', 'value': 'COKE'},
            {'label': 'PA', 'value': 'TSLA'},
            {'label': 'AZ', 'value': 'AAPL'}
        ],
        value=['NV'],
        multi = True,
    ),
    dcc.Graph(id='my-graph1'),html.Div(
        [
            html.Div([
                html.P("Yearly Star Distribution"),
                dcc.Graph(
                    id="year1",
                    config=dict(displayModeBar=False),
                    style={"height": "87%", "width": "98%"},
                ),
            ],
                className="six columns chart_div"
            ),

            html.Div(
                [
                    html.P("Monthly stars distribution"),
                    dcc.Graph(
                        id="month1",
                        # figure=cases_by_account(accounts, cases),
                        config=dict(displayModeBar=False),
                        style={"height": "87%", "width": "98%"},
                    ),
                ],
                className="six columns chart_div"
            ),
        ],
        className="row",
        style={"marginTop": "5px"},
    ),
])

@app.callback(Output('my-graph1', 'figure'), [Input('my-dropdown', 'value')])
def plot_time_series(dropdown_value):
    #checkin = check_in.loc[check_in['business_id'] == '3Mc-LxcqeguOXOVT_2ZtCg']
    checkin = check_in.fillna(0)
    df = checkin.groupby(['weekday', 'hour'])['checkins'].sum()
    df = df.reset_index()
    df = df.pivot(index='hour', columns='weekday')[['checkins']]
    df.columns = df.columns.droplevel()
    df = df.reset_index()
    # Workaround for not being able to sort the values by hour
    df.hour = df.hour.apply(lambda x: str(x).split(':')[0])
    df.hour = df.hour.astype(int)
    # Sort the hour column
    df = df.sort_values('hour')
   #

    df = df[['hour', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']]
    df = checkin.groupby(['weekday', 'hour', ])['checkins'].sum().to_frame().reset_index()
    df.hour = df.hour.apply(lambda x: str(x).split(':')[0])
    df.hour = df.hour.astype(int)
    df = df.sort_values('hour')
    df = df.pivot(index='hour', columns='weekday')[['checkins']]
    df.columns = df.columns.droplevel()

    df = df.fillna(0)

    #print(df)
    json_stars = df.to_json(orient='split')

    # df = pd.DataFrame()
    # for x in dropdown_value:
    #     dat_x=pd.read_csv("C://Users//Snehal//Downloads//AAPL.csv")
    #     dat_x.set_index("Date", inplace= True)
    #     df=pd.concat([df,dat_x.Close],axis=1)
    #     print(df)
    #     print('***********************')
    # df.columns=dropdown_value
    # print(df.iplot(asFigure=True))
    return  df.iplot(asFigure=True)
@app.callback(
    Output("year1", "figure"),
    [
        Input('my-dropdown', 'value'),
    ],
)
def cases_reasons_callback(bid):
    return cases_by_reasons()

def cases_by_reasons():
    #print('before')
    #print(rev_df)
    cases = rev_df
    #print('after')
    #print(cases)
    cases['date'] = pd.to_datetime(cases['date'])
    cases['year'] = cases['date'].dt.year
    cases['month'] = cases['date'].dt.month
    cnt = cases.groupby('year')['stars'].sum()
    #print(cnt)
    #print('---------------')
    #print(list(cnt))
    cnt = cnt.reset_index().rename(columns={'index': 'year', 'year': 'count'})
    #print(cnt)
    data = [go.Bar(y=cnt['count'], x=cnt['stars'],
                   orientation="h")]  # x could be any column value since its a count

    layout = go.Layout(
        barmode="stack",
        margin=dict(l=210, r=25, b=20, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(title='Stars'),
        yaxis=dict(title='Year')
    )

    return {"data": data, "layout": layout}

@app.callback(
    Output("month1", "figure"),
    [
        Input('my-dropdown', 'value'),
    ],
)
def cases_account_callback(bid):
    return cases_by_account()

def cases_by_account():
    print('before')
    #print(rev_df)
    cases = rev_df
    #print('after')
    #print(cases)
    cases['date'] = pd.to_datetime(cases['date'])
    cases['year'] = cases['date'].dt.year
    cases['month'] = cases['date'].dt.month
    cnt = cases.groupby('month')['stars'].sum()
    #print(cnt)
    print('---------------')
    #print(list(cnt))
    cnt = cnt.reset_index().rename(columns={'index': 'month', 'month': 'count'})
    #print(cnt)
    data = [go.Bar(y=cnt['count'], x=cnt['stars'],
                   orientation="h")]  # x could be any column value since its a count

    layout = go.Layout(
        barmode="stack",
        margin=dict(l=210, r=25, b=20, t=0, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(title='Stars'),
        yaxis=dict(title='Month')
    )

    return {"data": data, "layout": layout}