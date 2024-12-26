from rest_framework import status
from django.test import Client

from taxi.models import Address, City, Street, District


CITY_BASE_NAME = 'Москва'
DISTRICT_BASE_NAME = 'Останкинский'
STREET_BASE_NAME = 'Павла Корчагина'


def create_cities() -> list[City]:
    city = City.objects.create(name=CITY_BASE_NAME)

    return [city]

def create_districts(cities: list[City] = []) -> list[District]:
    if not cities:
        cities = create_cities()
    districts = [
        District.objects.create(name=DISTRICT_BASE_NAME + str(i), city=city) for i in range(10) for city in cities
    ]

    return districts

def create_streets(districts: list[District] = []) -> list[Street]:
    if not districts:
        districts = create_districts()
    streets = [
        Street.objects.create(name=STREET_BASE_NAME + str(i), district=district) for i in range(10) for district in districts 
    ]

    return streets

def create_addresses(streets: list[Street] = []) -> list[Address]:
    if not streets:
        streets = create_streets()
    streets = [
        Address.objects.create(name=str(i), street=street) for i in range(10) for street in streets
    ]

    return streets

def test_fork_addresses(db):
    _ = create_addresses()
    c = Client()

    response = c.get('/api/addresses/')
    data = response.json()
    address = Address.objects.last()

    assert response.status_code == status.HTTP_200_OK 
    data = data.pop('results')[0]
    data.pop('street')
    data.pop('id')
    assert data == {
        'name': '0',
        'full_address': 'Москва Останкинский0 Павла Корчагина0 0',
    }
