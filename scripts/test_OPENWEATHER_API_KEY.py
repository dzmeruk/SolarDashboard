import requests
import config

url = f"http://api.openweathermap.org/data/2.5/weather?lat=33.7490&lon=-84.3880&appid={config.OPENWEATHER_API_KEY}"
response = requests.get(url)
print(response.json())