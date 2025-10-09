import requests
import config

url = f"https://developer.nrel.gov/api/nsrdb/v2/solar/psm3-download.json?api_key={config.NREL_API_KEY}&lat=33.7490&lon=-84.3880"  # Atlanta, GA
response = requests.get(url)
print(response.json())  # Should return JSON with irradiance data