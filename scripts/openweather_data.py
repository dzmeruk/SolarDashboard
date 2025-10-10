"""
Defines function to fetch solar irradiance and temperature data from OpenWeather
for a specified latitude, longitude, and year.

Requirements:
    - You must have an NREL API key stored in config.py as NREL_API_KEY.
    - The API terms of use require a name, reason, and email in the request.
"""
import requests
import pandas as pd
from pathlib import Path
from config import *

def fetch_openweather(lat: float, lon: float) -> pd.DataFrame | None:
    """
    Fetch 48-hour forecast for a location

    Parameters:
    - lat, lon: coordinates
    """
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error fetching OpenWeather data: {response.status_code}")
        return None

    # JSON --> pandas dataframe prior to csv to be consistent with other weather data.
    data = response.json()
    hourly_data = data.get("hourly",[])

    if not hourly_data:
        print("No 'hourly' forecast data returned.")
        return None

    records = []
    for hour in hourly_data:
        records.append({
            "timestamp": pd.to_datetime(hour["dt"], unit="s"),
            "lat": lat,
            "lon": lon,
            "temperature": hour.get("temp"),
            "feels_like": hour.get("feels_like"),
            "humidity": hour.get("humidity"),
            "cloud_cover": hour.get("clouds"),
            "wind_speed": hour.get("wind_speed"),
            "wind_gust": hour.get("wind_gust"),
            "pressure": hour.get("pressure"),
            "dew_point": hour.get("dew_point"),
            "uvi": hour.get("uvi"),
            "precip_prob": hour.get("pop")
        })

    df = pd.DataFrame(records)
    csv_file = DATA_DIR / f"openweather_hourly_forecast_{lat:.4f}_{lon:.4f}.csv"
    df.to_csv(csv_file, index=False)

    print(f"Saved {len(df)} hourly forecast records to {csv_file.resolve()}")
    return df

if __name__ == "__main__":
    # Example: Hailey, ID
    lat, lon = 43.5196, -114.3153
    fetch_openweather(lat, lon,)
