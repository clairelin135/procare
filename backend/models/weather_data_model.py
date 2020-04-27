import requests
from pprint import pprint

def get_temperature(zip_code):
    API_key = "Your API key"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    Final_url = base_url + "appid=" + API_key + "&zip=" + zip_code

    weather_data = requests.get(Final_url).json()
    pprint(weather_data)