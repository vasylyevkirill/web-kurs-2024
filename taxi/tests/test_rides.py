from rest_framework import status
from django.test import Client, TestCase
from django.contrib.auth import get_user_model

from taxi.models import Ride, RideAddressesQueue, Address, Consumer, Driver
from taxi.serializers import RideAddressesQueueSerializer, RideSerializer
from .test_addresses import create_addresses


User = get_user_model()


def create_ride():
    consumer_user = User.objects.create(username='consumer_user', email='consumer_user@taxi.ru')
    driver_user = User.objects.create(username='driver_user', email='driver_user@taxi.ru')
    consumer = Consumer.objects.create(user=consumer_user)
    driver = Driver.objects.create(user=driver_user)

    return Ride.objects.create(
        consumer=consumer,
        driver=driver,
    )


class RideTestCase(TestCase):
    def test_create_address_queue_serializer(self):
        _ = create_addresses()
        address = Address.objects.first()
        ride = create_ride()

        serializer = RideAddressesQueueSerializer(data={'address': address.id, 'ride': ride.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = dict(serializer.data)
        assert data.pop('date_created') is not None
        assert data.pop('ride') is not None
        assert data.pop('address') is not None
        assert data == {
            'order': 0,
            'name': '0',
            'full_address': 'Москва Останкинский0 Павла Корчагина0 0',
            'date_ended': None,
        }

        
    def test_save_ride_serializer(self):
        _ = create_addresses()
        address1, address2 = list(Address.objects.all())[:2]
        user = User.objects.create(username='consumer_user', email='consumer_user@taxi.ru')
        consumer = Consumer.objects.create(user=user)

        serializer = RideSerializer(data={
            'consumer': consumer,
            'addresses': [
                {'address': address1.id},
                {'address': address2.id},
            ]
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = dict(serializer.data)

    def test_create_ride_api_request(self):
        _ = create_addresses()
        address1, address2 = list(Address.objects.all())[:2]
        user = User.objects.create(username='consumer_user', email='consumer_user@taxi.ru')
        consumer = Consumer.objects.create(user=user)

        c = Client()
        c.force_login(user)

        response = c.post(
            '/api/rides/',
            {
                'addresses': [
                    {'address': address1.id},
                    {'address': address2.id},
                ]
            },
            content_type='application/json',
        )
        data = response.json()
         
        assert response.status_code == status.HTTP_201_CREATED
        data['addresses'] = [
            {'name': address.get('name'), 'full_address': address.get('full_address')}
            for address in data['addresses']
        ]
        assert data.pop('date_created') != None
        assert data == {
            'consumer': user.id,
            'addresses': [{
                'name': '0',
                'full_address': 'Москва Останкинский0 Павла Корчагина0 0',
            },
            {
                'name': '1',
                'full_address': 'Москва Останкинский0 Павла Корчагина0 1',
            }],
            'driver': None,
            'status': 'Searching driver',
            'date_ended': None,
            'price': 1337,
        }
