import openmeteo_requests

import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

import requests_cache
from retry_requests import retry

# Get Data: copy pasted from the API https://open-meteo.com/en/docs/historical-weather-api?start_date=2006-10-01&end_date=2026-10-01&latitude=47.6597&longitude=-117.4291&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=America%2FLos_Angeles&hourly=precipitation

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
	"latitude": 47.6597,
	"longitude": -117.4291,
	"start_date": "2005-01-01",
	"end_date": "2025-12-31",
	"hourly": "precipitation",
	"timezone": "America/Los_Angeles",
	"temperature_unit": "fahrenheit",
	"wind_speed_unit": "mph",
	"precipitation_unit": "inch",
}
responses = openmeteo.weather_api(url, params = params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_precipitation = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {
	"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	).tz_convert(response.Timezone().decode())
}

hourly_data["precipitation"] = hourly_precipitation

hourly_dataframe = pd.DataFrame(data = hourly_data)
print("\nHourly data\n", hourly_dataframe)


# ----------------------
# Colors
plot_colors = plt.cm.cividis_r
pie_colors  = plt.cm.twilight(np.linspace(0.1, 1, 12))


# ----------------------
# Graph 1: Preciptiation over time
plt.title('Precipitation in Spokane, Washington')
plt.xlabel('time in years')
plt.ylabel('precipitation in inches')
plt.plot(hourly_data['date'], hourly_data['precipitation'], color = plot_colors(np.linspace(0.9, 0.9, 1)))

# plt.show()
plt.savefig("PrecipitationOverTime_Spokane.png", format = "png", dpi = 600, bbox_inches = 'tight', pad_inches = 0)
plt.clf()
plt.close()


# ----------------------
# Calculations for yearly precipitation
hourly_dataframe['year']  = hourly_dataframe['date'].dt.year
hourly_dataframe['month'] = hourly_dataframe['date'].dt.month

annual_totals = hourly_dataframe.groupby('year')['precipitation'].sum()

# Graph 2: total precipitation per year
normalized  = plt.Normalize(vmin = annual_totals.values.min(), vmax = annual_totals.values.max(), clip = True)
bar_colors  = plot_colors(normalized(annual_totals.values))

color_scale = plt.cm.ScalarMappable(cmap = plot_colors, norm = normalized)
color_scale.set_array([])
color_bar   = plt.colorbar(color_scale, ax=plt.gca())

plt.title('Total Annual Precipitation in Spokane, Washington')
plt.xlabel('year')
plt.ylabel('total precipitation in inches')
plt.bar(annual_totals.index, annual_totals.values, color = bar_colors)

# plt.show()
plt.savefig("TotalAnnualPrecipiation_Spokane.png", format = "png", dpi = 600, bbox_inches = 'tight', pad_inches = 0)
plt.clf()
plt.close()

# ----------------------
# Calculations for monthly percentages of annual precipitation
total_precipitation = hourly_dataframe['precipitation'].sum()
monthly_totals      = hourly_dataframe.groupby('month')['precipitation'].sum()
monthly_percentages = (monthly_totals / total_precipitation) * 100

# Graph 3: average percent montly percipitation
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
labels = [
    f"{months[idx-1]}: {monthly_percentages[idx]:.1f}%"
    for idx in monthly_percentages.index
]

plt.title('Average Monthly Percent Precipitation in Spokane, Washington')
plt.pie(monthly_percentages, labels = labels, startangle = 180, counterclock = False, colors = pie_colors)

# plt.show()
plt.savefig("AverageMonthyPercentPrecipitation_Spokane.png", format = "png", dpi = 600, bbox_inches = 'tight', pad_inches = 0)
plt.clf()
plt.close()

# ----------------------
# Calculations for 2025 precipitation percentages
precipitiation_2025          = hourly_dataframe[hourly_dataframe['date'].dt.year == 2025].copy()
precipitiation_2025['month'] = precipitiation_2025['date'].dt.month
total_precipitation_2025     = precipitiation_2025['precipitation'].sum()
monthly_totals_2025          = precipitiation_2025.groupby('month')['precipitation'].sum()
monthly_percentages_2025     = (monthly_totals_2025 / total_precipitation_2025) * 100

# Graph 4: 2025 precipitation percentages by month
labels_2025 = [
    f"{months[idx-1]}: {monthly_percentages_2025[idx]:.1f}%"
    for idx in monthly_percentages_2025.index
]

plt.title('Percent Precepitation by Month in Spokane, Washington, in 2025')
plt.pie(monthly_percentages_2025, labels = labels_2025, startangle = 180, counterclock = False, colors = pie_colors)

# plt.show()
plt.savefig("PercentPrecipitation2025_Spokane.png", format = "png", dpi = 600, bbox_inches = 'tight', pad_inches = 0)
plt.clf()
plt.close()

# ----------------------
# Calculations for 2021 precipitation percentages (least total precipitation)
precipitiation_2021          = hourly_dataframe[hourly_dataframe['date'].dt.year == 2021].copy()
precipitiation_2021['month'] = precipitiation_2021['date'].dt.month
total_precipitation_2021     = precipitiation_2021['precipitation'].sum()
monthly_totals_2021          = precipitiation_2021.groupby('month')['precipitation'].sum()
monthly_percentages_2021     = (monthly_totals_2021 / total_precipitation_2021) * 100

# Graph 4: 2021 precipitation percentages by month
labels_2021 = [
    f"{months[idx-1]}: {monthly_percentages_2021[idx]:.1f}%"
    for idx in monthly_percentages_2021.index
]

plt.title('Percent Precepitation by Month in Spokane, Washington, in 2021')
plt.pie(monthly_percentages_2021, labels = labels_2021, startangle = 180, counterclock = False, colors = pie_colors)

# plt.show()
plt.savefig("PercentPrecipitation2021_Spokane.png", format = "png", dpi = 600, bbox_inches = 'tight', pad_inches = 0)
plt.clf()
plt.close()

# ----------------------
# Calculations for 2012 precipitation percentages (highest total precipitation)
precipitiation_2012          = hourly_dataframe[hourly_dataframe['date'].dt.year == 2012].copy()
precipitiation_2012['month'] = precipitiation_2012['date'].dt.month
total_precipitation_2012     = precipitiation_2012['precipitation'].sum()
monthly_totals_2012          = precipitiation_2012.groupby('month')['precipitation'].sum()
monthly_percentages_2012     = (monthly_totals_2012 / total_precipitation_2012) * 100

# Graph 4: 2012 precipitation percentages by month
labels_2012 = [
    f"{months[idx-1]}: {monthly_percentages_2012[idx]:.1f}%"
    for idx in monthly_percentages_2012.index
]

explode_values = [
    0.25 if idx == 8 else (0.5 if idx == 9 else 0.0) 
    for idx in monthly_percentages_2012.index
]

plt.title('Percent Precepitation by Month in Spokane, Washington, in 2012')
plt.pie(monthly_percentages_2012, labels = labels_2012, startangle = 180, counterclock = False, colors = pie_colors, explode = explode_values)

# plt.show()
plt.savefig("PercentPrecipitation2012_Spokane.png", format = "png", dpi = 600, bbox_inches = 'tight', pad_inches = 0)
plt.clf()
plt.close()
