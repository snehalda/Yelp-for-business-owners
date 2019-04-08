import math

import pandas as pd
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import dateutil.parser
from pymongo import MongoClient
from bson.json_util import dumps
from pandas.io.json import json_normalize
import json
import re

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
app.config.suppress_callback_exceptions = True
app.config['suppress_callback_exceptions']=True

millnames = ["", " K", " M", " B", " T"]  # used to convert numbers

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'DIVA'
COLLECTION_NAME = 'business'


#df=pd.read_json(os.path.join(STATIC_PATH,'yelp_academic_dataset_business.json'))

connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
business = connection[DBS_NAME]['business']
reviews = connection[DBS_NAME]['review']
connection.close()

# business_df = pd.read_json('D:/Spring19/DIVA/project/dataset/yelp-dataset (1)/yelp_academic_dataset_business.json', lines=True)
# business_df = business_df[business_df.categories.str.contains("Restaurant", na=False) & business_df['is_open']==1]
#
# reviews_df = pd.read_json('D:/Spring19/DIVA/project/dataset/yelp-dataset (1)/test3.json', lines=True)

path = "C:\\Users\\Snehal\Downloads\\yelp_checkin.csv"
check_in = pd.read_csv(path)

def categories():
    FIELDS = {'business_id': True, 'name': True, 'state': True, 'stars': 1, 'is_open': True, 'categories': True,
              'latitude': True, 'longitude': True, '_id': False}
    bus = business.find(projection=FIELDS, limit=100000)
    df = json_normalize(json.loads(dumps(bus)))
    rest_df = df[df.categories.str.contains("Restaurant", na=False)]
    rest_df = rest_df[rest_df.categories.str.contains("Restaurant", na=False)]
    business_cats = rest_df['categories'].to_string(index=False)
    business_cats = re.sub("Restaurants", '', business_cats)
    business_cats = re.sub("Food", '', business_cats)
    business_cats = re.sub("\n", '', business_cats)
    business_cats = business_cats.replace(",...,", ",")
    b_list = business_cats.split(',')
    cats = pd.DataFrame(' '.join(b_list).split(), columns=['category'])
    x = cats.category.value_counts()
    print("There are ", len(x), " different types/categories of Businesses in Yelp!")
    x = x.sort_values(ascending=False)
    x = x.iloc[1:20]
    x = x.sort_index()
    x = x.reset_index().rename(columns={'index': 'cat', 'stars': 'count'})
    print(x['cat'])
    return x['cat']

def get_categories(ip_def):
    rest_df1 = ip_def[ip_def.categories.str.contains("Restaurant", na=False)]
    business_cats = rest_df1['categories'].to_string(index=False)
    business_cats = re.sub("Restaurants", '', business_cats)
    business_cats = re.sub("Food", '', business_cats)
    business_cats = re.sub("\n", '', business_cats)
    business_cats = business_cats.replace("...", "")
    b_list = business_cats.split(',')
    cats = pd.DataFrame(' '.join(b_list).split(), columns=['category'])
    x = cats.category.value_counts()
    print("There are ", len(x), " different types/categories of Businesses in Yelp!")
    x = x.sort_values(ascending=False)
    x = x.iloc[1:5]
    x = x.sort_index()
    x = x.reset_index().rename(columns={'index': 'cat', 'stars': 'count'})
    print(x['cat'])
    return x['cat']
# return html Table with dataframe values
def df_to_table(df):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # Body
        [
            html.Tr(
                [
                    html.Td(df.iloc[i][col])
                    for col in df.columns
                ]
            )
            for i in range(len(df))
        ]
    )


# returns most significant part of a number
def millify(n):
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    return "{:.0f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])


# returns top indicator div
def indicator(color, text, id_value):
    return html.Div(
        [

            html.P(
                text,
                className="twelve columns indicator_text"
            ),
            html.P(
                id=id_value,
                className="indicator_value",
                style={"font-size": "20px"},
            ),
        ],
        className="four columns indicator",

    )
