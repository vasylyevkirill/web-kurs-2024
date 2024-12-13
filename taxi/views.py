from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from taxi.models import (
    Car, City, District, Street, Address, Driver,
    Consumer, Ride, DriverRate, ConsumerRate, RideAddressesQueue
)
from taxi.serializers import (
    CitySerializer,
    CityPreviewSerializer,
    DistrictSerializer,
    DistrictPreviewSerializer,
    StreetSerializer,
    StreetPreviewSerializer,
    AddressSerializer,
    CarSerializer,
    DriverSerializer,
)


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name'] 


    def get_serializer_class(self, *args, **kwargs):
        if self.action in 'list '.split():
            return CityPreviewSerializer
        return self.serializer_class


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'full_address']


    def get_serializer_class(self, *args, **kwargs):
        if self.action in 'list '.split():
            return DistrictPreviewSerializer
        return self.serializer_class


class StreetViewSet(viewsets.ModelViewSet):
    queryset = Street.objects.all()
    serializer_class = StreetSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'full_address']

    def get_serializer_class(self, *args, **kwargs):
        if self.action in 'list '.split():
            return StreetPreviewSerializer
        return self.serializer_class


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'full_address']


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    pagination_class = LargeResultsSetPagination


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        if self.action in 'list '.split():
            return Driver.objects.available()
        return self.queryset

    
    @action(methods=['GET'], detail=False)
    def available(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
