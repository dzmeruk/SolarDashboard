# Solar Dashboard

A web-based dashboard to predict solar energy generation for any U.S. location. Built with Python, Pandas, pvlib (Sandia National Labs), Dash.

Dashboard takes in ZIP code and solar power generation specs and outputs monthly estimates of AC power production.

I can think of several obvious ways to improve the dashboard, but I'm not going to do this now.

To run:
- get an API key from the NREL site linked below.
- Create a file called "config.py" using the "config_template.py" file.
- Fill out with your info and NREL API key (OpenWeather key not used in this version)
- Run solar_dashboard or solar_dashboard2 and follow output instructions.

It is quite slow. One reason is that the NREL database only allows you to grab one year at a time.

Data sources:
https://simplemaps.com/data/us-zips
https://developer.nrel.gov/docs/solar/nsrdb/nsrdb-GOES-aggregated-v4-0-0-download/
