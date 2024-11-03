
import responses
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APITestCase

from shipments.weather_integration import get_client
from shipments.models import Shipment, Article, ArticleShipmentItem

class WeatherIntegrationTestCase(TestCase):
    """
    Test cases for the weather integration module.
    This is Unit test, not Integration Test
    """
    location = '10115 Berlin'
    dummy_key = 'test_test_test'
    url = f'https://api.weatherapi.com/v1/current.json?key={dummy_key}&q={location}'

    def setUp(self):
        cache.clear()


    def test_dummy_weather_client(self):
        client = get_client()
        self.assertEquals(client.__class__.__name__, 'DummyWeatherClient')

        data = client.get_weather(self.location)
        self.assertIn('Dummy', data['condition'])
        self.assertIsNone(cache.get(self.location))
        

    @override_settings(WEATHER_API_KEY=dummy_key)
    @responses.activate
    def test_weather_api_client(self):
        client = get_client()
        self.assertEquals(client.__class__.__name__, 'WeatherAPIClient')


    @override_settings(WEATHER_API_KEY=dummy_key)
    @responses.activate
    def test_client_with_same_duplicate_location(self):
        client = get_client()
        response = responses.get(self.url, json={'weather': 'good!'}, status=200)

        data = client.get_weather(self.location)
        self.assertEquals(data, {'weather': 'good!'})
        self.assertEquals(cache.get(self.location), {'weather': 'good!'})
        self.assertEquals(len(responses.calls), 1)

        same_data = client.get_weather(self.location)
        self.assertEquals(cache.get(self.location), {'weather': 'good!'})
        self.assertEquals(len(responses.calls), 1)



    @override_settings(WEATHER_API_KEY=dummy_key)
    @responses.activate
    def test_client_with_different_location(self):
        different_location = '70173 Stuttgart'
        client = get_client()
        response = responses.get(self.url, json={'weather': 'good!'}, status=200)
        response_2 = responses.get(
            f'https://api.weatherapi.com/v1/current.json?key={self.dummy_key}&q={different_location}',
            json={'weather': 'awesome!'},
            status=200
        )
        data = client.get_weather(self.location)
        self.assertEquals(data, {'weather': 'good!'})
        self.assertEquals(cache.get(self.location), {'weather': 'good!'})
        self.assertEquals(response.call_count, 1)

        different_data = client.get_weather(different_location)
        self.assertEquals(cache.get(different_location), {'weather': 'awesome!'})
        self.assertEquals(response_2.call_count, 1)
        # All calls
        self.assertEquals(len(responses.calls), 2)
        different_data_again = client.get_weather(different_location)
        self.assertEquals(len(responses.calls), 2)


    @override_settings(WEATHER_API_KEY=dummy_key)
    @responses.activate
    def test_client_error(self):
        client = get_client()
        response = responses.get(self.url, json={'error': 'bad!'}, status=400)

        data = client.get_weather(self.location)
        self.assertIsNone(data)
        self.assertIsNone(cache.get(self.location))
        self.assertTrue(response.call_count, 1)

        try_again_data = client.get_weather(self.location)
        self.assertEquals(response.call_count, 2)


    @override_settings(WEATHER_API_KEY=dummy_key)
    @responses.activate
    def test_client_with_cache(self):
        client = get_client()
        response = responses.get(self.url, json={'weather': 'good!'}, status=200)
        weather_cache = cache.set(self.location, {'weather': 'rainy!'})
        
        self.assertEquals(response.call_count, 0)
        data = client.get_weather(self.location)
        self.assertEquals(data, {'weather': 'rainy!'})
        self.assertEquals(cache.get(self.location), {'weather': 'rainy!'})
        self.assertEquals(response.call_count, 0)


    @override_settings(WEATHER_API_KEY=dummy_key)
    @responses.activate
    def test_client_with_stale_cache(self):
        client = get_client()
        response = responses.get(self.url, json={'weather': 'good!'}, status=200)
        weather_cache = cache.set(self.location, {'weather': 'rainy!'})
        cache.clear()

        self.assertEquals(response.call_count, 0)
        data = client.get_weather(self.location)
        self.assertEquals(data, {'weather': 'good!'})
        self.assertEquals(cache.get(self.location), {'weather': 'good!'})
        self.assertEquals(response.call_count, 1)
