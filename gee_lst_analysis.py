import ee
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import optimize


service_account = "gee-service-account@gee-experimentation.iam.gserviceaccount.com"
credentials = ee.ServiceAccountCredentials(service_account, "private-key.json")
ee.Initialize(credentials)

# Import the MODIS land cover collection.
lc = ee.ImageCollection("MODIS/006/MCD12Q1")

# Import the MODIS land surface temperature collection.
lst = ee.ImageCollection("MODIS/006/MOD11A1")

# Import the USGS ground elevation image.
elv = ee.Image("USGS/SRTMGL1_003")

# Initial date of interest (inclusive).
i_date = "2000-01-01"

# Final date of interest (exclusive).
f_date = "2023-01-01"

# Selection of appropriate bands and dates for LST.
lst = lst.select("LST_Day_1km", "QC_Day").filterDate(i_date, f_date)

# Define the urban location of interest as a point near Lyon, France.
u_lon = 4.8148
u_lat = 45.7758
u_poi = ee.Geometry.Point(u_lon, u_lat)

# Define the rural location of interest as a point away from the city.
r_lon = 5.175964
r_lat = 45.574064
r_poi = ee.Geometry.Point(r_lon, r_lat)

scale = 1000  # scale in meters

# Print the elevation near Lyon, France.
elv_urban_point = elv.sample(u_poi, scale).first().get("elevation").getInfo()
print("Ground elevation at urban point:", elv_urban_point, "m")

# Calculate and print the mean value of the LST collection at the point.
lst_urban_point = lst.mean().sample(u_poi, scale).first().get("LST_Day_1km").getInfo()
print(
    "Average daytime LST at urban point:",
    round(lst_urban_point * 0.02 - 273.15, 2),
    "°C",
)

# Print the land cover type at the point.
lc_urban_point = lc.first().sample(u_poi, scale).first().get("LC_Type1").getInfo()
print("Land cover value at urban point is:", lc_urban_point)

# Get the data for the pixel intersecting the point in urban area.
lst_u_poi = lst.getRegion(u_poi, scale).getInfo()

# Get the data for the pixel intersecting the point in rural area.
lst_r_poi = lst.getRegion(r_poi, scale).getInfo()

# Preview the result.
print(lst_u_poi[:5])


def ee_array_to_df(arr, list_of_bands):
    """Transforms client-side ee.Image.getRegion array to pandas.DataFrame."""
    df = pd.DataFrame(arr)

    # Rearrange the header.
    headers = df.iloc[0]
    df = pd.DataFrame(df.values[1:], columns=headers)

    # Remove rows without data inside.
    df = df[["longitude", "latitude", "time", *list_of_bands]].dropna()

    # Convert the data to numeric values.
    for band in list_of_bands:
        df[band] = pd.to_numeric(df[band], errors="coerce")

    # Convert the time field into a datetime.
    df["datetime"] = pd.to_datetime(df["time"], unit="ms")

    # Keep the columns of interest.
    df = df[["time", "datetime", *list_of_bands]]

    return df


def t_modis_to_celsius(t_modis):
    """Converts MODIS LST units to degrees Celsius."""
    t_celsius = 0.02 * t_modis - 273.15
    return t_celsius


def fit_func(t, lst0, delta_lst, tau, phi):
    return lst0 + (delta_lst / 2) * np.sin(2 * np.pi * t / tau + phi)


lst_df_urban = ee_array_to_df(lst_u_poi, ["LST_Day_1km"])


# Apply the function to get temperature in celsius.
lst_df_urban["LST_Day_1km"] = lst_df_urban["LST_Day_1km"].apply(t_modis_to_celsius)

# Do the same for the rural point.
lst_df_rural = ee_array_to_df(lst_r_poi, ["LST_Day_1km"])
lst_df_rural["LST_Day_1km"] = lst_df_rural["LST_Day_1km"].apply(t_modis_to_celsius)

print(lst_df_urban.head())

# Fitting curves.
## First, extract x values (times) from the dfs.
x_data_u = np.asanyarray(lst_df_urban["time"].apply(float))  # urban
x_data_r = np.asanyarray(lst_df_rural["time"].apply(float))  # rural

## Secondly, extract y values (LST) from the dfs.
y_data_u = np.asanyarray(lst_df_urban["LST_Day_1km"].apply(float))  # urban
y_data_r = np.asanyarray(lst_df_rural["LST_Day_1km"].apply(float))  # rural

## Optimize the parameters using a good start p0.
lst0 = 20
delta_lst = 40
tau = 365 * 24 * 3600 * 1000  # milliseconds in a year
phi = (
    2 * np.pi * 4 * 30.5 * 3600 * 1000 / tau
)  # offset regarding when we expect LST(t)=LST0

params_u, params_covariance_u = optimize.curve_fit(
    fit_func, x_data_u, y_data_u, p0=[lst0, delta_lst, tau, phi]
)
params_r, params_covariance_r = optimize.curve_fit(
    fit_func, x_data_r, y_data_r, p0=[lst0, delta_lst, tau, phi]
)

# Subplots.
fig, ax = plt.subplots(figsize=(14, 6))

# Add scatter plots.
ax.scatter(
    lst_df_urban["datetime"],
    lst_df_urban["LST_Day_1km"],
    c="black",
    alpha=0.2,
    label="Urban (data)",
)
ax.scatter(
    lst_df_rural["datetime"],
    lst_df_rural["LST_Day_1km"],
    c="green",
    alpha=0.35,
    label="Rural (data)",
)

# Add fitting curves.
ax.plot(
    lst_df_urban["datetime"],
    fit_func(x_data_u, params_u[0], params_u[1], params_u[2], params_u[3]),
    label="Urban (fitted)",
    color="black",
    lw=2.5,
)
ax.plot(
    lst_df_rural["datetime"],
    fit_func(x_data_r, params_r[0], params_r[1], params_r[2], params_r[3]),
    label="Rural (fitted)",
    color="green",
    lw=2.5,
)

# Add some parameters.
ax.set_title("Daytime Land Surface Temperature Near Lyon", fontsize=16)
ax.set_xlabel("Date", fontsize=14)
ax.set_ylabel("Temperature [C]", fontsize=14)
ax.set_ylim(-0, 40)
ax.grid(lw=0.2)
ax.legend(fontsize=14, loc="lower right")

plt.savefig("output2.png")
