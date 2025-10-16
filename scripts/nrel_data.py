"""
Defines function to fetch solar irradiance and temperature data from the NREL NSRDB GOES v4 API
for a specified latitude, longitude, and year.
API docs here: https://developer.nrel.gov/docs/solar/nsrdb/nsrdb-GOES-full-disc-v4-0-0-download/
More here: https://microsoft.github.io/AIforEarthDataSets/data/nsrdb.html

Requirements:
    - You must have an NREL API key stored in config.py as NREL_API_KEY.
    - The API terms of use require a name, reason, and email in the request.
"""

import requests
import pandas as pd
import time
from pathlib import Path
from config import *


OUTPUT_FILE = DATA_DIR/"nrel_data.csv"
REASON = "Educational / portfolio project"
BASE_URL = "https://developer.nrel.gov/api/nsrdb/v2/solar/nsrdb-GOES-aggregated-v4-0-0-download.csv"
YEARS = [2021, 2022, 2023, 2024]
REPRESENTATIVE_YEAR = 2023 # need a non-leap year as the final representative calendar

# Function to fetch data
def fetch_nrel_data(lat: float, lon: float, year: int = 2024) -> pd.DataFrame | None:
    """Fetch hourly solar irradiance and temperature data for a given location and year."""
    params = {
        "api_key": NREL_API_KEY,
        "wkt": f"POINT({lon:.4f} {lat:.4f})",
        "names": str(year),
        "leap_day": "false",
        "interval": 60,  # hourly
        "attributes": "ghi,dhi,dni,air_temperature,wind_speed",
        "affiliation": "Portfolio project",
        "full_name": USER_NAME,
        "reason": REASON,
        "email": EMAIL,
        "utc": "true",  # timestamps in UTC
    }
    print(f"Requesting NSRDB GOES Aggregated data for {lat:.6f}, {lon:.6f} ({year})...")
    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        print(f"Error fetching NSRDB GOES Aggregated data: {response.status_code}")
        return None

    try:
        #save the csv content to a temp file
        temp_file = DATA_DIR / f"nrel_data_temp_{lat}_{lon}_{year}.csv"
        temp_file.write_text(response.text)

        # Read the CSV into a DataFrame
        df = pd.read_csv(temp_file)

        print(f"Retrieved {len(df)} hourly records for {year}.")
        df = pd.read_csv(temp_file, skiprows=2)  # Skip NSRDB metadata rows
        df['timestamp'] = pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute']]).astype(int) // 10 ** 9
        return df

    except Exception as e:
        print(f"Failed to parse CSV: {e}")
        return None

if __name__ == "__main__":
    # Example: Hailey, ID
    lat, lon = 43.5196, -114.3153
    year = 2024

    df = fetch_nrel_data(lat, lon, year)

    if df is not None and not df.empty:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Data saved to {OUTPUT_FILE.resolve()}")
    else:
        print("No data fetched.")