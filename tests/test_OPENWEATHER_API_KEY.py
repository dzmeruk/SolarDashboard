# Allows tests located in "tests" subdirectory to import modules in "scripts"######################
import path_to_scripts
path_to_scripts.path_to_scripts()
###################################################################################################

import requests
import config

url = f"http://api.openweathermap.org/data/2.5/weather?lat=33.7490&lon=-84.3880&appid={config.OPENWEATHER_API_KEY}"
response = requests.get(url)
print(response.json())