from django.core.management.base import BaseCommand
import os
import json
import requests

from taxi.models import City, District, Street, Address


ADDRESSES_API_URL = f'https://apidata.mos.ru/v1/datasets/60562/rows?api_key={os.getenv("ADDRESSES_API_TOKEN")}'

def create_address_from_api_record(record: dict) -> (City, District, Street, Address):
    # function for parse https://data.mos.ru/opendata/60562 api
    city, _ = City.objects.get_or_create(name=record['Cells']['P1'])
    district, _ = District.objects.get_or_create(name=record['Cells']['P5'], city=city)
    street, _ = Street.objects.get_or_create(name=record['Cells']['P7'], district=district)
    address, _ = Address.objects.get_or_create(name=record['Cells']['L1_VALUE'], street=street)

    return (city, district, street, address)




class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self._parse_addresses()

    def _parse_addresses(self, url: str=ADDRESSES_API_URL, parse_function=create_address_from_api_record):
        response = requests.get(url)
        data = json.loads(response.content)

        for record in data:
            try:
                create_address_from_api_record(record)
            except Exception as error:
                print(error)                
