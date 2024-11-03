import responses

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from shipments.models import Shipment, Article, ArticleShipmentItem

class ShipmentViewSetTestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.super_user = User.objects.create_superuser('admin', 'random_pass')
        self.normal_user = User.objects.create_user('user', 'random_pass')

        self.shipment = Shipment.objects.create(
            tracking_number="TN12345678",
            carrier="DHL",
            sender_address="Street 1, 10115 Berlin, Germany",
            receiver_address="Street 10, 75001 Paris, France",
            status="IN_TRANSIT"
        )
        self.article = Article.objects.create(name="Laptop", price=1200.00, sku="LP123")
        self.shipment.articles.add(self.article)


    def test_list_shipments_by_no_auth(self):
        response = self.client.get(reverse('shipment-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_list_shipments_by_normal_user(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(reverse('shipment-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_list_shipments_by_super_user_auth(self):
        self.client.force_authenticate(user=self.super_user)
        response = self.client.get(reverse('shipment-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_get_shipment(self):
        response = self.client.get(f'/v1/shipments/{self.shipment.carrier}/{self.shipment.tracking_number}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tracking_number'], self.shipment.tracking_number)


    def test_filter_shipments_by_status(self):
        self.client.force_authenticate(user=self.super_user)
        response = self.client.get(reverse('shipment-list'), {'status': 'IN_TRANSIT'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'IN_TRANSIT')


    def test_get_shipment_by_tracking_number_and_carrier(self):
        url = reverse('shipment-get_shipment', args=[self.shipment.carrier, self.shipment.tracking_number])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tracking_number'], self.shipment.tracking_number)
        self.assertEqual(response.data['carrier'], self.shipment.carrier)


    def test_get_shipment_not_found(self):
        url = reverse('shipment-get_shipment', args=["InvalidCarrier", "InvalidTrackingNumber"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_create_shipment(self):
        self.client.force_authenticate(user=self.super_user)
        data = {
            'tracking_number': ' TN12345679',
            'carrier': 'DHL',
            'sender_address': 'Street 1, 10115 Berlin, Germany',
            'receiver_address': 'Street 10, 75001 Paris, France',
            'status': 'IN_TRANSIT'
        }
        response = self.client.post(reverse('shipment-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Shipment.objects.count(), 2)

    def test_create_shipment_with_invalid_address(self):
        self.client.force_authenticate(user=self.super_user)
        data = {
            'tracking_number': ' TN12345679',
            'carrier': 'DHL',
            'sender_address': 'Street 1 10115 Berlin Germany',
            'receiver_address': 'Street 10, 75001 Paris, France',
            'status': 'IN_TRANSIT'
        }
        response = self.client.post(reverse('shipment-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Shipment.objects.count(), 1)
        self.assertIn('sender_address', response.data)
        self.assertNotIn('receiver_address', response.data)
