# weather_controller.py
import os
import requests
from logger import log_info, log_error

class WeatherController:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city: str) -> str:
        if not self.api_key:
            return "OpenWeatherMap API key is not configured."
        if not city:
            return "Please specify a city."

        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric" # Use metric units (Celsius)
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status() # Raise an error for bad status codes
            data = response.json()

            description = data['weather'][0]['description']
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']

            return (f"The weather in {city} is currently {description} with a "
                    f"temperature of {temp}°C, which feels like {feels_like}°C. "
                    f"The humidity is at {humidity}%.")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return f"Sorry, I couldn't find the city '{city}'."
            return f"Sorry, there was an error with the weather service: {e}"
        except Exception as e:
            log_error(f"Weather fetch error: {e}")
            return "Sorry, I was unable to fetch the weather data."