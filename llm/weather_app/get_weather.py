import os
from dotenv import load_dotenv
import requests

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


# Use the requests library to get the weather for a given location
def get_weather(location):
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}"

    response = requests.get(url)
    data = response.json()

    return data
