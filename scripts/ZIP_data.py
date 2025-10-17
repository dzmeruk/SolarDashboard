# Main purpose is to defin get_ZIP_data function
# Input = ZIP
# Outut = latitude, longitude, elevation (meters), timezone
# Tries two different methods to get latitude/longitude. First, looks in uszips file. Then tries with geolocator.

import pandas as pd
import requests
from geopy.geocoders import Nominatim
from config import DATA_DIR
from timezonefinderL import TimezoneFinder

# Start by defining two functions that are called after lat/long are found.

# first, define function that takes in lat/long and outputs elevation
def get_elevation(lat: float, lon: float) -> float | None:
    """
    Takes latitude and longitude, returns elevation in meters using Open-Meteo API.
    Returns None if the request fails.
    """
    try:
        api_url = f"https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lon}"
        response = requests.get(api_url)
        response.raise_for_status()  # Raises error for bad responses
        elevation = response.json().get("elevation", [0.0])[0]  # Extract elevation
        return elevation
    except Exception as e:
        print(f"Elevation API error: {e}")
        return None

# then, define function that takes in lat/long and outputs timezone (tz)
def get_timezone(lat: float, lon: float) -> TimezoneFinder:
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lon, lat=lat)
    return timezone_str

ZIP_df = pd.read_csv(DATA_DIR/"uszips.csv")
geolocator = Nominatim(user_agent="solar_forecaster")

# Finally, define main function
def get_ZIP_data(ZIP):
    """
    Input is a ZIP code. Output is (latitude,longitude)
    First tries the csv database, then tries geopy.
    Returns None if neither work.
    """

    df_row = ZIP_df[ZIP_df["zip"].astype(str)==str(ZIP)]
    if not df_row.empty:
        lat = df_row.iloc[0]["lat"]
        lon = df_row.iloc[0]["lng"]
        elevation = get_elevation(lat, lon)
        timezone = get_timezone(lat, lon)
        return lat, lon, elevation, timezone

    try:
        location = geolocator.geocode(f"{ZIP},USA")
        if location:
            elevation = get_elevation(location.latitude, location.longitude)
            timezone = get_timezone(location.latitude, location.longitude)
            return location.latitude, location.longitude, elevation, timezone
    except Exception as e:
        print(f"Geopy error for ZIP {ZIP}: {e}")
        return None


#test
if __name__ == "__main__":
    #only runs if the script is run directly -- not if it's imported as a module
    test_ZIPs = ["83333","91106","49629"]
    for ZIP in test_ZIPs:
        data = ZIP_data(ZIP)
        print(f"{ZIP},{data[0]},{data[1]},{data[2]},{data[3]}")