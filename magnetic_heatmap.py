import pandas as pd
import plotly.express as px
from IPython.display import display

pd.set_option('display.max_columns', None)

# read text file into pandas DataFrame
df = pd.read_csv("mag_data1.txt", sep=",")
  
print(df)

x = df['GPSLAT'].values.tolist()
y = df['GPSLON'].values.tolist()
time = df['TIME'].values.tolist()
mag_field = df['MAGFIELD'].values.tolist()


x = df['GPSLAT'].values.tolist()
y = df['GPSLON'].values.tolist()
time = df['TIME'].values.tolist()
mag_field = df['MAGFIELD'].values.tolist()

fig = px.density_mapbox(
    df, 
    lat=x, 
    lon=y, 
    z=mag_field, 
    radius=15,
    center=dict(lat=45.782, lon=3.147), zoom=18,
    mapbox_style="stamen-terrain",
    labels= {'lat':'lat', 'lon':'lon', 'z':'µT'},
    title='Puy de la Poix : distributions de valeurs magnétiques au transect 1',
    width=1250,
    height=1000,
)

fig.write_image('mag_heatmap.png')