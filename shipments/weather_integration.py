import logging
from typing import Optional

import requests
from django.conf import settings
from django.core.cache import cache


logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60*60*2

def get_client():
    """
    Entry Point: Get the weather integration client based on the configuration.
    """
    if getattr(settings, 'WEATHER_API_KEY', None):
        return WeatherAPIClient()
    else:
        return DummyWeatherClient()


class AbstractWeatherClient:
    BASE_URL: str = ''
    SETTINGS_API_KEY: str = ''


    def make_request(self, location: str) -> Optional[dict]:
        raise NotImplementedError("Subclasses must implement this method")

    def get_weather(self, location: str) -> Optional[dict]:
        """
        Get weather data for a location. If cached data is available and not older than 2 hours, return it.
        Otherwise, fetch the data from the weather API and cache it and return the new data.
        
        Args:
            location (str): Location in Shipment. format.

        Returns:
            Optional[dict]: Weather data if available, otherwise None.
        """
        weather_cache = self.get_weather_cache(location)
        if weather_cache:
            return weather_cache
        
        weather_data = None
        try:
            weather_data = self.make_request(location)
        except requests.RequestException as exc:
            logger.error(f"Failed to fetch weather data for {location}: {exc}")
            weather_data = None
        
        if weather_data:
            self.set_weather_cache(location, weather_data)

        return weather_data

    def get_weather_cache(self, location: str) -> Optional[dict]:
        """ Get the weather cache for a location """
        return cache.get(location)
    
    def set_weather_cache(self, location: str, weather_data: dict):
        """ Set the weather cache for a location """
        cache.set(location, weather_data, timeout=DEFAULT_TIMEOUT)


class WeatherAPIClient(AbstractWeatherClient):
    BASE_URL = "https://api.weatherapi.com/v1/current.json"
    SETTINGS_API_KEY = 'WEATHER_API_KEY'

    def make_request(self, location: str) -> Optional[dict]:
        key = getattr(settings, self.SETTINGS_API_KEY, '')
        response = requests.get(f"{self.BASE_URL}?key={settings.WEATHER_API_KEY}&q={location}")
        response.raise_for_status()

        if response.status_code == 200:
            weather_data = response.json()
            return weather_data
        
        return None


class DummyWeatherClient(AbstractWeatherClient):
    """ A dummy weather client that always returns the same weather data. """

    def make_request(self, location: str) -> dict:
        return {
            "temperature": 25,
            "condition": "Sunny and Dummy (Set the API key to get real weather data :)"
        }

    def set_weather_cache(self, location: str, weather_data: dict):
        """ No need to cache dummy data """
