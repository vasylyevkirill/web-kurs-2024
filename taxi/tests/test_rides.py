from rest_framework import status
from django.test import Client, TestCase
from django.contrib.auth import get_user_model

from taxi.models import Ride, RideAddressesQueue, Address, Consumer, Driver
from taxi.serializers import RideAddressesQueueSerializer, RideCreateSerializer, InlineRideAddressesQueueSerializer
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
    ), consumer, driver


class RideTestCase(TestCase):
    def test_create_address_queue_serializer(self):
        _ = create_addresses()
        address = Address.objects.first()
        ride = create_ride()[0]

        serializer = RideAddressesQueueSerializer(data={'address': address.id, 'ride': ride.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = serializer.data
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

        serializer = RideCreateSerializer(data={
            'consumer': consumer,
            'addresses': [
                {'address': address1.id},
                {'address': address2.id},
            ]
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = dict(serializer.data)

    def test_add_ride_address_method(self):
        _ = create_addresses()
        address1, address2, address3 = list(Address.objects.all())[:3]
        user = User.objects.create(username='consumer_user', email='consumer_user@taxi.ru')
        consumer = Consumer.objects.create(user=user)

        ride = Ride.objects.create(consumer=consumer)
        [
            RideAddressesQueue.objects.create(address=address, ride=ride) for address in [address1, address2]
        ]

        c = Client()
        c.force_login(user)

        response = c.post(
            f'/api/rides/{ride.id}/add_address/',
            {
                'address': address3.id
            },
            content_type='application/json',
        )

        data = response.json()
         
        assert response.status_code == status.HTTP_201_CREATED
        assert data.pop('date_created') != None
        assert data == {
            'address': address3.id,
            'ride': ride.id,
            'order': 2,
            'name': '2',
            'full_address': 'Москва Останкинский0 Павла Корчагина0 2',
            'date_ended': None,
        }

    def test_complete_address(self):
        _ = create_addresses()
        ride, consumer, driver = create_ride()
        address1, address2 = list(Address.objects.all())[:2]

        [
            RideAddressesQueue.objects.create(address=address, ride=ride) for address in [address1, address2]
        ]

        c = Client()
        c.force_login(driver.user)

        response = c.post(
            f'/api/rides/{ride.id}/complete_address/',
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
         
        assert data['addresses'][0].get('date_ended') is not None
        assert data['addresses'][1].get('date_ended') is None
        assert data.pop('date_created') != None
        assert data.pop('id') != None
        data['addresses'] = [
            {'name': address.get('name'), 'full_address': address.get('full_address')}
            for address in data['addresses']
        ]
        assert data == {
            'consumer': {
                'first_name': '',
                'last_name': '',
                'location': None,
                'average_rating': '0.00',
                'profile_image_url': None
            },
            'driver': {
                'first_name': '',
                'last_name': '',
                'location': None,
                'average_rating': '0.00',
                'profile_image_url': None
            },
            'addresses': [{
                'name': '0',
                'full_address': 'Москва Останкинский0 Павла Корчагина0 0',
            },
            {
                'name': '1',
                'full_address': 'Москва Останкинский0 Павла Корчагина0 1',
            }],
            'status': 'In progress',
            'date_ended': None,
            'price': 1337,
        }


    def test_accept_ride_method(self):
        _ = create_addresses()
        address1, address2, address3 = list(Address.objects.all())[:3]
        consumer_user = User.objects.create(username='consumer_user', email='consumer_user@taxi.ru')
        driver_user = User.objects.create(username='driver_user', email='driver_user@taxi.ru')
        consumer = Consumer.objects.create(user=consumer_user)
        driver = Driver.objects.create(user=driver_user)

        ride = Ride.objects.create(consumer=consumer)
        [
            RideAddressesQueue.objects.create(address=address, ride=ride) for address in [address1, address2]
        ]

        c = Client()
        c.force_login(driver_user)

        response = c.post(
            f'/api/rides/{ride.id}/accept/',
            content_type='application/json',
        )

        data = response.json()
         
        assert response.status_code == status.HTTP_200_OK
        assert data.pop('date_created') != None
        assert data.pop('id') != None
        data['addresses'] = [
            {'name': address.get('name'), 'full_address': address.get('full_address')}
            for address in data['addresses']
        ]
        assert data == {
            'consumer': {
                'first_name': '',
                'last_name': '',
                'location': None,
                'average_rating': '0.00',
                'profile_image_url': None
            },
            'driver': {
                'first_name': '',
                'last_name': '',
                'location': None,
                'average_rating': '0.00',
                'profile_image_url': None
            },
            'addresses': [{
                'name': '0',
                'full_address': 'Москва Останкинский0 Павла Корчагина0 0',
            },
            {
                'name': '1',
                'full_address': 'Москва Останкинский0 Павла Корчагина0 1',
            }],
            'status': 'Wating driver',
            'date_ended': None,
            'price': 1337,
        }

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
        assert data.pop('id') != None
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
