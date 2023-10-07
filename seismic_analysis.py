import pandas as pd
import datetime as datetime
import plotly.express as px
from IPython.display import display

# Data is pulled from this dataset : https://www.kaggle.com/datasets/garrickhague/world-earthquake-data-from-1906-2022/

pd.set_option("display.max_rows", None, "display.max_columns", None)

df = pd.read_csv('earthquake_data.csv')
df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%dT%H:%M:%S.%fZ')

df = df.loc[df['time'] >= datetime.datetime(2015, 1, 1)]

# df = df.loc[df['mag'] >= 4]

x = df['latitude'].values.tolist()
y = df['longitude'].values.tolist()
magnitudes = df['mag'].values.tolist()

fig = px.scatter_mapbox(
    df, 
    lat=x, 
    lon=y, 
    size=magnitudes,
    color=magnitudes,
    center=dict(lat=33.8, lon=35.8), zoom=5,
    mapbox_style="open-street-map",
    labels= {'lat':'lat', 'lon':'lon', 'color':'Magnitude'},
    title='Earthquake distribution and magnitudes, 2015/01-2023/03',
    width=1350,
    height=1200,
)

fig.write_image('earthquake_dist.png')

# print(df.sort_values('time', ascending=False))


