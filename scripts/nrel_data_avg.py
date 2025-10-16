"""
Defines a function to fetch and average multi-year solar irradiance data
from the NREL NSRDB API to create a Typical Meteorological Year (TMY) file
for direct use with the pvlib library.

API docs here: https://developer.nrel.gov/docs/solar/nsrdb/nsrdb-GOES-full-disc-v4-0-0-download/
More here: https://microsoft.github.io/AIforEarthDataSets/data/nsrdb.html
"""

import requests
import pandas as pd
from pathlib import Path
import time
from config import NREL_API_KEY, USER_NAME, EMAIL, DATA_DIR
from ZIP_data import get_ZIP_data

# --- Configuration ---
BASE_URL = "https://developer.nrel.gov/api/nsrdb/v2/solar/nsrdb-GOES-aggregated-v4-0-0-download.csv"
REASON = "Educational / portfolio project"
PVLIB_ATTRIBUTES = "ghi,dhi,dni,air_temperature,wind_speed"
YEARS_TO_FETCH = [2023, 2024]
REPRESENTATIVE_YEAR = 2023

def fetch_and_average_nrel_data(zip_code: str, output_dir: Path) -> Path | None:
    """
    Fetches and averages hourly NREL data for multiple years to create a TMY file.
    """
    location_data = get_ZIP_data(zip_code)
    if not location_data:
        print(f"Could not get location data for ZIP {zip_code}")
        return None
    lat, lon, elevation, timezone = location_data

    all_years_dfs = []

    # Loop through each year and fetch its data
    for year in YEARS_TO_FETCH:
        params = {
            "api_key": NREL_API_KEY, "wkt": f"POINT({lon:.4f} {lat:.4f})", "names": str(year),
            "leap_day": "false", "interval": "60", "utc": "true", "full_name": USER_NAME,
            "email": EMAIL, "affiliation": "Portfolio Project", "reason": REASON,
            "attributes": PVLIB_ATTRIBUTES,
        }

        print(f"Requesting NREL data for ZIP {zip_code} (Year: {year})...")
        response = requests.get(BASE_URL, params=params)

        if response.status_code != 200:
            print(f"Error fetching NREL data for {year}: {response.status_code} - {response.text}")
            return None

        # Define a unique temporary file path for each year
        temp_file_path = output_dir / f"nrel_temp_{zip_code}_{year}.csv"

        try:
            # Write the API response to the temporary file
            temp_file_path.write_text(response.text)

            # Read the data from the temporary file
            df = pd.read_csv(temp_file_path, skiprows=2)

            df['timestamp'] = pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute']])
            df = df.set_index('timestamp').tz_localize('UTC')
            all_years_dfs.append(df)
            print(f" -> Success for {year}.")

        except Exception as e:
            print(f" -> Failed to parse data for {year}: {e}")
            return None
        finally:
            # Ensure the temporary file is always deleted
            if temp_file_path.exists():
                temp_file_path.unlink()

        time.sleep(1) # Delay between API calls

    if not all_years_dfs:
        print("No data was successfully fetched.")
        return None

    # Combine all yearly DataFrames
    multi_year_df = pd.concat(all_years_dfs)

    # Calculate the average for each hour of the year
    print("\nAveraging data across all years...")
    tmy_df = multi_year_df.groupby([
        multi_year_df.index.month, multi_year_df.index.day, multi_year_df.index.hour
    ]).mean()
    tmy_df.index.names = ['Month', 'Day', 'Hour']

    # Create a new DatetimeIndex for the representative year
    tmy_index = pd.to_datetime(
        f'{REPRESENTATIVE_YEAR}-' + tmy_df.index.get_level_values('Month').astype(str) + '-' +
        tmy_df.index.get_level_values('Day').astype(str) + ' ' +
        tmy_df.index.get_level_values('Hour').astype(str) + ':00'
    )
    tmy_df.index = tmy_index.tz_localize('UTC')

    # Rename and select final columns for pvlib
    rename_map = {
        'GHI': 'ghi', 'DHI': 'dhi', 'DNI': 'dni',
        'Temperature': 'temp_air', 'Wind Speed': 'wind_speed'
    }
    tmy_df = tmy_df.rename(columns=rename_map)
    final_df = tmy_df[list(rename_map.values())]

    # Save the final TMY file
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"nrel_tmy_{zip_code}.csv"
    final_df.to_csv(output_path)

    print(f"Successfully created TMY file with {len(final_df)} hourly records.")
    return output_path

# Test
if __name__ == "__main__":
    test_zip = "83333"
    file_path = fetch_and_average_nrel_data(zip_code=test_zip, output_dir=DATA_DIR)

    if file_path:
        print(f"\n Success! TMY data saved to: {file_path.resolve()}")
        print("\n--- TMY File Head ---")
        print(pd.read_csv(file_path, index_col=0, parse_dates=True).head())
    else:
        print(f"\n Failed to get data for ZIP {test_zip}.")