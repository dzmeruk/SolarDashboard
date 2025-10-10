# Tries two different ways. First, csv lookup, then geopy

import pandas as pd
from geopy.geocoders import Nominatim
from config import DATA_DIR

ZIP_df = pd.read_csv(DATA_DIR/"uszips.csv")
geolocator = Nominatim(user_agent="solar_forecaster")

def ZIPtocoords(ZIP:str) -> tuple[float,float]|None:
    # Could have just done "ZIPtocoords(ZIP)" without the other stuff.
    # Using "type hints" in this way helps with error messaging and readability.
    """
    Input is a ZIP code. Output is (latitude,longitude)
    First tries the csv database, then tries geopy.
    Returns None if neither work.
    """
    df_row = ZIP_df[ZIP_df["zip"].astype(str)==str(ZIP)]
    if not df_row.empty:
        lat = df_row.iloc[0]["lat"]
        lon = df_row.iloc[0]["lng"]
        return lat,lon

    try:
        location = geolocator.geocode(f"{ZIP},USA")
        if location:
            return location.latitude,location.longitude
    except Exception as e:
        print(f"Geopy error for ZIP {ZIP}: {e}")
    return None

#test
if __name__ == "__main__":
    #only runs if the script is run directly -- not if it's imported as a module
    test_ZIPs = ["83333","91106","49629"]
    for ZIP in test_ZIPs:
        coords = ZIPtocoords(ZIP)
        print(f"{ZIP},{coords[0]},{coords[1]}")