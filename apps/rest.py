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
                    id="states",
                    options=[{'label': i, 'value': i} for i in bus_df['state'].unique()],
                    value="NV",
                    clearable=False,
                ),
                className="two columns",
                style={"marginBottom": "10"},
            ),
            html.Div(

                dcc.Dropdown(
                    id="city",
                    value="Las Vegas",
                    clearable=False,
                ),
                className="two columns",
            ),
            html.Div(

                dcc.Dropdown(
                    id="restname",
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
        id="b_id",
        key="",
        style={"display": "none"},
    ),
    html.Div(
        [
            indicator(
                "#00cc96",
                "Category",
                "category",
            ),
            indicator(
                "#119DFF",
                "Stars",
                "star",
            ),
            indicator(
                "#EF553B",
                "Number of reviews",
                "review",
            )
        ],
        className="row",
    ),

    html.Div(
        [

            html.Div(
                [
                    html.P('Checkins over a week'),
                    dcc.Graph(
                        id='my-graph',
                        config=dict(displayModeBar=False),
                        style={"height": "87%", "width": "98%"}),
                ])

        ],
        className="row",
        style={"marginTop": "5px"},
    ),

    html.Div(
        [
            html.Div([
                html.P("Popular categories in same region"),
                dcc.Graph(
                    id="cases_reasons",
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
                        id="cases_by_account",
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
    html.Div(
                [
                    html.P("Word cloud"),
                    dcc.Graph(
                        id="word_cloud",
                        style={"height": "80%", "width": "60%"},
                        config=dict(displayModeBar=False),
                    ),
                ]
            )
]

@app.callback(
    dash.dependencies.Output('city', 'options'),
    [dash.dependencies.Input('states', 'value')]
)
def update_city_dropdown(name):
    return [{'label': i, 'value': i} for i in bus_df[bus_df['state']==name]['city'].unique()]

@app.callback(
    dash.dependencies.Output('restname', 'options'),
    [dash.dependencies.Input('city', 'value'),dash.dependencies.Input('states', 'value')]
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
    Output("category", "children"),
[Input("states", "value"),
        Input("city", "value"),
        Input("restname", "value")]
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
    Output("star", "children"),
[Input("states", "value"),
        Input("city", "value"),
        Input("restname", "value")]
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
       # print(bus_df[bus_df['business_id']==bid]['stars'])
        return bus_df[bus_df['business_id']==bid]['stars']

@app.callback(
    Output("review", "children"),
[Input("states", "value"),
        Input("city", "value"),
        Input("restname", "value")]
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
    Output("b_id", "key"),
[Input("states", "value"),
        Input("city", "value"),
        Input("restname", "value")]
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

@app.callback(Output('my-graph', 'figure'), [Input('b_id', 'key')])
def plot_time_series(bid):
    checkin = check_in.loc[check_in['business_id'] == bid]
    checkin = checkin.fillna(0)

    df = checkin.groupby(['weekday', 'hour', ])['checkins'].sum().to_frame().reset_index()
    df.hour = df.hour.apply(lambda x: str(x).split(':')[0])
    df.hour = df.hour.astype(int)
    df = df.sort_values('hour')
    df = df.pivot(index='hour', columns='weekday')[['checkins']]
    df.columns = df.columns.droplevel()

    df = df.fillna(0)

    #print(df)

    # df = pd.DataFrame()
    # for x in dropdown_value:
    #     dat_x=pd.read_csv("C://Users//Snehal//Downloads//AAPL.csv")
    #     dat_x.set_index("Date", inplace= True)
    #     df=pd.concat([df,dat_x.Close],axis=1)
    #     print(df)
    #     print('***********************')
    # df.columns=dropdown_value
    # print(df.iplot(asFigure=True))

    return  df.iplot( mode='markers+lines',asFigure=True,xTitle='Hour of day',yTitle='Check-ins',title='Weekly check-in trend')


def pie_chart(df, column, city, state):
    df = df.dropna(subset=["categories", "city", "state"])
    #print('in piechart')
    nb_cases = len(df.index)
    types = []
    values = []

    # filter priority and origin
    if state == "all_p":
        if state == "all":
            types = get_categories(df).tolist()
        else:
            types = get_categories(df[df["state"] == state]).tolist()
    else:
        if state == "all":
            types = get_categories(df[df["city"] == city]).tolist()
        else:
            types = get_categories(df[(df["city"] == city) & (df["state"] == state)]).tolist()

    # if no results were found
    if types == []:
        layout = dict(annotations=[dict(text="No results found", showarrow=False)])
        return {"data": [], "layout": layout}

    for case_type in types:
        nb_type = df.loc[df.categories.str.contains(case_type,na=False)].shape[0]
        values.append(nb_type / nb_cases * 100)

    layout = go.Layout(
        margin=dict(l=0, r=0, b=0, t=4, pad=8),
        legend=dict(orientation="h"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        annotations=[
            dict(
                text='Top categories',
                showarrow=False
            )
        ]
    )

    trace = go.Pie(
        labels=types,
        values=values,
        marker={"colors": ['#FEBFB3', '#E1396C', '#96D38C', '#D0F9B1']},
        hole=0.4
    )

    return {"data": [trace], "layout": layout}

@app.callback(
    Output("cases_reasons", "figure"),
    [
        Input("states", "value"),
        Input("city", "value"),
        Input("restname", "value"),
    ],
)
def cases_reasons_callback(state, city, name):
    print(city)
    print(name)
    dff = bus_df[bus_df['state']==state]
    dff =dff[dff['city']==city]
    return pie_chart(dff, "categories", city, state)

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
@app.callback(
    Output('word_cloud', 'figure'),
    [Input("b_id", "key")])
def update_wordcloud(bid):
    print('word cloud for business id')
    if bid == '':
        bid = 'PZ-LZzSlhSe9utkQYU8pFg'
    review_list = rev_df[rev_df['business_id'] == bid]['text'].tolist()
    json_reviews = []
    comment_words = ' '
    stopwords = set(STOPWORDS)
    stopwords.update(["i", "the", "food", "restaurant", "every","place","this","will","back","come","made","came","here."])
    #print(stopwords)
    word_freq = defaultdict(int)
    for rev in review_list:
        json_reviews.append(rev)
        rev = str(rev)

        # split the value
        tokens = rev.split()

        # Converts each token into lowercase
        for i in range(len(tokens)):
            if tokens[i].lower() not in stopwords:
                json_reviews.append(tokens[i].lower())
                word_freq[tokens[i].lower()] += 1
                comment_words = comment_words + tokens[i].lower() + ' '


    # str1 = ''.join(json_reviews)
    # words = re.split('; |, |\*|\n',str1)[:15]
    word_list=pd.DataFrame.from_dict(word_freq, orient='index') \
        .sort_values(0, ascending=False) \
        .reset_index() \
        .rename(columns={'index':'word',0: 'abs_freq'})
    print('Word frequencies:')
    #print(word_list)
    #print('------------------------')
    word_list = word_list.iloc[1:15]
    frequency = word_list['abs_freq']
    lower, upper = 15, 45
    frequency = [((x - min(frequency)) / (max(frequency) - min(frequency))) * (upper - lower) + lower for x in
                 frequency]
    word_list1 = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []
    wordcloud = WordCloud(width=800, height=800,
                          background_color='white',
                          stopwords=stopwords,
                          min_font_size=10).generate(comment_words)
    for (word, freq), fontsize, position, orientation, color in wordcloud.layout_:
        word_list1.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)
    x = []
    y = []
    for i in position_list[0:30]:
        x.append(i[0])
        y.append(i[1])
    new_freq_list = []
    for i in freq_list[0:30]:
        new_freq_list.append(i * 100)
    new_freq_list
    colors = [plotly.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for i in range(15)]
    weights = [random.randint(15, 35) for i in range(35)]
    y_new = random.choices(range(35), k=30)
    data = [dict(x=x,
                      y=y_new,
                      mode='text',
                      text=word_list1[0:30],
                      marker={'opacity': 0.3},
                      hovertext=['{0}{1}'.format(w, f) for w, f in zip(word_list, freq_list)],
                      textfont=dict(size=new_freq_list,
                                       color=color_list))]
    layout = dict({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})

    return {"data": data, "layout": layout}
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
    Output("cases_by_account", "figure"),
    [
        Input("b_id", "key"),
    ],
)
def cases_account_callback(bid):
    return cases_by_account(bid)
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
def cases_by_account(bid):
    print('before')
    #print(rev_df)
    cases = rev_df[rev_df['business_id'] == bid]
    print('after')
    #print(cases)
    cases['date'] = pd.to_datetime(cases['date'])
    cases['year'] = cases['date'].dt.year
    cases['month'] = cases['date'].dt.month
    cnt = cases.groupby('month')['stars'].mean()
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